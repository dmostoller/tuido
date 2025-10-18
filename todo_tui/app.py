"""Main Textual application."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Footer, Header

from .models import Project, Task
from .storage import StorageManager
from .widgets.dashboard import Dashboard
from .widgets.dialogs import (
    AddProjectDialog,
    AddTaskDialog,
    ConfirmDialog,
    EditTaskDialog,
)
from .widgets.project_list import ProjectListPanel, ProjectSelected
from .widgets.task_detail import TaskDetailPanel
from .widgets.task_list import TaskListPanel, TaskSelected


class TodoApp(App):
    """A Terminal User Interface for managing todos."""

    CSS_PATH = Path(__file__).parent / "theme.css"

    BINDINGS = [
        Binding("ctrl+n", "add_task", "Add Task", priority=True),
        Binding("ctrl+p", "add_project", "Add Project"),
        Binding("space", "toggle_task", "Toggle Complete"),
        Binding("delete", "delete_task", "Delete Task"),
        Binding("enter", "edit_task", "Edit Task"),
        Binding("q", "quit", "Quit"),
        Binding("?", "help", "Help"),
    ]

    def __init__(self):
        super().__init__()
        self.storage = StorageManager()
        self.projects: List[Project] = []
        self.current_project_id: Optional[str] = None
        self.current_task: Optional[Task] = None

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header()
        yield Dashboard(id="dashboard")
        with Horizontal(id="main-content"):
            yield ProjectListPanel(id="projects-panel")
            yield TaskListPanel(id="task-list-panel")
            yield TaskDetailPanel(id="task-detail-panel")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the application on mount."""
        self.title = "Todo TUI"
        self.sub_title = "Terminal Todo Manager"

        # Load projects
        self.projects = self.storage.load_projects()

        # Create default project if none exist
        if not self.projects:
            default_project = Project(name="Personal")
            self.storage.add_project(default_project)
            self.projects = [default_project]

        # Set up UI
        project_panel = self.query_one("#projects-panel", ProjectListPanel)
        project_panel.set_projects(self.projects)

        # Load all tasks initially
        self._load_all_tasks()

    def _load_all_tasks(self) -> None:
        """Load and display all tasks across all projects."""
        all_tasks = self.storage.load_all_tasks()
        task_panel = self.query_one("#task-list-panel", TaskListPanel)
        task_panel.set_tasks(all_tasks)

        # Update dashboard
        dashboard = self.query_one("#dashboard", Dashboard)
        dashboard.update_metrics(all_tasks)

        self.current_project_id = None

    def _load_project_tasks(self, project_id: str) -> None:
        """Load and display tasks for a specific project."""
        tasks = self.storage.load_tasks(project_id)
        task_panel = self.query_one("#task-list-panel", TaskListPanel)
        task_panel.set_tasks(tasks)

        # Update dashboard with all tasks for global metrics
        all_tasks = self.storage.load_all_tasks()
        dashboard = self.query_one("#dashboard", Dashboard)
        dashboard.update_metrics(all_tasks)

        self.current_project_id = project_id

    def on_project_selected(self, message: ProjectSelected) -> None:
        """Handle project selection."""
        if message.project_id is None:
            self._load_all_tasks()
        else:
            self._load_project_tasks(message.project_id)

        # Clear task detail panel
        detail_panel = self.query_one("#task-detail-panel", TaskDetailPanel)
        detail_panel.clear()
        self.current_task = None

    def on_task_selected(self, message: TaskSelected) -> None:
        """Handle task selection."""
        self.current_task = message.task
        detail_panel = self.query_one("#task-detail-panel", TaskDetailPanel)
        detail_panel.show_task(message.task)

    async def action_add_task(self) -> None:
        """Show add task dialog."""
        # Determine which project to add to
        project_id = self.current_project_id
        if project_id is None and self.projects:
            # Default to first project if viewing all tasks
            project_id = self.projects[0].id

        if not project_id:
            return

        result = await self.push_screen(
            AddTaskDialog(project_id), wait_for_dismiss=True
        )
        if result:
            # Save task
            self.storage.add_task(result)

            # Refresh display
            if self.current_project_id is None:
                self._load_all_tasks()
            else:
                self._load_project_tasks(self.current_project_id)

    async def action_edit_task(self) -> None:
        """Show edit task dialog for current task."""
        if not self.current_task:
            return

        result = await self.push_screen(
            EditTaskDialog(self.current_task), wait_for_dismiss=True
        )
        if result:
            # Save task
            self.storage.update_task(result)

            # Refresh display
            if self.current_project_id is None:
                self._load_all_tasks()
            else:
                self._load_project_tasks(self.current_project_id)

            # Update detail panel
            detail_panel = self.query_one("#task-detail-panel", TaskDetailPanel)
            detail_panel.show_task(result)

    async def action_delete_task(self) -> None:
        """Delete the current task."""
        if not self.current_task:
            return

        confirmed = await self.push_screen(
            ConfirmDialog(f"Delete task '{self.current_task.title}'?"),
            wait_for_dismiss=True,
        )

        if confirmed:
            # Delete task
            self.storage.delete_task(self.current_task.project_id, self.current_task.id)

            # Refresh display
            if self.current_project_id is None:
                self._load_all_tasks()
            else:
                self._load_project_tasks(self.current_project_id)

            # Clear detail panel
            detail_panel = self.query_one("#task-detail-panel", TaskDetailPanel)
            detail_panel.clear()
            self.current_task = None

    def action_toggle_task(self) -> None:
        """Toggle completion status of current task."""
        if not self.current_task:
            return

        # Toggle completion
        self.current_task.toggle_complete()
        self.storage.update_task(self.current_task)

        # Refresh display
        task_panel = self.query_one("#task-list-panel", TaskListPanel)
        task_panel.refresh_display()

        # Update detail panel
        detail_panel = self.query_one("#task-detail-panel", TaskDetailPanel)
        detail_panel.show_task(self.current_task)

        # Update dashboard
        if self.current_project_id is None:
            all_tasks = self.storage.load_all_tasks()
        else:
            all_tasks = self.storage.load_all_tasks()

        dashboard = self.query_one("#dashboard", Dashboard)
        dashboard.update_metrics(all_tasks)

    async def action_add_project(self) -> None:
        """Show add project dialog."""
        result = await self.push_screen(AddProjectDialog(), wait_for_dismiss=True)
        if result:
            # Save project
            self.storage.add_project(result)
            self.projects = self.storage.load_projects()

            # Update project list
            project_panel = self.query_one("#projects-panel", ProjectListPanel)
            project_panel.set_projects(self.projects)

    def action_help(self) -> None:
        """Show help information."""
        # TODO: Implement help screen
        pass

    async def on_button_pressed(self, event) -> None:
        """Handle button presses in task detail panel."""
        if event.button.id == "btn-edit-task":
            await self.action_edit_task()
        elif event.button.id == "btn-toggle-task":
            self.action_toggle_task()
        elif event.button.id == "btn-delete-task":
            await self.action_delete_task()
