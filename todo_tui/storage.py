"""JSON-based storage manager for tasks and projects."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union

from .models import Project, Settings, Task


class StorageManager:
    """Manages JSON file storage for projects and tasks."""

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize storage manager with data directory."""
        if data_dir is None:
            # Use XDG standard location for user data
            data_dir = Path.home() / ".local" / "share" / "tuido"
        self.data_dir = Path(data_dir)
        self.projects_file = self.data_dir / "projects.json"
        self.settings_file = self.data_dir / "settings.json"
        self._ensure_data_dir()
        self._migrate_old_data_if_needed()

    def _ensure_data_dir(self) -> None:
        """Create data directory if it doesn't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize projects file if it doesn't exist
        if not self.projects_file.exists():
            self._save_json(self.projects_file, [])

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

    # Settings operations
    def load_settings(self) -> Settings:
        """Load application settings."""
        if not self.settings_file.exists():
            # Return defaults if no settings file
            return Settings()

        data = self._load_json(self.settings_file)
        return Settings.from_dict(data)

    def save_settings(self, settings: Settings) -> None:
        """Save application settings."""
        self._save_json(self.settings_file, settings.to_dict())
