"""Task detail panel widget."""

from __future__ import annotations

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.widgets import Button, Label, ListItem, ListView, Static

from ..icons import Icons
from ..models import Task


class SubtaskToggled(Message):
    """Message sent when a subtask is toggled."""

    def __init__(self, task: Task, subtask_id: str):
        super().__init__()
        self.task = task
        self.subtask_id = subtask_id


class TaskDetailPanel(Container):
    """Panel displaying detailed information about a selected task."""

    DEFAULT_CSS = """
    TaskDetailPanel {
        width: auto;
        height: 100%;
    }

    #task-detail-content {
        height: 100%;
        overflow-y: auto;
    }

    .detail-buttons {
        dock: bottom;
        width: 100%;
        height: auto;
        padding: 1;
        border-top: solid $primary;
    }
    """

    def __init__(self, id: str = "task-detail-panel"):
        super().__init__(id=id)
        self.current_task: Optional[Task] = None

    def compose(self) -> ComposeResult:
        """Compose the task detail panel."""
        yield Label(f"{Icons.EDIT} Task Details", classes="header")
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
        checkbox = Icons.CHECK_SQUARE if task.completed else Icons.SQUARE_O
        priority_icon, _ = task.get_priority_display()
        priority_str = f"{priority_icon} " if priority_icon else ""
        title_text = f"{priority_str}{checkbox} {task.title}"
        title_class = "title completed" if task.completed else "title"
        content.mount(Label(title_text, classes=title_class))

        # Priority (show label if not none)
        if task.priority != "none":
            priority_labels = {
                "high": "High Priority",
                "medium": "Medium Priority",
                "low": "Low Priority",
            }
            priority_display = priority_labels.get(task.priority, "")
            if priority_display:
                content.mount(Label("Priority:", classes="detail-label"))
                content.mount(
                    Static(
                        f"{priority_icon} {priority_display}", classes="detail-value"
                    )
                )

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
            subtask_list = ListView()
            content.mount(subtask_list)
            for subtask in task.subtasks:
                checkbox = Icons.CHECK_SQUARE if subtask.completed else Icons.SQUARE_O
                item_class = "completed" if subtask.completed else ""
                subtask_list.append(
                    ListItem(
                        Static(
                            f"{checkbox} {subtask.title}",
                            classes=f"subtask-item {item_class}",
                        )
                    )
                )

        # Action buttons (docked to bottom like a footer)
        button_container = Horizontal(classes="detail-buttons")
        content.mount(button_container)
        button_container.mount(Button("Edit", id="btn-edit-task", variant="primary"))
        button_container.mount(
            Button("Toggle Complete", id="btn-toggle-task", variant="success")
        )
        button_container.mount(Button("Delete", id="btn-delete-task", variant="error"))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle subtask selection - toggle completion."""
        if not self.current_task or not self.current_task.subtasks:
            return

        # Get the index of the selected subtask
        list_view = event.list_view
        index = list_view.index

        # Check if index is valid
        if index is not None and 0 <= index < len(self.current_task.subtasks):
            subtask = self.current_task.subtasks[index]
            # Post message to app to handle the toggle and save
            self.post_message(SubtaskToggled(self.current_task, subtask.id))

    def clear(self) -> None:
        """Clear the task detail display."""
        self.show_task(None)
