"""Task list widget."""

from __future__ import annotations

from typing import List, Optional

from textual.app import ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.widgets import Label, ListItem, ListView, Static

from ..models import Task


class TaskSelected(Message):
    """Message sent when a task is selected."""

    def __init__(self, task: Optional[Task]):
        super().__init__()
        self.task = task


class TaskListPanel(Container):
    """Panel displaying the list of tasks."""

    DEFAULT_CSS = """
    TaskListPanel {
        width: auto;
    }
    """

    def __init__(self, id: str = "task-list-panel"):
        super().__init__(id=id)
        self.tasks: List[Task] = []
        self.selected_task: Optional[Task] = None

    def compose(self) -> ComposeResult:
        """Compose the task list panel."""
        yield Label("✓ Tasks", classes="header")
        yield ListView(id="task-list")

    def set_tasks(self, tasks: List[Task]) -> None:
        """Set the list of tasks."""
        self.tasks = tasks
        self._update_list()

    def _update_list(self) -> None:
        """Update the task list display."""
        list_view = self.query_one("#task-list", ListView)
        list_view.clear()

        if not self.tasks:
            list_view.append(
                ListItem(
                    Static("No tasks yet. Press Ctrl+N to add one!", classes="muted")
                )
            )
            return

        # Add tasks
        for task in self.tasks:
            checkbox = "☑" if task.completed else "☐"
            title_class = "task-title completed" if task.completed else "task-title"

            # Show subtask progress if any
            subtask_info = ""
            if task.subtasks:
                completed_subtasks = sum(1 for s in task.subtasks if s.completed)
                subtask_info = f" ({completed_subtasks}/{len(task.subtasks)})"

            list_view.append(
                ListItem(
                    Static(
                        f"{checkbox} {task.title}{subtask_info}", classes=title_class
                    ),
                    id=f"task-{task.id}",
                    classes="completed" if task.completed else "",
                )
            )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle task selection."""
        item_id = event.item.id

        if item_id and item_id.startswith("task-"):
            task_id = item_id.replace("task-", "")
            # Find the task
            for task in self.tasks:
                if task.id == task_id:
                    self.selected_task = task
                    self.post_message(TaskSelected(task))
                    return

        # No valid task selected
        self.selected_task = None
        self.post_message(TaskSelected(None))

    def add_task(self, task: Task) -> None:
        """Add a new task to the list."""
        self.tasks.append(task)
        self._update_list()

    def update_task(self, task: Task) -> None:
        """Update an existing task in the list."""
        for i, t in enumerate(self.tasks):
            if t.id == task.id:
                self.tasks[i] = task
                break
        self._update_list()

    def remove_task(self, task_id: str) -> None:
        """Remove a task from the list."""
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self._update_list()

        # If removed task was selected, clear selection
        if self.selected_task and self.selected_task.id == task_id:
            self.selected_task = None
            self.post_message(TaskSelected(None))

    def refresh_display(self) -> None:
        """Refresh the task list display."""
        self._update_list()
