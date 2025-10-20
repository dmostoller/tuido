"""JSON-based storage manager for tasks and projects."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from platformdirs import user_config_dir, user_data_dir

from .models import Note, Project, Settings, Task


class StorageManager:
    """Manages JSON file storage for projects and tasks."""

    @staticmethod
    def get_config_dir() -> Path:
        """Get the configuration directory path (platform-specific).

        Settings are stored here in a fixed location separate from user data.
        Returns: Path like ~/.config/tuido/ on Linux, ~/Library/Application Support/tuido/ on macOS
        """
        return Path(user_config_dir("tuido", appauthor=False))

    @staticmethod
    def get_default_data_dir() -> Path:
        """Get the default data directory path (platform-specific).

        Returns: Path like ~/.local/share/tuido/ on Linux, ~/Library/Application Support/tuido/ on macOS
        """
        return Path(user_data_dir("tuido", appauthor=False))

    @staticmethod
    def load_settings() -> Settings:
        """Load application settings from fixed config location.

        This is a static method because settings must be loaded before
        initializing StorageManager (to know which data directory to use).
        """
        config_dir = StorageManager.get_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)
        settings_file = config_dir / "settings.json"

        if not settings_file.exists():
            return Settings()

        with open(settings_file, "r") as f:
            data = json.load(f)
        return Settings.from_dict(data)

    @staticmethod
    def save_settings(settings: Settings) -> None:
        """Save application settings to fixed config location."""
        config_dir = StorageManager.get_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)
        settings_file = config_dir / "settings.json"

        with open(settings_file, "w") as f:
            json.dump(settings.to_dict(), f, indent=2)

    def __init__(self):
        """Initialize storage manager with default data directory."""
        self.data_dir = self.get_default_data_dir()
        self.projects_file = self.data_dir / "projects.json"
        self.scratchpad_file = self.data_dir / "scratchpad.md"
        self.notes_file = self.data_dir / "notes.json"
        self._ensure_data_dir()
        self._migrate_old_data_if_needed()
        self._migrate_scratchpad_to_notes()

    def _ensure_data_dir(self) -> None:
        """Create data directory if it doesn't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize projects file if it doesn't exist
        if not self.projects_file.exists():
            self._save_json(self.projects_file, [])

        # Initialize notes file if it doesn't exist
        if not self.notes_file.exists():
            self._save_json(self.notes_file, [])

        # Initialize scratchpad file if it doesn't exist (for backwards compatibility)
        if not self.scratchpad_file.exists():
            self.scratchpad_file.write_text(
                "# Scratchpad\n\nStart writing your notes here...\n"
            )

    def _migrate_old_data_if_needed(self) -> None:
        """Migrate data from old relative 'data/' directory to new location."""
        # Only migrate if new location is empty (just initialized)
        json_files = list(self.data_dir.glob("*.json"))
        if len(json_files) > 1:  # More than just empty projects.json
            return  # Already has data, skip migration

        # Check for old data in project directory
        # Get the project root (where the package is installed)
        package_dir = Path(__file__).parent.parent  # Go up from todo_tui/storage.py
        old_data_dir = package_dir / "data"

        if old_data_dir.exists() and old_data_dir.is_dir():
            old_files = list(old_data_dir.glob("*.json"))
            if old_files:
                print(f"📦 Migrating data from {old_data_dir} to {self.data_dir}")
                for file in old_files:
                    dest = self.data_dir / file.name
                    shutil.copy2(file, dest)
                    print(f"   ✓ Copied {file.name}")
                print(f"✅ Migration complete! Your data is now in {self.data_dir}")
                print(f"   (You can safely delete the old '{old_data_dir}' folder)")
                print()

    def _save_json(self, file_path: Path, data: Union[List, Dict]) -> None:
        """Save data to JSON file."""
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    def _load_json(self, file_path: Path) -> Union[List, Dict]:
        """Load data from JSON file."""
        if not file_path.exists():
            return []
        with open(file_path, "r") as f:
            return json.load(f)

    def get_task_file(self, project_id: str) -> Path:
        """Get the file path for a project's tasks."""
        return self.data_dir / f"{project_id}.json"

    # Project operations
    def load_projects(self) -> List[Project]:
        """Load all projects."""
        data = self._load_json(self.projects_file)
        return [Project.from_dict(p) for p in data]

    def save_projects(self, projects: List[Project]) -> None:
        """Save all projects."""
        data = [p.to_dict() for p in projects]
        self._save_json(self.projects_file, data)

    def add_project(self, project: Project) -> None:
        """Add a new project."""
        projects = self.load_projects()
        projects.append(project)
        self.save_projects(projects)

        # Create empty tasks file for the project
        self._save_json(self.get_task_file(project.id), [])

    def update_project(self, project: Project) -> None:
        """Update an existing project."""
        projects = self.load_projects()
        for i, p in enumerate(projects):
            if p.id == project.id:
                projects[i] = project
                break
        self.save_projects(projects)

    def delete_project(self, project_id: str) -> None:
        """Delete a project and its tasks."""
        projects = self.load_projects()
        projects = [p for p in projects if p.id != project_id]
        self.save_projects(projects)

        # Delete the project's task file
        task_file = self.get_task_file(project_id)
        if task_file.exists():
            task_file.unlink()

    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a specific project by ID."""
        projects = self.load_projects()
        for p in projects:
            if p.id == project_id:
                return p
        return None

    # Task operations
    def load_tasks(self, project_id: str) -> List[Task]:
        """Load all tasks for a project."""
        task_file = self.get_task_file(project_id)
        data = self._load_json(task_file)
        return [Task.from_dict(t) for t in data]

    def save_tasks(self, project_id: str, tasks: List[Task]) -> None:
        """Save all tasks for a project."""
        task_file = self.get_task_file(project_id)
        data = [t.to_dict() for t in tasks]
        self._save_json(task_file, data)

    def add_task(self, task: Task) -> None:
        """Add a new task to a project."""
        tasks = self.load_tasks(task.project_id)
        tasks.append(task)
        self.save_tasks(task.project_id, tasks)

    def update_task(self, task: Task) -> None:
        """Update an existing task."""
        tasks = self.load_tasks(task.project_id)
        for i, t in enumerate(tasks):
            if t.id == task.id:
                tasks[i] = task
                break
        self.save_tasks(task.project_id, tasks)

    def delete_task(self, project_id: str, task_id: str) -> None:
        """Delete a task from a project."""
        tasks = self.load_tasks(project_id)
        tasks = [t for t in tasks if t.id != task_id]
        self.save_tasks(project_id, tasks)

    def get_task(self, project_id: str, task_id: str) -> Optional[Task]:
        """Get a specific task by ID."""
        tasks = self.load_tasks(project_id)
        for t in tasks:
            if t.id == task_id:
                return t
        return None

    def load_all_tasks(self) -> List[Task]:
        """Load all tasks across all projects."""
        all_tasks = []
        projects = self.load_projects()
        for project in projects:
            tasks = self.load_tasks(project.id)
            all_tasks.extend(tasks)
        return all_tasks

    # Scratchpad operations (deprecated, kept for backwards compatibility)
    def load_scratchpad(self) -> str:
        """Load scratchpad content.

        Returns:
            str: The markdown content from the scratchpad file.
        """
        if not self.scratchpad_file.exists():
            return "# Scratchpad\n\nStart writing your notes here...\n"
        return self.scratchpad_file.read_text()

    def save_scratchpad(self, content: str) -> None:
        """Save scratchpad content.

        Args:
            content: The markdown content to save.
        """
        self.scratchpad_file.write_text(content)

    def _migrate_scratchpad_to_notes(self) -> None:
        """Migrate old scratchpad.md to new notes system."""
        # Check if we've already migrated (notes.json has content)
        notes = self.load_notes()
        if notes:
            return  # Already have notes, skip migration

        # Check if old scratchpad exists and has non-default content
        if self.scratchpad_file.exists():
            content = self.scratchpad_file.read_text()
            default_content = "# Scratchpad\n\nStart writing your notes here...\n"

            # Only migrate if content is different from default
            if content.strip() and content != default_content:
                # Create a note from the scratchpad content
                note = Note(
                    title="Quick Notes",
                    content=content,
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat(),
                )
                self.add_note(note)

                # Rename old scratchpad file as backup
                backup_file = self.data_dir / "scratchpad.md.backup"
                self.scratchpad_file.rename(backup_file)

        # If no notes exist after migration, create a default note
        notes = self.load_notes()
        if not notes:
            default_note = Note(
                title="Quick Notes",
                content="# Quick Notes\n\nStart writing your notes here...\n",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
            )
            self.add_note(default_note)

    # Note operations
    def load_notes(self) -> List[Note]:
        """Load all notes."""
        data = self._load_json(self.notes_file)
        return [Note.from_dict(n) for n in data]

    def save_notes(self, notes: List[Note]) -> None:
        """Save all notes."""
        data = [n.to_dict() for n in notes]
        self._save_json(self.notes_file, data)

    def add_note(self, note: Note) -> None:
        """Add a new note."""
        notes = self.load_notes()
        notes.append(note)
        self.save_notes(notes)

    def update_note(self, note: Note) -> None:
        """Update an existing note."""
        # Update the updated_at timestamp
        note.updated_at = datetime.now().isoformat()

        notes = self.load_notes()
        for i, n in enumerate(notes):
            if n.id == note.id:
                notes[i] = note
                break
        self.save_notes(notes)

    def delete_note(self, note_id: str) -> None:
        """Delete a note."""
        notes = self.load_notes()
        notes = [n for n in notes if n.id != note_id]
        self.save_notes(notes)

    def get_note(self, note_id: str) -> Optional[Note]:
        """Get a specific note by ID."""
        notes = self.load_notes()
        for n in notes:
            if n.id == note_id:
                return n
        return None
