"""Dialog widgets for user interactions."""

import os
import webbrowser
from typing import List, Optional, Tuple

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
    TabbedContent,
    TabPane,
    TextArea,
)

from ..icons import Icons
from ..models import Note, Project, Settings, Snippet, Task


class AddTaskDialog(ModalScreen):
    """Modal dialog for adding a new task."""

    DEFAULT_CSS = """
    AddTaskDialog {
        align: center middle;
    }

    AddTaskDialog > #dialog-container {
        width: 60;
        height: auto;
        border: round $primary;
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
                (f"[$primary]{Icons.BOOKMARK}[/] Low", "low"),
                (f"[$secondary]{Icons.BOOKMARK}[/] Medium", "medium"),
                (f"[$accent]{Icons.BOOKMARK}[/] High", "high"),
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
        border: round $primary;
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
                (f"[$primary]{Icons.BOOKMARK}[/] Low", "low"),
                (f"[$secondary]{Icons.BOOKMARK}[/] Medium", "medium"),
                (f"[$accent]{Icons.BOOKMARK}[/] High", "high"),
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
        border: round $primary;
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
        border: round $primary;
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
        border: round $error;
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


class SyncDirectionDialog(ModalScreen):
    """Modal dialog for choosing cloud sync direction."""

    DEFAULT_CSS = """
    SyncDirectionDialog {
        align: center middle;
    }

    SyncDirectionDialog > #dialog-container {
        width: 60;
        height: 20;
        border: round $primary;
        padding: 1;
    }

    #sync-info {
        padding: 1 0;
        background: $panel;
        margin-bottom: 1;
    }

    #dialog-buttons {
        height: auto;
        layout: horizontal;
        align: center middle;
    }
    """

    def __init__(self, cloud_timestamp: Optional[str], local_timestamp: Optional[str]):
        """Initialize sync direction dialog.

        Args:
            cloud_timestamp: Last cloud sync timestamp (ISO format)
            local_timestamp: Last local sync timestamp (ISO format)
        """
        super().__init__()
        self.cloud_timestamp = cloud_timestamp or "Never"
        self.local_timestamp = local_timestamp or "Never"

    def compose(self) -> ComposeResult:
        """Compose the sync direction dialog."""
        with Container(id="dialog-container"):
            yield Label(f"{Icons.CLOUD}  Choose Sync Direction", classes="header")
            yield Label(
                "Both cloud and local data exist. Choose which direction to sync:"
            )
            with Container(id="sync-info"):
                yield Label(f"☁️  Cloud last synced: {self.cloud_timestamp}")
                yield Label(f"💾 Local last synced: {self.local_timestamp}")
            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", id="btn-cancel", variant="default")
                yield Button("⬇ Download", id="btn-download", variant="primary")
                yield Button("⬆ Upload", id="btn-upload", variant="success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-download":
            self.dismiss("download")
        elif event.button.id == "btn-upload":
            self.dismiss("upload")

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape":
            self.dismiss(None)
            event.prevent_default()


class StartupSyncDialog(ModalScreen):
    """Modal dialog shown on startup asking if user wants to download from cloud."""

    DEFAULT_CSS = """
    StartupSyncDialog {
        align: center middle;
    }

    StartupSyncDialog > #dialog-container {
        width: 60;
        height: 18;
        border: round $primary;
        padding: 1;
    }

    #sync-info {
        padding: 1 0;
        background: $panel;
        margin-bottom: 1;
    }

    #dialog-buttons {
        height: auto;
        layout: horizontal;
        align: center middle;
    }
    """

    def __init__(self, cloud_timestamp: Optional[str]):
        """Initialize startup sync dialog.

        Args:
            cloud_timestamp: Last cloud sync timestamp (ISO format)
        """
        super().__init__()
        self.cloud_timestamp = cloud_timestamp or "Unknown"

    def compose(self) -> ComposeResult:
        """Compose the startup sync dialog."""
        with Container(id="dialog-container"):
            yield Label(f"{Icons.CLOUD}  Cloud Data Found", classes="header")
            yield Label("Cloud sync data is available. Do you want to download it?")
            with Container(id="sync-info"):
                yield Label(f"☁️  Last synced: {self.cloud_timestamp}")
                yield Label("⚠️  This will replace your local data")
            with Horizontal(id="dialog-buttons"):
                yield Button("Skip", id="btn-skip", variant="default")
                yield Button("⬇ Download", id="btn-download", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-skip":
            self.dismiss(False)
        elif event.button.id == "btn-download":
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
        border: round $primary;
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


def _detect_terminal() -> Tuple[str, str]:
    """Detect the current terminal emulator and return setup instructions.

    Returns:
        Tuple of (terminal_name, configuration_instructions)
    """
    term_program = os.environ.get("TERM_PROGRAM", "").lower()
    ghostty_dir = os.environ.get("GHOSTTY_RESOURCES_DIR", "")

    if ghostty_dir:
        return (
            "Ghostty",
            "Config file: ~/.config/ghostty/config\n"
            "Add: font-family = JetBrainsMono Nerd Font",
        )
    elif term_program == "vscode":
        return (
            "VS Code Terminal",
            "Settings → Search 'terminal.integrated.fontFamily'\n"
            "Set to: JetBrainsMono Nerd Font",
        )
    elif term_program == "iterm.app":
        return (
            "iTerm2",
            "Preferences → Profiles → Text → Font\n"
            "Select: JetBrainsMono Nerd Font",
        )
    elif term_program == "apple_terminal":
        return (
            "macOS Terminal",
            "Preferences → Profiles → Text → Change Font\n"
            "Select: JetBrainsMono Nerd Font",
        )
    elif term_program == "hyper":
        return (
            "Hyper",
            "Config file: ~/.hyper.js\n"
            "Set fontFamily: 'JetBrainsMono Nerd Font'",
        )
    elif term_program == "alacritty":
        return (
            "Alacritty",
            "Config file: ~/.config/alacritty/alacritty.yml\n"
            "Set font.normal.family: JetBrainsMono Nerd Font",
        )
    elif term_program == "wezterm":
        return (
            "WezTerm",
            "Config file: ~/.wezterm.lua\n"
            "Set config.font = wezterm.font('JetBrainsMono Nerd Font')",
        )
    elif term_program == "kitty":
        return (
            "Kitty",
            "Config file: ~/.config/kitty/kitty.conf\n"
            "Set font_family JetBrainsMono Nerd Font",
        )
    else:
        return (
            "Unknown Terminal",
            "Configure your terminal's font settings to use:\n"
            "JetBrainsMono Nerd Font",
        )


class OnboardingDialog(ModalScreen):
    """Modal dialog for first-run onboarding and setup wizard."""

    DEFAULT_CSS = """
    OnboardingDialog {
        align: center middle;
    }

    OnboardingDialog > #dialog-container {
        width: 75;
        height: auto;
        max-height: 90%;
        border: round $primary;
        padding: 1 2;
    }

    OnboardingDialog .section {
        margin: 1 0;
        padding: 1;
        border: round $accent;
    }

    OnboardingDialog .section-header {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    OnboardingDialog .section-description {
        color: $text-muted;
        margin-bottom: 1;
    }

    OnboardingDialog .instructions {
        color: $text;
        margin: 1 0;
    }

    OnboardingDialog .link-row {
        height: auto;
        margin: 1 0;
    }

    OnboardingDialog .setting-row {
        height: auto;
        margin: 1 0;
    }

    OnboardingDialog .setting-hint {
        color: $text-muted;
        text-style: italic;
        margin-left: 2;
    }

    OnboardingDialog #dialog-buttons {
        height: auto;
        layout: horizontal;
        align: center middle;
        margin-top: 1;
    }

    OnboardingDialog .welcome-header {
        text-style: bold;
        color: $primary;
        text-align: center;
        margin-bottom: 1;
    }

    OnboardingDialog .font-test-box {
        background: $panel;
        padding: 1;
        margin: 1 0;
        border: round $primary;
    }

    OnboardingDialog .font-test-icons {
        text-align: center;
        text-style: bold;
        color: $accent;
    }

    OnboardingDialog .terminal-detected {
        color: $success;
        text-style: bold;
        margin: 1 0;
    }

    OnboardingDialog .font-status-good {
        color: $success;
        text-style: bold;
    }

    OnboardingDialog .font-status-bad {
        color: $warning;
    }

    OnboardingDialog #font-help-section {
        display: none;
    }

    OnboardingDialog #font-help-section.visible {
        display: block;
    }

    OnboardingDialog TabbedContent {
        height: auto;
        max-height: 50;
    }

    OnboardingDialog TabPane {
        padding: 1;
    }
    """

    def __init__(self, current_settings: Settings):
        super().__init__()
        self.settings = current_settings
        self.terminal_name, self.terminal_instructions = _detect_terminal()

    def compose(self) -> ComposeResult:
        """Compose the onboarding dialog."""
        with Container(id="dialog-container"):
            yield Label(
                f"{Icons.STAR} Welcome to Tuido!",
                classes="welcome-header",
            )
            yield Static(
                "Let's get you set up for the best experience.",
                classes="section-description",
            )

            with TabbedContent(initial="font-tab"):
                # Font Setup Tab
                with TabPane(f"{Icons.PALETTE} Font Setup", id="font-tab"):
                    # Show detected terminal
                    yield Static(
                        f"{Icons.CHECK} Detected: {self.terminal_name}",
                        classes="terminal-detected",
                    )

                    yield Static(
                        "Tuido uses Nerd Font icons for a beautiful interface. "
                        "Do these icons display correctly?",
                        classes="section-description",
                    )

                    # Font test box with sample icons
                    with Container(classes="font-test-box"):
                        yield Static(
                            f"  {Icons.CHECK}  {Icons.STAR}  {Icons.FOLDER}  {Icons.CLOCK}  {Icons.CLOUD_SUN}  ",
                            classes="font-test-icons",
                        )
                        yield Static(
                            "You should see: checkmark, star, folder, clock, sun/cloud",
                            classes="setting-hint",
                        )

                    # Font status toggle
                    with Horizontal(classes="setting-row"):
                        yield Label("Icons display correctly:")
                        yield Switch(value=True, id="font-working-switch")
                        yield Static(
                            "Yes, I see the icons!",
                            id="font-status-label",
                            classes="font-status-good",
                        )

                    # Show configuration instructions (hidden by default if icons work)
                    with Container(id="font-help-section"):
                        with Horizontal(classes="link-row"):
                            yield Button(
                                f"{Icons.DOWNLOAD} Download JetBrains Mono Nerd Font",
                                id="btn-download-font",
                                variant="primary",
                            )
                        yield Static(
                            f"For {self.terminal_name}:\n{self.terminal_instructions}",
                            classes="instructions",
                        )
                        yield Static(
                            "After configuring, restart your terminal completely.",
                            classes="setting-hint",
                        )

                # Weather Setup Tab
                with TabPane(f"{Icons.CLOUD_SUN} Weather (Optional)", id="weather-tab"):
                    yield Static(
                        "The weather widget displays current conditions and forecast. "
                        "It requires a free OpenWeatherMap API key.",
                        classes="section-description",
                    )
                    with Horizontal(classes="link-row"):
                        yield Button(
                            f"{Icons.LINK} Get Free API Key",
                            id="btn-get-api-key",
                            variant="default",
                        )
                    yield Label("API Key:")
                    yield Input(
                        value=self.settings.weather_api_key,
                        placeholder="Paste your OpenWeatherMap API key here",
                        id="weather-api-key-input",
                        password=True,
                    )
                    yield Label("Location:")
                    yield Input(
                        value=self.settings.weather_location,
                        placeholder="e.g., San Francisco  or  London,UK",
                        id="weather-location-input",
                    )
                    with Horizontal(classes="setting-row"):
                        yield Label("Temperature Unit:")
                        yield Switch(
                            value=self.settings.weather_use_fahrenheit,
                            id="weather-unit-switch",
                        )
                        yield Static(
                            "Fahrenheit (°F)"
                            if self.settings.weather_use_fahrenheit
                            else "Celsius (°C)",
                            id="weather-unit-label",
                            classes="setting-hint",
                        )
                    with Horizontal(classes="setting-row"):
                        yield Label("Enable Weather Widget:")
                        yield Switch(
                            value=self.settings.show_weather_widget,
                            id="show-weather-switch",
                        )
                        yield Static(
                            "Disable to skip weather setup",
                            classes="setting-hint",
                        )

            with Horizontal(id="dialog-buttons"):
                yield Button("Skip for Now", id="btn-skip", variant="default")
                yield Button(
                    f"{Icons.CHECK} Get Started",
                    id="btn-save",
                    variant="success",
                )

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Handle switch changes for live updates."""
        if event.switch.id == "font-working-switch":
            # Toggle visibility of font help section
            font_help = self.query_one("#font-help-section", Container)
            font_status = self.query_one("#font-status-label", Static)
            if event.value:
                # Icons work - hide help section
                font_help.remove_class("visible")
                font_status.update("Yes, I see the icons!")
                font_status.remove_class("font-status-bad")
                font_status.add_class("font-status-good")
            else:
                # Icons don't work - show help section
                font_help.add_class("visible")
                font_status.update("No, I see rectangles □")
                font_status.remove_class("font-status-good")
                font_status.add_class("font-status-bad")
        elif event.switch.id == "weather-unit-switch":
            label = self.query_one("#weather-unit-label", Static)
            label.update("Fahrenheit (°F)" if event.value else "Celsius (°C)")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-download-font":
            webbrowser.open("https://www.nerdfonts.com/font-downloads")
        elif event.button.id == "btn-get-api-key":
            webbrowser.open("https://openweathermap.org/api")
        elif event.button.id == "btn-skip":
            # Mark onboarding complete but don't save weather settings
            self.settings.onboarding_complete = True
            self.dismiss(self.settings)
        elif event.button.id == "btn-save":
            # Save all settings
            weather_api_key = self.query_one(
                "#weather-api-key-input", Input
            ).value.strip()
            weather_location = self.query_one(
                "#weather-location-input", Input
            ).value.strip()
            weather_use_fahrenheit = self.query_one(
                "#weather-unit-switch", Switch
            ).value
            show_weather = self.query_one("#show-weather-switch", Switch).value

            self.settings.weather_api_key = weather_api_key
            self.settings.weather_location = weather_location
            self.settings.weather_use_fahrenheit = weather_use_fahrenheit
            self.settings.show_weather_widget = show_weather
            self.settings.onboarding_complete = True
            self.dismiss(self.settings)

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape":
            # Treat escape as skip
            self.settings.onboarding_complete = True
            self.dismiss(self.settings)
            event.prevent_default()


