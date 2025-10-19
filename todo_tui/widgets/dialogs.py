"""Dialog widgets for user interactions."""

from typing import List, Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Input,
    Label,
    ListItem,
    ListView,
    Select,
    Static,
    Switch,
    TextArea,
)

from ..icons import Icons
from ..models import Project, Settings, Task


class AddTaskDialog(ModalScreen):
    """Modal dialog for adding a new task."""

    DEFAULT_CSS = """
    AddTaskDialog {
        align: center middle;
    }

    AddTaskDialog > #dialog-container {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }

    #task-description-input {
        height: 6;
        min-height: 6;
    }

    #task-notes-input {
        height: 6;
        min-height: 6;
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
            yield Label(f"{Icons.PLUS} Add New Task", classes="header")
            yield Label("Title:")
            yield Input(placeholder="Enter task title", id="task-title-input")
            yield Label("Priority:")
            priority_options = [
                ("None", "none"),
                (f"[#89b4fa]{Icons.BOOKMARK}[/] Low", "low"),
                (f"[#f9e2af]{Icons.BOOKMARK}[/] Medium", "medium"),
                (f"[#f38ba8]{Icons.BOOKMARK}[/] High", "high"),
            ]
            yield Select(options=priority_options, value="none", id="priority-select")
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

            priority_select = self.query_one("#priority-select", Select)
            priority = (
                priority_select.value
                if priority_select.value != Select.BLANK
                else "none"
            )
            description = self.query_one(
                "#task-description-input", TextArea
            ).text.strip()
            notes = self.query_one("#task-notes-input", TextArea).text.strip()

            task = Task(
                title=title,
                description=description,
                notes=notes,
                project_id=self.project_id,
                priority=priority,
            )
            self.dismiss(task)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle enter key in input field."""
        if event.input.id == "task-title-input":
            # Move to Add button
            self.query_one("#btn-add", Button).focus()

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape":
            self.dismiss(None)
            event.prevent_default()


