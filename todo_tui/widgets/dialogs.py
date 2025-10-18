"""Dialog widgets for user interactions."""

from typing import List, Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, ListItem, ListView, Select, Static, TextArea

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

    def __init__(self, task: Task, projects: Optional[List[Project]] = None):
        super().__init__()
        self.edit_task = task
        self.projects = projects or []

    def compose(self) -> ComposeResult:
        """Compose the edit task dialog."""
        with Container(id="dialog-container"):
            yield Label("✏️ Edit Task", classes="header")
            yield Label("Title:")
            yield Input(
                value=self.edit_task.title,
                placeholder="Enter task title",
                id="task-title-input",
            )

            # Project selector (only show if projects are provided)
            if self.projects:
                yield Label("Project:")
                # Create options as (label, value) tuples
                project_options = [(p.name, p.id) for p in self.projects]
                yield Select(
                    options=project_options,
                    value=self.edit_task.project_id,
                    id="project-select",
                )

            yield Label("Description (optional):")
            yield TextArea(self.edit_task.description, id="task-description-input")
            yield Label("Notes (optional):")
            yield TextArea(self.edit_task.notes, id="task-notes-input")

            # Subtasks section
            with Vertical(id="subtask-section"):
                yield Label("Subtasks (Space: toggle, Delete: remove):", classes="detail-label")
                yield Input(placeholder="Add subtask (press Enter)", id="subtask-input")
                subtask_list = ListView(id="edit-subtask-list")
                yield subtask_list

            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", id="btn-cancel", variant="default")
                yield Button("Save", id="btn-save", variant="success")

    def on_mount(self) -> None:
        """Populate the subtask list after mounting."""
        self._refresh_subtask_list()

    def _refresh_subtask_list(self) -> None:
        """Refresh the subtask list display."""
        subtask_list = self.query_one("#edit-subtask-list", ListView)
        subtask_list.clear()

        for subtask in self.edit_task.subtasks:
            checkbox = "☑" if subtask.completed else "☐"
            item_class = "completed" if subtask.completed else ""
            subtask_list.append(
                ListItem(
                    Static(
                        f"{checkbox} {subtask.title}",
                        classes=f"subtask-item {item_class}",
                    )
                )
            )

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

            self.edit_task.title = title
            self.edit_task.description = description
            self.edit_task.notes = notes

            # Update project if selector is present
            if self.projects:
                try:
                    project_select = self.query_one("#project-select", Select)
                    if project_select.value != Select.BLANK:
                        self.edit_task.project_id = project_select.value
                except Exception:
                    pass  # Selector not found, keep existing project

            self.dismiss(self.edit_task)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle enter key in input field."""
        if event.input.id == "subtask-input":
            subtask_title = event.input.value.strip()
            if subtask_title:
                self.edit_task.add_subtask(subtask_title)
                self._refresh_subtask_list()
                event.input.value = ""

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle subtask selection - toggle completion."""
        if event.list_view.id != "edit-subtask-list":
            return

        if not self.edit_task.subtasks:
            return

        # Get the index of the selected subtask
        index = event.list_view.index

        # Check if index is valid
        if index is not None and 0 <= index < len(self.edit_task.subtasks):
            subtask = self.edit_task.subtasks[index]
            # Toggle the subtask
            self.edit_task.toggle_subtask(subtask.id)
            # Refresh the display
            self._refresh_subtask_list()

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts for subtask operations."""
        subtask_list = self.query_one("#edit-subtask-list", ListView)

        # Only handle keys when subtask list has focus
        if not subtask_list.has_focus:
            return

        index = subtask_list.index
        if index is None or not (0 <= index < len(self.edit_task.subtasks)):
            return

        subtask = self.edit_task.subtasks[index]

        if event.key == "delete":
            # Delete the selected subtask
            self.edit_task.remove_subtask(subtask.id)
            self._refresh_subtask_list()
            event.prevent_default()
        elif event.key == "space":
            # Toggle completion (also handled by list selection, but good for explicit shortcut)
            self.edit_task.toggle_subtask(subtask.id)
            self._refresh_subtask_list()
            event.prevent_default()


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


class EditProjectDialog(ModalScreen):
    """Modal dialog for editing an existing project."""

    DEFAULT_CSS = """
    EditProjectDialog {
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

    def __init__(self, project: Project):
        super().__init__()
        self.edit_project = project

    def compose(self) -> ComposeResult:
        """Compose the edit project dialog."""
        with Container(id="dialog-container"):
            yield Label("✏️ Edit Project", classes="header")
            yield Label("Project Name:")
            yield Input(
                value=self.edit_project.name,
                placeholder="Enter project name",
                id="project-name-input",
            )
            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", id="btn-cancel", variant="default")
                yield Button("Save", id="btn-save", variant="success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            name = self.query_one("#project-name-input", Input).value.strip()
            if not name:
                return

            self.edit_project.name = name
            self.dismiss(self.edit_project)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle enter key in input field."""
        if event.input.id == "project-name-input":
            self.query_one("#btn-save", Button).focus()


class ConfirmDialog(ModalScreen):
    """Modal dialog for confirmation."""

    DEFAULT_CSS = """
    ConfirmDialog {
        align: center middle;
    }

    #dialog-container {
        width: 50;
        height: auto;
        background: #313244;
        border: thick #f38ba8;
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


class MoveTaskDialog(ModalScreen):
    """Modal dialog for moving a task to a different project."""

    DEFAULT_CSS = """
    MoveTaskDialog {
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

    def __init__(self, task: Task, projects: List[Project], current_project_id: str):
        super().__init__()
        self.move_task = task
        self.projects = projects
        self.current_project_id = current_project_id
        self.selected_project_id: Optional[str] = None

    def compose(self) -> ComposeResult:
        """Compose the move task dialog."""
        with Container(id="dialog-container"):
            yield Label("📦 Move Task", classes="header")
            yield Label(f"Moving: {self.move_task.title}")
            yield Label("Select destination project:")

            project_list = ListView(id="move-project-list")
            yield project_list

            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", id="btn-cancel", variant="default")
                yield Button("Move", id="btn-move", variant="success")

    def on_mount(self) -> None:
        """Populate project list after mounting."""
        project_list = self.query_one("#move-project-list", ListView)

        for project in self.projects:
            # Skip current project
            if project.id == self.current_project_id:
                continue

            project_list.append(
                ListItem(Static(f"📁 {project.name}"))
            )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle project selection."""
        if event.list_view.id != "move-project-list":
            return

        index = event.list_view.index
        # Filter out current project from list
        available_projects = [p for p in self.projects if p.id != self.current_project_id]

        if index is not None and 0 <= index < len(available_projects):
            self.selected_project_id = available_projects[index].id

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-move":
            if self.selected_project_id:
                self.dismiss(self.selected_project_id)
            else:
                # No project selected, can't move
                self.dismiss(None)


class HelpDialog(ModalScreen):
    """Modal dialog showing keyboard shortcuts and help information."""

    DEFAULT_CSS = """
    HelpDialog {
        align: center middle;
    }

    #dialog-container {
        width: 70;
        height: auto;
        background: #313244;
        border: thick #89b4fa;
        padding: 1;
    }

    #help-content {
        height: auto;
        padding: 1;
    }

    .help-section {
        margin: 1 0;
    }

    .help-title {
        color: #89b4fa;
        text-style: bold;
        margin-bottom: 1;
    }

    .help-item {
        margin-left: 2;
    }

    .key {
        color: #f9e2af;
        text-style: bold;
    }

    #dialog-buttons {
        height: auto;
        layout: horizontal;
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the help dialog."""
        with Container(id="dialog-container"):
            yield Label("❓ Help - Keyboard Shortcuts", classes="header")

            with Vertical(id="help-content"):
                # General shortcuts
                with Vertical(classes="help-section"):
                    yield Static("General", classes="help-title")
                    yield Static("  [.key]Ctrl+N[/]  - Add new task", classes="help-item", markup=True)
                    yield Static("  [.key]Ctrl+P[/]  - Add new project", classes="help-item", markup=True)
                    yield Static("  [.key]?[/]       - Show this help", classes="help-item", markup=True)
                    yield Static("  [.key]q[/]       - Quit application", classes="help-item", markup=True)

                # Task shortcuts
                with Vertical(classes="help-section"):
                    yield Static("Tasks (when task selected)", classes="help-title")
                    yield Static("  [.key]Enter[/]   - Edit task", classes="help-item", markup=True)
                    yield Static("  [.key]Space[/]   - Toggle completion", classes="help-item", markup=True)
                    yield Static("  [.key]Delete[/]  - Delete task", classes="help-item", markup=True)
                    yield Static("  [.key]m[/]       - Move task to another project", classes="help-item", markup=True)

                # Project shortcuts
                with Vertical(classes="help-section"):
                    yield Static("Projects (when project selected)", classes="help-title")
                    yield Static("  [.key]e[/]       - Edit project name", classes="help-item", markup=True)
                    yield Static("  [.key]Delete[/]  - Delete project (migrates tasks)", classes="help-item", markup=True)

                # Subtask shortcuts
                with Vertical(classes="help-section"):
                    yield Static("Subtasks (in edit dialog)", classes="help-title")
                    yield Static("  [.key]Enter[/]   - Add subtask (in input field)", classes="help-item", markup=True)
                    yield Static("  [.key]Space[/]   - Toggle subtask completion", classes="help-item", markup=True)
                    yield Static("  [.key]Delete[/]  - Remove subtask", classes="help-item", markup=True)

                # Navigation
                with Vertical(classes="help-section"):
                    yield Static("Navigation", classes="help-title")
                    yield Static("  [.key]Tab[/]     - Move focus between panels", classes="help-item", markup=True)
                    yield Static("  [.key]↑/↓[/]     - Navigate lists", classes="help-item", markup=True)

            with Horizontal(id="dialog-buttons"):
                yield Button("Close", id="btn-close", variant="success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-close":
            self.dismiss()