class SettingsDialog(ModalScreen):
    """Modal dialog for application settings with tabbed layout."""

    DEFAULT_CSS = """
    SettingsDialog {
        align: center middle;
    }

    SettingsDialog > #dialog-container {
        width: 75;
        height: auto;
        max-height: 85%;
        border: round $primary;
        padding: 1;
    }

    SettingsDialog TabbedContent {
        height: auto;
        max-height: 60;
    }

    SettingsDialog TabPane {
        padding: 1;
    }

    SettingsDialog #dialog-buttons {
        height: auto;
        layout: horizontal;
        align: center middle;
        margin-top: 1;
    }

    SettingsDialog .setting-row {
        height: auto;
        margin: 1 0;
    }

    SettingsDialog .setting-hint {
        color: $text-muted;
        text-style: italic;
        margin-left: 2;
    }

    SettingsDialog .section-description {
        color: $text-muted;
        margin-bottom: 1;
    }
    """

    def __init__(self, current_settings: Settings, available_themes: List[str]):
        super().__init__()
        self.settings = current_settings
        self.available_themes = available_themes
        self.original_theme = current_settings.theme  # Store for revert on cancel

    def compose(self) -> ComposeResult:
        """Compose the settings dialog with tabs."""
        with Container(id="dialog-container"):
            yield Label(f"{Icons.COG} Settings", classes="header")

            with TabbedContent(initial="general-tab"):
                # General Tab
                with TabPane(f"{Icons.COG} General", id="general-tab"):
                    yield Label("Default Theme:")
                    theme_options = [(name, name) for name in self.available_themes]
                    yield Select(
                        options=theme_options,
                        value=self.settings.theme,
                        id="theme-select",
                    )

                    with Horizontal(classes="setting-row"):
                        yield Label("Show Completed Tasks:")
                        yield Switch(
                            value=self.settings.show_completed_tasks,
                            id="show-completed-switch",
                        )

                    yield Static(
                        "Run the setup wizard to configure fonts and weather:",
                        classes="section-description",
                    )
                    yield Button(
                        f"{Icons.STAR} Run Setup Wizard",
                        id="btn-setup-wizard",
                        variant="default",
                    )

                # Weather Tab
                with TabPane(f"{Icons.CLOUD_SUN} Weather", id="weather-tab"):
                    with Horizontal(classes="setting-row"):
                        yield Label("Enable Weather Widget:")
                        yield Switch(
                            value=self.settings.show_weather_widget,
                            id="show-weather-switch",
                        )
                        yield Static(
                            "Shows weather and forecast in dashboard",
                            classes="setting-hint",
                        )

                    yield Label("API Key (from OpenWeatherMap):")
                    yield Input(
                        value=self.settings.weather_api_key,
                        placeholder="Paste your OpenWeatherMap API key",
                        id="weather-api-key-input",
                        password=True,
                    )
                    yield Static(
                        "Get a free key at: openweathermap.org/api",
                        classes="setting-hint",
                    )

                    yield Label("Location:")
                    yield Input(
                        value=self.settings.weather_location,
                        placeholder="e.g., San Francisco  or  London,UK",
                        id="weather-location-input",
                    )

                    with Horizontal(classes="setting-row"):
                        yield Label("Temperature Unit:")
                        yield Switch(
                            value=self.settings.weather_use_fahrenheit,
                            id="weather-unit-switch",
                        )
                        yield Static(
                            "Fahrenheit (°F)"
                            if self.settings.weather_use_fahrenheit
                            else "Celsius (°C)",
                            id="weather-unit-label",
                            classes="setting-hint",
                        )

                # Pomodoro Tab
                with TabPane(f"{Icons.TOMATO} Pomodoro", id="pomodoro-tab"):
                    yield Static(
                        "Customize your Pomodoro timer durations:",
                        classes="section-description",
                    )

                    yield Label("Work Duration (minutes):")
                    yield Input(
                        value=str(self.settings.pomodoro_work_minutes),
                        placeholder="25",
                        id="pomodoro-work-input",
                        type="integer",
                    )

                    yield Label("Short Break (minutes):")
                    yield Input(
                        value=str(self.settings.pomodoro_short_break_minutes),
                        placeholder="5",
                        id="pomodoro-short-break-input",
                        type="integer",
                    )

                    yield Label("Long Break (minutes):")
                    yield Input(
                        value=str(self.settings.pomodoro_long_break_minutes),
                        placeholder="15",
                        id="pomodoro-long-break-input",
                        type="integer",
                    )

                # Cloud Sync Tab
                with TabPane(f"{Icons.CLOUD} Cloud Sync", id="cloud-tab"):
                    yield Static(
                        "Sync your data across devices via tuido.vercel.app",
                        classes="section-description",
                    )

                    with Horizontal(classes="setting-row"):
                        yield Label("Enable Cloud Sync:")
                        yield Switch(
                            value=self.settings.cloud_sync_enabled,
                            id="cloud-sync-enabled-switch",
                        )

                    yield Label("API Token:")
                    yield Input(
                        value=self.settings.cloud_sync_token,
                        placeholder="Paste your API token from tuido.vercel.app",
                        id="cloud-token-input",
                        password=True,
                    )

                    yield Label("API URL:")
                    yield Input(
                        value=self.settings.cloud_sync_url,
                        placeholder="https://tuido.vercel.app/api",
                        id="cloud-url-input",
                    )

                    if self.settings.last_cloud_sync:
                        yield Static(
                            f"Last synced: {self.settings.last_cloud_sync}",
                            classes="setting-hint",
                        )
                    else:
                        yield Static(
                            "Never synced",
                            classes="setting-hint",
                        )

                    yield Static(
                        "Get your token at: https://tuido.vercel.app",
                        classes="setting-hint",
                    )

            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", id="btn-cancel", variant="default")
                yield Button("Save", id="btn-save", variant="success")

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle theme selection changes - apply immediately for live preview."""
        if event.select.id == "theme-select":
            # Apply the theme immediately for preview
            self.app.theme = event.value

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Handle switch changes for live updates."""
        if event.switch.id == "weather-unit-switch":
            label = self.query_one("#weather-unit-label", Static)
            label.update("Fahrenheit (°F)" if event.value else "Celsius (°C)")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-cancel":
            # Revert to original theme when canceling
            self.app.theme = self.original_theme
            self.dismiss(None)
        elif event.button.id == "btn-setup-wizard":
            # Close settings and open onboarding wizard
            self.app.theme = self.original_theme
            self.dismiss("open_wizard")
        elif event.button.id == "btn-save":
            # Read current values from all tabs
            theme_select = self.query_one("#theme-select", Select)
            show_completed_switch = self.query_one("#show-completed-switch", Switch)

            # Read weather settings
            show_weather_switch = self.query_one("#show-weather-switch", Switch)
            weather_api_key_input = self.query_one("#weather-api-key-input", Input)
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

            # Read cloud sync settings
            cloud_sync_enabled = self.query_one("#cloud-sync-enabled-switch", Switch)
            cloud_token_input = self.query_one("#cloud-token-input", Input)
            cloud_url_input = self.query_one("#cloud-url-input", Input)

            # Update settings
            self.settings.theme = theme_select.value
            self.settings.show_completed_tasks = show_completed_switch.value
            self.settings.show_weather_widget = show_weather_switch.value
            self.settings.weather_api_key = weather_api_key_input.value.strip()
            self.settings.weather_location = weather_location_input.value.strip()
            self.settings.weather_use_fahrenheit = weather_unit_switch.value
            self.settings.pomodoro_work_minutes = work_minutes
            self.settings.pomodoro_short_break_minutes = short_break_minutes
            self.settings.pomodoro_long_break_minutes = long_break_minutes
            self.settings.cloud_sync_enabled = cloud_sync_enabled.value
            self.settings.cloud_sync_token = cloud_token_input.value.strip()
            self.settings.cloud_sync_url = (
                cloud_url_input.value.strip() or "https://tuido.vercel.app/api"
            )

            self.dismiss(self.settings)

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape":
            # Revert to original theme when canceling
            self.app.theme = self.original_theme
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
        border: round $error;
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
        border: round $primary;
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
        border: round $primary;
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


