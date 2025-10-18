"""Dialog widgets for user interactions."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, TextArea

from ..models import Project, Task


class AddTaskDialog(ModalScreen):
    """Modal dialog for adding a new task."""

    DEFAULT_CSS = """
    AddTaskDialog {
        align: center middle;
    }

    #dialog-container {
        width: 60;
        height: auto;
        background: #313244;
        border: thick #89b4fa;
        padding: 1;
    }

    #dialog-buttons {
        height: auto;
        layout: horizontal;
        align: center middle;
    }
    """

    def __init__(self, project_id: str = ""):
        super().__init__()
        self.project_id = project_id

    def compose(self) -> ComposeResult:
        """Compose the add task dialog."""
        with Container(id="dialog-container"):
            yield Label("➕ Add New Task", classes="header")
            yield Label("Title:")
            yield Input(placeholder="Enter task title", id="task-title-input")
            yield Label("Description (optional):")
            yield TextArea(id="task-description-input")
            yield Label("Notes (optional):")
            yield TextArea(id="task-notes-input")
            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", id="btn-cancel", variant="default")
                yield Button("Add Task", id="btn-add", variant="success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-add":
            title = self.query_one("#task-title-input", Input).value.strip()
            if not title:
                return

            description = self.query_one(
                "#task-description-input", TextArea
            ).text.strip()
            notes = self.query_one("#task-notes-input", TextArea).text.strip()

            task = Task(
                title=title,
                description=description,
                notes=notes,
                project_id=self.project_id,
            )
            self.dismiss(task)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle enter key in input field."""
        if event.input.id == "task-title-input":
            # Move to Add button
            self.query_one("#btn-add", Button).focus()


class EditTaskDialog(ModalScreen):
    """Modal dialog for editing an existing task."""

    DEFAULT_CSS = """
    EditTaskDialog {
        align: center middle;
    }

    #dialog-container {
        width: 60;
        height: auto;
        background: #313244;
        border: thick #89b4fa;
        padding: 1;
    }

    #dialog-buttons {
        height: auto;
        layout: horizontal;
        align: center middle;
    }

    #subtask-section {
        height: auto;
    }
    """

    def __init__(self, task: Task):
        super().__init__()
        self.task = task

    def compose(self) -> ComposeResult:
        """Compose the edit task dialog."""
        with Container(id="dialog-container"):
            yield Label("✏️ Edit Task", classes="header")
            yield Label("Title:")
            yield Input(
                value=self.task.title,
                placeholder="Enter task title",
                id="task-title-input",
            )
            yield Label("Description (optional):")
            yield TextArea(self.task.description, id="task-description-input")
            yield Label("Notes (optional):")
            yield TextArea(self.task.notes, id="task-notes-input")

            # Subtasks section
            with Vertical(id="subtask-section"):
                yield Label("Subtasks:")
                yield Input(placeholder="Add subtask (press Enter)", id="subtask-input")
                for subtask in self.task.subtasks:
                    checkbox = "☑" if subtask.completed else "☐"
                    yield Label(
                        f"{checkbox} {subtask.title}", id=f"subtask-{subtask.id}"
                    )

            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", id="btn-cancel", variant="default")
                yield Button("Save", id="btn-save", variant="success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            title = self.query_one("#task-title-input", Input).value.strip()
            if not title:
                return

            description = self.query_one(
                "#task-description-input", TextArea
            ).text.strip()
            notes = self.query_one("#task-notes-input", TextArea).text.strip()

            self.task.title = title
            self.task.description = description
            self.task.notes = notes

            self.dismiss(self.task)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle enter key in input field."""
        if event.input.id == "subtask-input":
            subtask_title = event.input.value.strip()
            if subtask_title:
                subtask = self.task.add_subtask(subtask_title)
                # Add subtask to display
                section = self.query_one("#subtask-section", Vertical)
                section.mount(Label(f"☐ {subtask.title}", id=f"subtask-{subtask.id}"))
                event.input.value = ""


class AddProjectDialog(ModalScreen):
    """Modal dialog for adding a new project."""

    DEFAULT_CSS = """
    AddProjectDialog {
        align: center middle;
    }

    #dialog-container {
        width: 50;
        height: auto;
        background: #313244;
        border: thick #89b4fa;
        padding: 1;
    }

    #dialog-buttons {
        height: auto;
        layout: horizontal;
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the add project dialog."""
        with Container(id="dialog-container"):
            yield Label("📁 Add New Project", classes="header")
            yield Label("Project Name:")
            yield Input(placeholder="Enter project name", id="project-name-input")
            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", id="btn-cancel", variant="default")
                yield Button("Create", id="btn-create", variant="success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-create":
            name = self.query_one("#project-name-input", Input).value.strip()
            if not name:
                return

            project = Project(name=name)
            self.dismiss(project)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle enter key in input field."""
        if event.input.id == "project-name-input":
            self.query_one("#btn-create", Button).focus()


class ConfirmDialog(ModalScreen):
    """Modal dialog for confirmation."""

    DEFAULT_CSS = """
    ConfirmDialog {
        align: center middle;
    }

    #dialog-container {
        width: 50;
        height: auto;
        background: $surface0;
        border: thick $red;
        padding: 1;
    }

    #dialog-buttons {
        height: auto;
        layout: horizontal;
        align: center middle;
    }
    """

    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        """Compose the confirm dialog."""
        with Container(id="dialog-container"):
            yield Label("⚠️  Confirm Action", classes="header")
            yield Label(self.message)
            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", id="btn-cancel", variant="default")
                yield Button("Confirm", id="btn-confirm", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-cancel":
            self.dismiss(False)
        elif event.button.id == "btn-confirm":
            self.dismiss(True)
