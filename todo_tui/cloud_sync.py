"""Cloud sync client for syncing data with the Tuido cloud service."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

import httpx

from .models import Note, Project, Snippet, Task
from .storage import StorageManager


class CloudSyncClient:
    """Client for syncing local data with Tuido cloud service."""

    def __init__(self, api_url: str, api_token: str):
        """Initialize cloud sync client.

        Args:
            api_url: Base URL for the cloud API (e.g., https://tuido.vercel.app/api)
            api_token: API token for authentication
        """
        self.api_url = api_url.rstrip("/")
        self.api_token = api_token
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

        Args:
            storage: StorageManager instance

        Returns:
            Tuple of (success, message)
        """
        try:
            # Gather local data
            data = self._get_local_data(storage)

            # Upload to cloud
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/sync/upload",
                    headers=self.headers,
                    json=data,
                )

                if response.status_code == 200:
                    response_data = response.json()
                    # API wraps data in { success, data, message } envelope
                    result_data = response_data.get("data", {})
                    timestamp = result_data.get("timestamp", data["timestamp"])
                    return True, f"Synced to cloud at {timestamp}"
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

                    self._save_local_data(storage, cloud_data)
                    timestamp = cloud_data.get("timestamp", "unknown")
                    return True, f"Downloaded data from {timestamp}"
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