class AddNoteDialog(ModalScreen):
    """Modal dialog for adding a new note."""

    DEFAULT_CSS = """
    AddNoteDialog {
        align: center middle;
    }

    #dialog-container {
        width: 50;
        height: auto;
        border: round $primary;
        padding: 1;
    }

    #dialog-buttons {
        height: auto;
        layout: horizontal;
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the add note dialog."""
        with Container(id="dialog-container"):
            yield Label(f"{Icons.PLUS} Add New Note", classes="header")
            yield Label("Note Title:")
            yield Input(placeholder="Enter note title", id="note-title-input")
            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", id="btn-cancel", variant="default")
                yield Button("Create", id="btn-create", variant="success")

    def on_mount(self) -> None:
        """Focus the input field when dialog opens."""
        self.query_one("#note-title-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-create":
            title = self.query_one("#note-title-input", Input).value.strip()
            if not title:
                return

            # Create new note
            note = Note(title=title, content="")
            self.dismiss(note)

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape":
            self.dismiss(None)
            event.prevent_default()
        elif event.key == "enter":
            # Trigger create button
            title = self.query_one("#note-title-input", Input).value.strip()
            if title:
                note = Note(title=title, content="")
                self.dismiss(note)
            event.prevent_default()


class RenameNoteDialog(ModalScreen):
    """Modal dialog for renaming a note."""

    DEFAULT_CSS = """
    RenameNoteDialog {
        align: center middle;
    }

    #dialog-container {
        width: 50;
        height: auto;
        border: round $primary;
        padding: 1;
    }

    #dialog-buttons {
        height: auto;
        layout: horizontal;
        align: center middle;
    }
    """

    def __init__(self, note: Note):
        super().__init__()
        self.note = note

    def compose(self) -> ComposeResult:
        """Compose the rename note dialog."""
        with Container(id="dialog-container"):
            yield Label(f"{Icons.PENCIL} Rename Note", classes="header")
            yield Label("Note Title:")
            yield Input(
                value=self.note.title,
                placeholder="Enter note title",
                id="note-title-input",
            )
            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", id="btn-cancel", variant="default")
                yield Button("Rename", id="btn-rename", variant="success")

    def on_mount(self) -> None:
        """Focus and select text in the input field when dialog opens."""
        input_widget = self.query_one("#note-title-input", Input)
        input_widget.focus()
        # Select all text for easy editing
        input_widget.action_select_all()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-rename":
            title = self.query_one("#note-title-input", Input).value.strip()
            if not title:
                return

            # Update note title
            self.note.title = title
            self.dismiss(self.note)

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape":
            self.dismiss(None)
            event.prevent_default()
        elif event.key == "enter":
            # Trigger rename button
            title = self.query_one("#note-title-input", Input).value.strip()
            if title:
                self.note.title = title
                self.dismiss(self.note)
            event.prevent_default()


class AddSnippetDialog(ModalScreen):
    """Modal dialog for adding a new code snippet."""

    DEFAULT_CSS = """
    AddSnippetDialog {
        align: center middle;
    }

    #dialog-container {
        width: 70;
        height: auto;
        border: round $primary;
        padding: 1;
    }

    #snippet-command-input {
        height: 8;
        min-height: 8;
    }

    #dialog-buttons {
        height: auto;
        layout: horizontal;
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the add snippet dialog."""
        with Container(id="dialog-container"):
            yield Label(f"{Icons.PLUS} Add New Snippet", classes="header")
            yield Label("Name:")
            yield Input(placeholder="e.g., SSH to staging", id="snippet-name-input")
            yield Label("Command/Code:")
            yield TextArea(id="snippet-command-input")
            yield Label("Tags (comma-separated, optional):")
            yield Input(
                placeholder="e.g., docker, ssh, deploy", id="snippet-tags-input"
            )
            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", id="btn-cancel", variant="default")
                yield Button("Add Snippet", id="btn-add", variant="success")

    def on_mount(self) -> None:
        """Focus the name input field when dialog opens."""
        self.query_one("#snippet-name-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-add":
            name = self.query_one("#snippet-name-input", Input).value.strip()
            command = self.query_one("#snippet-command-input", TextArea).text.strip()
            tags_str = self.query_one("#snippet-tags-input", Input).value.strip()

            # Validate required fields
            if not name or not command:
                self.app.notify("Name and command are required", severity="warning")
                return

            # Parse tags from comma-separated string
            tags = [t.strip() for t in tags_str.split(",") if t.strip()]

            # Create new snippet
            snippet = Snippet(name=name, command=command, tags=tags)
            self.dismiss(snippet)

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape":
            self.dismiss(None)
            event.prevent_default()


class EditSnippetDialog(ModalScreen):
    """Modal dialog for editing an existing code snippet."""

    DEFAULT_CSS = """
    EditSnippetDialog {
        align: center middle;
    }

    #dialog-container {
        width: 70;
        height: auto;
        border: round $primary;
        padding: 1;
    }

    #snippet-command-input {
        height: 8;
        min-height: 8;
    }

    #dialog-buttons {
        height: auto;
        layout: horizontal;
        align: center middle;
    }
    """

    def __init__(self, snippet: Snippet):
        super().__init__()
        self.snippet = snippet

    def compose(self) -> ComposeResult:
        """Compose the edit snippet dialog."""
        with Container(id="dialog-container"):
            yield Label(f"{Icons.PENCIL} Edit Snippet", classes="header")
            yield Label("Name:")
            yield Input(
                value=self.snippet.name,
                placeholder="e.g., SSH to staging",
                id="snippet-name-input",
            )
            yield Label("Command/Code:")
            yield TextArea(text=self.snippet.command, id="snippet-command-input")
            yield Label("Tags (comma-separated, optional):")
            yield Input(
                value=", ".join(self.snippet.tags) if self.snippet.tags else "",
                placeholder="e.g., docker, ssh, deploy",
                id="snippet-tags-input",
            )
            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", id="btn-cancel", variant="default")
                yield Button("Save", id="btn-save", variant="success")

    def on_mount(self) -> None:
        """Focus the name input field when dialog opens."""
        self.query_one("#snippet-name-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            name = self.query_one("#snippet-name-input", Input).value.strip()
            command = self.query_one("#snippet-command-input", TextArea).text.strip()
            tags_str = self.query_one("#snippet-tags-input", Input).value.strip()

            # Validate required fields
            if not name or not command:
                self.app.notify("Name and command are required", severity="warning")
                return

            # Parse tags from comma-separated string
            tags = [t.strip() for t in tags_str.split(",") if t.strip()]

            # Update snippet
            self.snippet.name = name
            self.snippet.command = command
            self.snippet.tags = tags
            self.dismiss(self.snippet)

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape":
            self.dismiss(None)
            event.prevent_default()