class EditTaskDialog(ModalScreen):
    """Modal dialog for editing an existing task."""

    DEFAULT_CSS = """
    EditTaskDialog {
        align: center middle;
    }

    EditTaskDialog > #dialog-container {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }

    #task-description-input {
        height: 6;
        min-height: 6;
    }

    #task-notes-input {
        height: 6;
        min-height: 6;
    }

    #dialog-buttons {
        height: auto;
        layout: horizontal;
        align: center middle;
    }

    #subtask-section {
        height: auto;
    }

    #edit-subtask-list {
        max-height: 10;
        height: auto;
    }

    .subtask-row {
        height: auto;
        width: 100%;
    }

    .subtask-text {
        width: 1fr;
    }

    .subtask-delete-btn {
        width: 4;
        min-width: 4;
        height: 1;
        padding: 0;
        background: transparent;
        border: none;
        color: $error;
    }

    .subtask-delete-btn:hover {
        color: $error-lighten-1;
        background: $panel;
    }
    """

    def __init__(self, task: Task, projects: Optional[List[Project]] = None):
        super().__init__()
        self.edit_task = task
        self.projects = projects or []

    def compose(self) -> ComposeResult:
        """Compose the edit task dialog."""
        with Container(id="dialog-container"):
            yield Label(f"{Icons.EDIT} Edit Task", classes="header")
            yield Label("Title:")
            yield Input(
                value=self.edit_task.title,
                placeholder="Enter task title",
                id="task-title-input",
            )

            # Priority selector
            yield Label("Priority:")
            priority_options = [
                ("None", "none"),
                (f"[#89b4fa]{Icons.BOOKMARK}[/] Low", "low"),
                (f"[#f9e2af]{Icons.BOOKMARK}[/] Medium", "medium"),
                (f"[#f38ba8]{Icons.BOOKMARK}[/] High", "high"),
            ]
            yield Select(
                options=priority_options,
                value=self.edit_task.priority,
                id="priority-select-edit",
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
                yield Label(
                    "Subtasks (Space: toggle, ✗: remove):", classes="detail-label"
                )
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

        # Show empty state if no subtasks
        if not self.edit_task.subtasks:
            subtask_list.append(
                ListItem(
                    Static(
                        "No subtasks yet. Type above and press Enter to add one!",
                        classes="muted",
                    )
                )
            )
            return

        for idx, subtask in enumerate(self.edit_task.subtasks):
            checkbox = Icons.CHECK_SQUARE if subtask.completed else Icons.SQUARE_O
            item_class = "completed" if subtask.completed else ""

            # Create widgets for the subtask
            subtask_text = Static(
                f"{checkbox} {subtask.title}",
                classes=f"subtask-item subtask-text {item_class}",
            )
            delete_btn = Button(
                Icons.TIMES,
                name=f"delete-subtask-{idx}",
                classes="subtask-delete-btn",
            )

            # Create a horizontal container with the widgets
            row = Horizontal(subtask_text, delete_btn, classes="subtask-row")
            subtask_list.append(ListItem(row))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        # Check if this is a delete-subtask button
        if event.button.name and event.button.name.startswith("delete-subtask-"):
            try:
                # Extract index from button name (e.g., "delete-subtask-0" -> 0)
                idx = int(event.button.name.split("-")[-1])
                if 0 <= idx < len(self.edit_task.subtasks):
                    subtask = self.edit_task.subtasks[idx]
                    self.edit_task.remove_subtask(subtask.id)
                    self._refresh_subtask_list()
            except (ValueError, IndexError):
                pass  # Invalid index, ignore
            return

        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            title = self.query_one("#task-title-input", Input).value.strip()
            if not title:
                return

            priority_select = self.query_one("#priority-select-edit", Select)
            priority = (
                priority_select.value
                if priority_select.value != Select.BLANK
                else "none"
            )
            description = self.query_one(
                "#task-description-input", TextArea
            ).text.strip()
            notes = self.query_one("#task-notes-input", TextArea).text.strip()

            self.edit_task.title = title
            self.edit_task.priority = priority
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
        # Handle escape key to close dialog
        if event.key == "escape":
            self.dismiss(None)
            event.prevent_default()
            return

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
        background: $surface;
        border: thick $primary;
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
            yield Label(f"{Icons.FOLDER} Add New Project", classes="header")
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

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape":
            self.dismiss(None)
            event.prevent_default()


class EditProjectDialog(ModalScreen):
    """Modal dialog for editing an existing project."""

    DEFAULT_CSS = """
    EditProjectDialog {
        align: center middle;
    }

    #dialog-container {
        width: 50;
        height: auto;
        background: $surface;
        border: thick $primary;
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
            yield Label(f"{Icons.EDIT} Edit Project", classes="header")
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

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape":
            self.dismiss(None)
            event.prevent_default()


class ConfirmDialog(ModalScreen):
    """Modal dialog for confirmation."""

    DEFAULT_CSS = """
    ConfirmDialog {
        align: center middle;
    }

    #dialog-container {
        width: 50;
        height: auto;
        background: $surface;
        border: thick $error;
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
            yield Label(f"{Icons.WARNING}  Confirm Action", classes="header")
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

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape":
            self.dismiss(False)
            event.prevent_default()


class MoveTaskDialog(ModalScreen):
    """Modal dialog for moving a task to a different project."""

    DEFAULT_CSS = """
    MoveTaskDialog {
        align: center middle;
    }

    #dialog-container {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
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
            yield Label(f"{Icons.FOLDER_OPEN} Move Task", classes="header")
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

            project_list.append(ListItem(Static(f"{Icons.FOLDER} {project.name}")))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle project selection."""
        if event.list_view.id != "move-project-list":
            return

        index = event.list_view.index
        # Filter out current project from list
        available_projects = [
            p for p in self.projects if p.id != self.current_project_id
        ]

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

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape":
            self.dismiss(None)
            event.prevent_default()


class SettingsDialog(ModalScreen):
    """Modal dialog for application settings."""

    DEFAULT_CSS = """
    SettingsDialog {
        align: center middle;
    }

    #dialog-container {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }

    #dialog-buttons {
        height: auto;
        layout: horizontal;
        align: center middle;
    }

    .setting-row {
        height: auto;
        margin: 1 0;
    }

    .setting-hint {
        color: $text-muted;
        text-style: italic;
        margin-left: 2;
    }
    """

    def __init__(self, current_settings: Settings, available_themes: List[str]):
        super().__init__()
        self.settings = current_settings
        self.available_themes = available_themes

    def compose(self) -> ComposeResult:
        """Compose the settings dialog."""
        with Container(id="dialog-container"):
            yield Label(f"{Icons.COG} Settings", classes="header")

            # Theme selection
            yield Label("Default Theme:")
            theme_options = [(name, name) for name in self.available_themes]
            yield Select(
                options=theme_options, value=self.settings.theme, id="theme-select"
            )

            # Show completed tasks toggle
            yield Label("Show Completed Tasks:")
            yield Switch(
                value=self.settings.show_completed_tasks, id="show-completed-switch"
            )

            # Weather configuration
            yield Label("Weather Location:")
            yield Input(
                value=self.settings.weather_location,
                placeholder="San Francisco  or  London,UK",
                id="weather-location-input",
            )

            yield Label("Temperature Unit:")
            yield Switch(
                value=self.settings.weather_use_fahrenheit, id="weather-unit-switch"
            )
            yield Static(
                "Fahrenheit (°F)"
                if self.settings.weather_use_fahrenheit
                else "Celsius (°C)",
                id="weather-unit-label",
                classes="setting-hint",
            )

            # Pomodoro duration settings
            yield Label("Pomodoro Work Duration (minutes):")
            yield Input(
                value=str(self.settings.pomodoro_work_minutes),
                placeholder="25",
                id="pomodoro-work-input",
                type="integer",
            )

            yield Label("Pomodoro Short Break (minutes):")
            yield Input(
                value=str(self.settings.pomodoro_short_break_minutes),
                placeholder="5",
                id="pomodoro-short-break-input",
                type="integer",
            )

            yield Label("Pomodoro Long Break (minutes):")
            yield Input(
                value=str(self.settings.pomodoro_long_break_minutes),
                placeholder="15",
                id="pomodoro-long-break-input",
                type="integer",
            )

            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", id="btn-cancel", variant="default")
                yield Button("Save", id="btn-save", variant="success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            # Read current values
            theme_select = self.query_one("#theme-select", Select)
            show_completed_switch = self.query_one("#show-completed-switch", Switch)

            # Read weather settings
            weather_location_input = self.query_one("#weather-location-input", Input)
            weather_unit_switch = self.query_one("#weather-unit-switch", Switch)

            # Read and validate pomodoro durations
            work_input = self.query_one("#pomodoro-work-input", Input)
            short_break_input = self.query_one("#pomodoro-short-break-input", Input)
            long_break_input = self.query_one("#pomodoro-long-break-input", Input)

            # Validate and parse durations with bounds checking
            try:
                work_minutes = int(work_input.value)
                if not (1 <= work_minutes <= 120):
                    work_minutes = self.settings.pomodoro_work_minutes
            except ValueError:
                work_minutes = self.settings.pomodoro_work_minutes

            try:
                short_break_minutes = int(short_break_input.value)
                if not (1 <= short_break_minutes <= 60):
                    short_break_minutes = self.settings.pomodoro_short_break_minutes
            except ValueError:
                short_break_minutes = self.settings.pomodoro_short_break_minutes

            try:
                long_break_minutes = int(long_break_input.value)
                if not (1 <= long_break_minutes <= 60):
                    long_break_minutes = self.settings.pomodoro_long_break_minutes
            except ValueError:
                long_break_minutes = self.settings.pomodoro_long_break_minutes

            # Update settings
            self.settings.theme = theme_select.value
            self.settings.show_completed_tasks = show_completed_switch.value
            self.settings.weather_location = weather_location_input.value.strip()
            self.settings.weather_use_fahrenheit = weather_unit_switch.value
            self.settings.pomodoro_work_minutes = work_minutes
            self.settings.pomodoro_short_break_minutes = short_break_minutes
            self.settings.pomodoro_long_break_minutes = long_break_minutes

            self.dismiss(self.settings)

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape":
            self.dismiss(None)
            event.prevent_default()


class ErrorDialog(ModalScreen):
    """Modal dialog for displaying error messages."""

    DEFAULT_CSS = """
    ErrorDialog {
        align: center middle;
    }

    ErrorDialog > #dialog-container {
        width: 50;
        height: auto;
        background: $surface;
        border: thick $error;
        padding: 1;
    }

    #dialog-buttons {
        height: auto;
        layout: horizontal;
        align: center middle;
    }
    """

    def __init__(self, message: str, title: str = "Error"):
        super().__init__()
        self.message = message
        self.title = title

    def compose(self) -> ComposeResult:
        """Compose the error dialog."""
        with Container(id="dialog-container"):
            yield Label(f"{Icons.WARNING}  {self.title}", classes="header")
            yield Label(self.message)
            with Horizontal(id="dialog-buttons"):
                yield Button("OK", id="btn-ok", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-ok":
            self.dismiss()

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape" or event.key == "enter":
            self.dismiss()
            event.prevent_default()


class InfoDialog(ModalScreen):
    """Modal dialog for displaying informational messages."""

    DEFAULT_CSS = """
    InfoDialog {
        align: center middle;
    }

    InfoDialog > #dialog-container {
        width: 50;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }

    #dialog-buttons {
        height: auto;
        layout: horizontal;
        align: center middle;
    }
    """

    def __init__(self, message: str, title: str = "Information"):
        super().__init__()
        self.message = message
        self.title = title

    def compose(self) -> ComposeResult:
        """Compose the info dialog."""
        with Container(id="dialog-container"):
            yield Label(f"{Icons.INFO}  {self.title}", classes="header")
            yield Label(self.message)
            with Horizontal(id="dialog-buttons"):
                yield Button("OK", id="btn-ok", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-ok":
            self.dismiss()

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape" or event.key == "enter":
            self.dismiss()
            event.prevent_default()


class HelpDialog(ModalScreen):
    """Modal dialog showing keyboard shortcuts and help information."""

    DEFAULT_CSS = """
    HelpDialog {
        align: center middle;
    }

    #dialog-container {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }

    .help-title {
        color: $primary;
        text-style: bold;
        margin-top: 1;
    }

    .help-item {
        margin-left: 1;
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
            yield Label(f"{Icons.QUESTION} Help - Keyboard Shortcuts", classes="header")

            # General shortcuts
            yield Static("General", classes="help-title")
            yield Static(
                "[bold yellow]n[/] - Add new task", classes="help-item", markup=True
            )
            yield Static(
                "[bold yellow]p[/] - Add new project", classes="help-item", markup=True
            )
            yield Static(
                "[bold yellow]?[/] - Show this help", classes="help-item", markup=True
            )
            yield Static(
                "[bold yellow]q[/] - Quit application", classes="help-item", markup=True
            )

            # Task shortcuts
            yield Static("Tasks (when task selected)", classes="help-title")
            yield Static(
                "[bold yellow]Enter[/] - Edit task", classes="help-item", markup=True
            )
            yield Static(
                "[bold yellow]Space[/] - Toggle completion",
                classes="help-item",
                markup=True,
            )
            yield Static(
                "[bold yellow]Delete[/] - Delete task", classes="help-item", markup=True
            )
            yield Static(
                "[bold yellow]m[/] - Move task to another project",
                classes="help-item",
                markup=True,
            )

            # Project shortcuts
            yield Static("Projects (when project selected)", classes="help-title")
            yield Static(
                "[bold yellow]E[/] - Edit project name",
                classes="help-item",
                markup=True,
            )
            yield Static(
                "[bold yellow]D[/] - Delete project (migrates tasks)",
                classes="help-item",
                markup=True,
            )

            # Subtask shortcuts
            yield Static("Subtasks (in edit dialog)", classes="help-title")
            yield Static(
                "[bold yellow]Enter[/] - Add subtask (in input field)",
                classes="help-item",
                markup=True,
            )
            yield Static(
                "[bold yellow]Space[/] - Toggle subtask completion",
                classes="help-item",
                markup=True,
            )
            yield Static(
                "[bold yellow]Delete[/] - Remove subtask",
                classes="help-item",
                markup=True,
            )

            # Navigation
            yield Static("Navigation", classes="help-title")
            yield Static(
                "[bold yellow]Tab[/] - Move focus between panels",
                classes="help-item",
                markup=True,
            )
            yield Static(
                "[bold yellow]↑/↓[/] - Navigate lists", classes="help-item", markup=True
            )

            with Horizontal(id="dialog-buttons"):
                yield Button("Close", id="btn-close", variant="success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-close":
            self.dismiss()

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape":
            self.dismiss()
            event.prevent_default()
