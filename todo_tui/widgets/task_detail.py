"""Task detail panel widget."""

from __future__ import annotations

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Label, ListItem, ListView, Static

from ..models import Task


class TaskDetailPanel(Container):
    """Panel displaying detailed information about a selected task."""

    DEFAULT_CSS = """
    TaskDetailPanel {
        width: auto;
    }
    """

    def __init__(self, id: str = "task-detail-panel"):
        super().__init__(id=id)
        self.current_task: Optional[Task] = None

    def compose(self) -> ComposeResult:
        """Compose the task detail panel."""
        yield Label("📝 Task Details", classes="header")
        with Vertical(id="task-detail-content"):
            yield Static(
                "Select a task to view details",
                id="task-detail-placeholder",
                classes="muted",
            )

    def show_task(self, task: Optional[Task]) -> None:
        """Display task details."""
        self.current_task = task
        content = self.query_one("#task-detail-content", Vertical)
        content.remove_children()

        if not task:
            content.mount(
                Static(
                    "Select a task to view details",
                    classes="muted",
                )
            )
            return

        # Task title
        title_text = f"{'☑' if task.completed else '☐'} {task.title}"
        title_class = "title completed" if task.completed else "title"
        content.mount(Label(title_text, classes=title_class))

        # Description
        if task.description:
            content.mount(Label("Description:", classes="detail-label"))
            content.mount(Static(task.description, classes="detail-value"))

        # Notes
        if task.notes:
            content.mount(Label("Notes:", classes="detail-label"))
            content.mount(Static(task.notes, classes="detail-value"))

        # Subtasks
        if task.subtasks:
            content.mount(
                Label(
                    f"Subtasks ({sum(1 for s in task.subtasks if s.completed)}/{len(task.subtasks)}):",
                    classes="detail-label",
                )
            )
            subtask_list = ListView(id="subtask-list")
            for subtask in task.subtasks:
                checkbox = "☑" if subtask.completed else "☐"
                item_class = "completed" if subtask.completed else ""
                subtask_list.append(
                    ListItem(
                        Static(
                            f"{checkbox} {subtask.title}",
                            classes=f"subtask-item {item_class}",
                        ),
                        id=f"subtask-{subtask.id}",
                    )
                )
            content.mount(subtask_list)

        # Action buttons
        button_container = Horizontal()
        button_container.mount(Button("Edit", id="btn-edit-task", variant="primary"))
        button_container.mount(
            Button("Toggle Complete", id="btn-toggle-task", variant="success")
        )
        button_container.mount(Button("Delete", id="btn-delete-task", variant="error"))
        content.mount(button_container)

    def clear(self) -> None:
        """Clear the task detail display."""
        self.show_task(None)
