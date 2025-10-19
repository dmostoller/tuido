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
    priority: str = "none"  # Options: "high", "medium", "low", "none"

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
            "priority": self.priority,
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
            priority=data.get("priority", "none"),
        )

    def get_priority_display(self) -> tuple[str, str]:
        """Get priority icon and color for display.

        Returns:
            tuple: (icon, color_class) for the priority level
        """
        from .icons import Icons

        priority_map = {
            "high": (f"[#f38ba8]{Icons.BOOKMARK}[/]", "error"),
            "medium": (f"[#f9e2af]{Icons.BOOKMARK}[/]", "warning"),
            "low": (f"[#89b4fa]{Icons.BOOKMARK}[/]", "success"),
            "none": ("", ""),
        }
        return priority_map.get(self.priority, ("", ""))


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


@dataclass
class Note:
    """A markdown note in the scratchpad."""

    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = "Untitled Note"
    content: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert note to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        """Create note from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            content=data.get("content", ""),
            created_at=data["created_at"],
            updated_at=data.get("updated_at", data["created_at"]),
        )


@dataclass
class Settings:
    """Application settings.

    Attributes:
        theme: The default theme to use on startup (e.g., 'catppuccin-mocha')
        show_completed_tasks: Whether to show completed tasks in the task list (True) or hide them (False)
        pomodoro_work_minutes: Duration of work sessions in minutes (default: 25)
        pomodoro_short_break_minutes: Duration of short breaks in minutes (default: 5)
        pomodoro_long_break_minutes: Duration of long breaks in minutes (default: 15)
        weather_location: Location for weather widget (e.g., 'San Francisco' or 'London,UK')
        weather_use_fahrenheit: Whether to use Fahrenheit (True) or Celsius (False) for temperature
    """

    theme: str = "catppuccin-mocha"  # Default startup theme
    show_completed_tasks: bool = True
    pomodoro_work_minutes: int = 25
    pomodoro_short_break_minutes: int = 5
    pomodoro_long_break_minutes: int = 15
    weather_location: str = ""  # Empty means not configured
    weather_use_fahrenheit: bool = True  # Default to Fahrenheit

    def to_dict(self) -> dict:
        """Convert settings to dictionary for JSON serialization."""
        return {
            "theme": self.theme,
            "show_completed_tasks": self.show_completed_tasks,
            "pomodoro_work_minutes": self.pomodoro_work_minutes,
            "pomodoro_short_break_minutes": self.pomodoro_short_break_minutes,
            "pomodoro_long_break_minutes": self.pomodoro_long_break_minutes,
            "weather_location": self.weather_location,
            "weather_use_fahrenheit": self.weather_use_fahrenheit,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Settings":
        """Create settings from dictionary."""
        return cls(
            theme=data.get("theme", "catppuccin-mocha"),
            show_completed_tasks=data.get("show_completed_tasks", True),
            pomodoro_work_minutes=data.get("pomodoro_work_minutes", 25),
            pomodoro_short_break_minutes=data.get("pomodoro_short_break_minutes", 5),
            pomodoro_long_break_minutes=data.get("pomodoro_long_break_minutes", 15),
            weather_location=data.get("weather_location", ""),
            weather_use_fahrenheit=data.get("weather_use_fahrenheit", True),
        )
