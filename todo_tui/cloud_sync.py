"""Cloud sync client for syncing data with the Tuido cloud service."""

from __future__ import annotations

import asyncio
import json
import logging
import platform
from dataclasses import dataclass
from datetime import datetime
from typing import AsyncGenerator, Optional

import httpx

from cryptography.exceptions import InvalidTag

from .encryption import (
    EncryptedPayload,
    decrypt_data,
    encrypt_data,
    get_device_token,
    has_device_token,
    save_device_credentials,
)
from .models import Note, Project, Snippet, Task
from .storage import StorageManager

logger = logging.getLogger(__name__)


@dataclass
class DeviceCodeResponse:
    """Response from device authorization request."""

    device_code: str
    user_code: str
    verification_url: str
    expires_in: int
    interval: int


@dataclass
class AuthorizationResult:
    """Result of device authorization polling."""

    status: str  # "pending", "authorized", "expired", "denied"
    token: Optional[str] = None
    device_id: Optional[str] = None
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    error: Optional[str] = None


class CloudSyncClient:
    """Client for syncing local data with Tuido cloud service."""

    def __init__(
        self, api_url: str, api_token: str, encryption_password: Optional[str] = None
    ):
        """Initialize cloud sync client.

        Args:
            api_url: Base URL for the cloud API (e.g., https://tuido.dev/api)
            api_token: API token for authentication
            encryption_password: Optional password for E2E encryption
        """
        self.api_url = api_url.rstrip("/")
        self.api_token = api_token
        self.encryption_password = encryption_password
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

    def _parse_timestamp(self, timestamp: str) -> datetime:
        """Parse ISO timestamp string into datetime object.

        Handles various ISO8601 formats including 'Z' suffix for UTC.
        Python 3.11+ natively supports 'Z' suffix in fromisoformat().

        Args:
            timestamp: ISO format timestamp string

        Returns:
            Parsed datetime object
        """
        return datetime.fromisoformat(timestamp)

    def _get_local_data(self, storage: StorageManager) -> dict:
        """Gather all local data to upload.

        Args:
            storage: StorageManager instance

        Returns:
            Dictionary containing all projects, tasks, notes, and snippets
        """
        # Load all projects
        projects = storage.load_projects()

        # Load tasks for each project
        tasks_by_project = {}
        for project in projects:
            tasks = storage.load_tasks(project.id)
            tasks_by_project[project.id] = [t.to_dict() for t in tasks]

        # Load all notes
        notes = storage.load_notes()

        # Load all snippets
        snippets = storage.load_snippets()

        return {
            "timestamp": datetime.now().isoformat(),
            "projects": [p.to_dict() for p in projects],
            "tasks": tasks_by_project,
            "notes": [n.to_dict() for n in notes],
            "snippets": [s.to_dict() for s in snippets],
        }

    def _save_local_data(self, storage: StorageManager, cloud_data: dict) -> None:
        """Save cloud data to local storage.

        Args:
            storage: StorageManager instance
            cloud_data: Data downloaded from cloud

        Raises:
            ValueError: If cloud data appears invalid or empty
        """
        # Validate that cloud_data has expected structure
        if not isinstance(cloud_data, dict):
            raise ValueError("Cloud data must be a dictionary")

        projects_list = cloud_data.get("projects", [])
        tasks_dict = cloud_data.get("tasks", {})
        notes_list = cloud_data.get("notes", [])
        snippets_list = cloud_data.get("snippets", [])

        # Warning: Check if we're about to overwrite with completely empty data
        # This could indicate a parsing error or API issue
        if (
            len(projects_list) == 0
            and len(tasks_dict) == 0
            and len(notes_list) == 0
            and len(snippets_list) == 0
        ):
            # Check if local storage has data
            existing_projects = storage.load_projects()
            if len(existing_projects) > 0:
                # Log warning but still allow sync (cloud might legitimately be empty)
                import sys

                print(
                    "WARNING: Overwriting local data with empty cloud data",
                    file=sys.stderr,
                )

        # Save projects
        projects = [Project.from_dict(p) for p in projects_list]
        storage.save_projects(projects)

        # Save tasks for each project
        for project_id, task_list in tasks_dict.items():
            tasks = [Task.from_dict(t) for t in task_list]
            storage.save_tasks(project_id, tasks)

        # Save notes
        notes = [Note.from_dict(n) for n in notes_list]
        storage.save_notes(notes)

        # Save snippets
        snippets = [Snippet.from_dict(s) for s in snippets_list]
        storage.save_snippets(snippets)

    async def upload(self, storage: StorageManager) -> tuple[bool, str]:
        """Upload local data to cloud.

        If encryption password is set, data is encrypted before upload.

        Args:
            storage: StorageManager instance

        Returns:
            Tuple of (success, message)
        """
        try:
            # Gather local data
            data = self._get_local_data(storage)

            # Encrypt if password is set
            if self.encryption_password:
                json_data = json.dumps(data)
                encrypted = encrypt_data(json_data, self.encryption_password)
                payload = {
                    **encrypted.to_dict(),
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                # Legacy unencrypted upload
                payload = data

            # Upload to cloud
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/sync/upload",
                    headers=self.headers,
                    json=payload,
                )

                if response.status_code == 200:
                    response_data = response.json()
                    # API wraps data in { success, data, message } envelope
                    result_data = response_data.get("data", {})
                    timestamp = result_data.get("timestamp", data["timestamp"])
                    encrypted_msg = " (encrypted)" if self.encryption_password else ""
                    return True, f"Synced to cloud{encrypted_msg} at {timestamp}"
                elif response.status_code == 401:
                    return False, "Invalid API token. Please check your settings."
                elif response.status_code == 413:
                    return False, "Data size exceeds 10MB limit."
                else:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", "Unknown error")
                    except (json.JSONDecodeError, ValueError):
                        error_msg = f"HTTP {response.status_code}"
                    return False, f"Upload failed: {error_msg}"

        except httpx.TimeoutException:
            return False, "Upload timed out. Check your internet connection."
        except httpx.ConnectError:
            return (
                False,
                "Cannot connect to cloud service. Check your internet connection.",
            )
        except Exception as e:
            return False, f"Upload failed: {str(e)}"

    async def download(self, storage: StorageManager) -> tuple[bool, str]:
        """Download data from cloud and save locally.

        If data is encrypted, requires encryption password to decrypt.

        Args:
            storage: StorageManager instance

        Returns:
            Tuple of (success, message)
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.api_url}/sync/download",
                    headers=self.headers,
                )

                if response.status_code == 200:
                    response_data = response.json()
                    # API wraps data in { success, data } envelope
                    cloud_data = response_data.get("data", {})

                    if not cloud_data:
                        return False, "Download failed: No data in response"

                    # Check if data is encrypted
                    if "ciphertext" in cloud_data:
                        if not self.encryption_password:
                            return (
                                False,
                                "Data is encrypted. "
                                "Set encryption password in settings.",
                            )

                        try:
                            payload = EncryptedPayload.from_dict(cloud_data)
                            decrypted_json = decrypt_data(
                                payload, self.encryption_password
                            )
                            cloud_data = json.loads(decrypted_json)
                        except InvalidTag:
                            # Wrong password or tampered data
                            return (
                                False,
                                "Decryption failed. Check your encryption password.",
                            )
                        except ValueError as e:
                            # Empty password or invalid payload
                            return (False, f"Decryption failed: {e}")
                        except Exception:
                            # Other unexpected errors
                            return (
                                False,
                                "Decryption failed due to an unexpected error.",
                            )

                    self._save_local_data(storage, cloud_data)
                    timestamp = cloud_data.get("timestamp", "unknown")
                    encrypted_msg = (
                        " (decrypted)" if self.encryption_password else ""
                    )
                    return True, f"Downloaded data{encrypted_msg} from {timestamp}"
                elif response.status_code == 404:
                    return False, "No cloud data found. Upload data first."
                elif response.status_code == 401:
                    return False, "Invalid API token. Please check your settings."
                else:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", "Unknown error")
                    except (json.JSONDecodeError, ValueError):
                        error_msg = f"HTTP {response.status_code}"
                    return False, f"Download failed: {error_msg}"

        except httpx.TimeoutException:
            return False, "Download timed out. Check your internet connection."
        except httpx.ConnectError:
            return (
                False,
                "Cannot connect to cloud service. Check your internet connection.",
            )
        except Exception as e:
            return False, f"Download failed: {str(e)}"

    async def get_last_sync_time(self) -> tuple[bool, Optional[str]]:
        """Get timestamp of last cloud sync.

        Returns:
            Tuple of (success, timestamp_or_none)
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.api_url}/sync/check",
                    headers=self.headers,
                )

                if response.status_code == 200:
                    response_data = response.json()
                    # API wraps data in { success, data } envelope
                    data = response_data.get("data", {})
                    return True, data.get("lastSync")
                else:
                    return False, None

        except Exception:
            return False, None

    async def check_sync_status(
        self, storage: StorageManager
    ) -> dict[str, Optional[str]]:
        """Check sync status and return cloud/local timestamps.

        Args:
            storage: StorageManager instance

        Returns:
            Dictionary with:
            - cloud_timestamp: Last cloud sync time or None
            - local_timestamp: Last local sync time or None
            - has_cloud_data: Whether cloud has data
            - has_local_data: Whether local has been synced before
            - recommended_action: "upload", "download", "sync", or "prompt"
        """
        # Get cloud timestamp
        success, cloud_timestamp = await self.get_last_sync_time()
        has_cloud_data = success and cloud_timestamp is not None

        # Get local timestamp
        settings = StorageManager.load_settings()
        local_timestamp = settings.last_cloud_sync
        has_local_data = local_timestamp is not None

        # Determine recommended action
        if not has_cloud_data and not has_local_data:
            recommended_action = "upload"  # Nothing anywhere, upload local
        elif not has_cloud_data and has_local_data:
            recommended_action = "upload"  # Local has data, cloud doesn't
        elif has_cloud_data and not has_local_data:
            recommended_action = "download"  # Cloud has data, local doesn't
        else:
            # Both have data - prompt user to choose
            recommended_action = "prompt"

        return {
            "cloud_timestamp": cloud_timestamp,
            "local_timestamp": local_timestamp,
            "has_cloud_data": has_cloud_data,
            "has_local_data": has_local_data,
            "recommended_action": recommended_action,
        }

    async def sync(self, storage: StorageManager) -> tuple[bool, str]:
        """Smart sync: compare timestamps and sync newest data.

        Uses timestamp-based conflict resolution:
        - If cloud is newer: download and replace local
        - If local is newer: upload to cloud
        - If equal: no sync needed

        Args:
            storage: StorageManager instance

        Returns:
            Tuple of (success, message)
        """
        try:
            # Get cloud timestamp
            success, cloud_timestamp = await self.get_last_sync_time()
            if not success or not cloud_timestamp:
                # No cloud data yet, upload local
                return await self.upload(storage)

            # Get local timestamp from settings
            settings = StorageManager.load_settings()
            local_timestamp = settings.last_cloud_sync

            if not local_timestamp:
                # Never synced before, download cloud data
                return await self.download(storage)

            # Compare timestamps using datetime objects
            try:
                cloud_dt = self._parse_timestamp(cloud_timestamp)
                local_dt = self._parse_timestamp(local_timestamp)

                if cloud_dt > local_dt:
                    # Cloud is newer, download
                    return await self.download(storage)
                elif cloud_dt == local_dt:
                    # Already in sync
                    return True, "Already in sync with cloud"
                else:
                    # Local is newer, upload
                    return await self.upload(storage)
            except (ValueError, AttributeError) as e:
                # Fail safely if timestamp parsing fails
                return (
                    False,
                    f"Sync failed: Unable to parse timestamps ({type(e).__name__})",
                )

        except Exception as e:
            return False, f"Sync failed: {str(e)}"

    # =========================================================================
    # Device Authorization Flow
    # =========================================================================

    @staticmethod
    def get_device_name() -> str:
        """Get a friendly name for this device."""
        try:
            hostname = platform.node()
            system = platform.system()
            return f"{hostname} ({system})"
        except Exception:
            return "Unknown Device"

    @staticmethod
    def is_device_linked() -> bool:
        """Check if this device is linked to an account."""
        return has_device_token()

    @staticmethod
    def get_stored_token() -> Optional[str]:
        """Get the stored device token from keyring."""
        return get_device_token()

    async def request_device_code(
        self, device_name: Optional[str] = None
    ) -> tuple[bool, DeviceCodeResponse | str]:
        """Request a device authorization code.

        Args:
            device_name: Optional name for this device

        Returns:
            Tuple of (success, DeviceCodeResponse or error message)
        """
        if device_name is None:
            device_name = self.get_device_name()

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/auth/device",
                    json={"device_name": device_name},
                )

                if response.status_code == 200:
                    data = response.json()
                    return True, DeviceCodeResponse(
                        device_code=data["deviceCode"],
                        user_code=data["userCode"],
                        verification_url=data["verificationUrl"],
                        expires_in=data["expiresIn"],
                        interval=data["interval"],
                    )
                else:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", "Unknown error")
                    except Exception as e:
                        logger.debug("Failed to parse error response: %s: %s", type(e).__name__, e)
                        error_msg = f"HTTP {response.status_code}"
                    return False, error_msg

        except httpx.ConnectError:
            return False, "Cannot connect to server. Check your internet connection."
        except httpx.TimeoutException:
            return False, "Request timed out. Please try again."
        except Exception as e:
            return False, f"Request failed: {str(e)}"

    async def poll_for_authorization(
        self, device_code: str
    ) -> AuthorizationResult:
        """Poll for authorization status.

        Args:
            device_code: The device code from request_device_code

        Returns:
            AuthorizationResult with current status
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/auth/device/poll",
                    json={"device_code": device_code},
                )

                if response.status_code == 200:
                    data = response.json()
                    user = data.get("user", {})
                    return AuthorizationResult(
                        status=data["status"],
                        token=data.get("token"),
                        device_id=data.get("deviceId"),
                        user_email=user.get("email"),
                        user_name=user.get("name"),
                        error=data.get("error"),
                    )
                else:
                    return AuthorizationResult(
                        status="error",
                        error=f"HTTP {response.status_code}",
                    )

        except Exception as e:
            logger.warning("Authorization polling failed: %s: %s", type(e).__name__, e)
            return AuthorizationResult(
                status="error",
                error=str(e),
            )

    async def authorize_device(
        self, device_name: Optional[str] = None
    ) -> AsyncGenerator[DeviceCodeResponse | AuthorizationResult, None]:
        """Complete device authorization flow.

        This is a generator that yields:
        1. DeviceCodeResponse with the codes to display to user
        2. AuthorizationResult updates as we poll for authorization

        Usage:
            async for result in client.authorize_device():
                if isinstance(result, DeviceCodeResponse):
                    # Display the user code and verification URL
                    show_code(result.user_code, result.verification_url)
                elif result.status == "authorized":
                    # Success! Token is saved automatically
                    break
                elif result.status in ("expired", "denied", "error"):
                    # Failed
                    show_error(result.error)
                    break
                # else status == "pending", keep waiting

        Yields:
            DeviceCodeResponse first, then AuthorizationResult updates
        """
        if device_name is None:
            device_name = self.get_device_name()

        # Request device code
        success, result = await self.request_device_code(device_name)
        if not success:
            yield AuthorizationResult(status="error", error=str(result))
            return

        code_response = result
        yield code_response

        # Poll for authorization
        # Track retries for authorized-but-no-token case
        authorized_retries = 0
        max_authorized_retries = 5

        # Client-side timeout based on device code expiration
        start_time = asyncio.get_event_loop().time()

        while True:
            # Enforce client-side expiration timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= code_response.expires_in:
                yield AuthorizationResult(
                    status="expired",
                    error="Device code expired. Please try again.",
                )
                break

            await asyncio.sleep(code_response.interval)

            auth_result = await self.poll_for_authorization(code_response.device_code)

            if auth_result.status == "authorized":
                # Save credentials to keyring
                if auth_result.token and auth_result.device_id:
                    save_device_credentials(auth_result.token, auth_result.device_id)
                    yield auth_result
                    break
                else:
                    # Authorized but no token yet - keep polling briefly
                    authorized_retries += 1
                    if authorized_retries >= max_authorized_retries:
                        # Give up - token was likely already consumed
                        yield AuthorizationResult(
                            status="error",
                            error="Authorization succeeded but token was not "
                            "received. Please try again.",
                        )
                        break
                    # Don't yield yet, keep polling for token
                    continue

            yield auth_result

            if auth_result.status in ("expired", "denied", "error"):
                break
            # else status == "pending", continue polling
