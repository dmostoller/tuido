"""Data models for the todo application."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4


@dataclass
class Subtask:
    """A subtask within a task."""

    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    completed: bool = False


@dataclass
class Task:
    """A todo task."""

    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    notes: str = ""
    completed: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    subtasks: List[Subtask] = field(default_factory=list)
    project_id: str = ""

    def toggle_complete(self) -> None:
        """Toggle task completion status."""
        self.completed = not self.completed
        if self.completed:
            self.completed_at = datetime.now().isoformat()
        else:
            self.completed_at = None

    def is_all_subtasks_complete(self) -> bool:
        """Check if all subtasks are completed."""
        if not self.subtasks:
            return False
        return all(subtask.completed for subtask in self.subtasks)

    def add_subtask(self, title: str) -> Subtask:
        """Add a new subtask."""
        subtask = Subtask(title=title)
        self.subtasks.append(subtask)
        return subtask

    def remove_subtask(self, subtask_id: str) -> bool:
        """Remove a subtask by ID."""
        original_len = len(self.subtasks)
        self.subtasks = [s for s in self.subtasks if s.id != subtask_id]
        return len(self.subtasks) < original_len

    def toggle_subtask(self, subtask_id: str) -> None:
        """Toggle subtask completion status."""
        for subtask in self.subtasks:
            if subtask.id == subtask_id:
                subtask.completed = not subtask.completed
                break

        # Auto-complete parent if all subtasks are done
        if self.subtasks and self.is_all_subtasks_complete() and not self.completed:
            self.toggle_complete()

    def to_dict(self) -> dict:
        """Convert task to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "notes": self.notes,
            "completed": self.completed,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "subtasks": [
                {"id": s.id, "title": s.title, "completed": s.completed}
                for s in self.subtasks
            ],
            "project_id": self.project_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create task from dictionary."""
        subtasks = [
            Subtask(id=s["id"], title=s["title"], completed=s["completed"])
            for s in data.get("subtasks", [])
        ]
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            notes=data.get("notes", ""),
            completed=data["completed"],
            created_at=data["created_at"],
            completed_at=data.get("completed_at"),
            subtasks=subtasks,
            project_id=data.get("project_id", ""),
        )


@dataclass
class Project:
    """A project that contains tasks."""

    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert project to dictionary for JSON serialization."""
        return {"id": self.id, "name": self.name, "created_at": self.created_at}

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        """Create project from dictionary."""
        return cls(id=data["id"], name=data["name"], created_at=data["created_at"])
