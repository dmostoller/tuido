"""Main Textual application."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header

from .models import Project, Task
from .storage import StorageManager
from .themes import ALL_THEMES
from .widgets.dashboard import Dashboard
from .widgets.dialogs import (
    AddProjectDialog,
    AddTaskDialog,
    ConfirmDialog,
    EditProjectDialog,
    EditTaskDialog,
    HelpDialog,
    MoveTaskDialog,
)
from .widgets.project_list import (
    DeleteProjectRequested,
    EditProjectRequested,
    ProjectListPanel,
    ProjectSelected,
)
from .widgets.task_detail import SubtaskToggled, TaskDetailPanel
from .widgets.task_list import TaskListPanel, TaskSelected


class TodoApp(App):
    """A Terminal User Interface for managing tasks."""

    CSS_PATH = "theme.css"

    BINDINGS = [
        Binding("n", "add_task", "Add Task", priority=True),
        Binding("p", "add_project", "Add Project"),
        Binding("space", "toggle_task", "Toggle Complete"),
        Binding("enter", "edit_task", "Edit Task"),
        Binding("q", "quit", "Quit"),
        Binding("?", "help", "Help"),
    ]

    def __init__(self):
        super().__init__()
        self.storage = StorageManager()
        self.projects: List[Project] = []
        self.current_project_id: Optional[str] = None
        self.current_project: Optional[Project] = None
        self.current_task: Optional[Task] = None

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header()
        yield Dashboard(id="dashboard")
        with Horizontal(id="main-content"):
            with Vertical(id="left-column"):
                yield ProjectListPanel(id="projects-panel")
                yield TaskListPanel(id="task-list-panel")
            yield TaskDetailPanel(id="task-detail-panel")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the application on mount."""
        self.title = "Tuido"
        self.sub_title = "Terminal Task Manager"

        # Register custom themes with official color palettes
        for theme in ALL_THEMES:
            self.register_theme(theme)

        # Set default theme to Catppuccin Mocha
        self.theme = "catppuccin-mocha"

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

        # Update project panel with task counts
        project_panel = self.query_one("#projects-panel", ProjectListPanel)
        project_panel.update_tasks(all_tasks)

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

        # Update project panel with task counts
        project_panel = self.query_one("#projects-panel", ProjectListPanel)
        project_panel.update_tasks(all_tasks)

        self.current_project_id = project_id

    def on_project_selected(self, message: ProjectSelected) -> None:
        """Handle project selection."""
        if message.project_id is None:
            self._load_all_tasks()
            self.current_project = None
        else:
            self._load_project_tasks(message.project_id)
            # Find and store the current project object
            self.current_project = next(
                (p for p in self.projects if p.id == message.project_id), None
            )

        # Clear task detail panel
        detail_panel = self.query_one("#task-detail-panel", TaskDetailPanel)
        detail_panel.clear()
        self.current_task = None

    def on_task_selected(self, message: TaskSelected) -> None:
        """Handle task selection."""
        self.current_task = message.task
        detail_panel = self.query_one("#task-detail-panel", TaskDetailPanel)
        detail_panel.show_task(message.task)

    def on_edit_project_requested(self, message: EditProjectRequested) -> None:
        """Handle edit project request from project panel."""
        self.action_edit_project()

    def on_delete_project_requested(self, message: DeleteProjectRequested) -> None:
        """Handle delete project request from project panel."""
        self.action_delete_project()

    def on_subtask_toggled(self, message: SubtaskToggled) -> None:
        """Handle subtask toggle."""
        task = message.task
        subtask_id = message.subtask_id

        # Toggle the subtask
        task.toggle_subtask(subtask_id)

        # Save the updated task
        self.storage.update_task(task)

        # Refresh displays
        task_panel = self.query_one("#task-list-panel", TaskListPanel)
        task_panel.refresh_display()

        detail_panel = self.query_one("#task-detail-panel", TaskDetailPanel)
        detail_panel.show_task(task)

        # Update dashboard
        all_tasks = self.storage.load_all_tasks()
        dashboard = self.query_one("#dashboard", Dashboard)
        dashboard.update_metrics(all_tasks)

        # Update current task reference
        self.current_task = task

    def action_add_task(self) -> None:
        """Show add task dialog."""
        # Determine which project to add to
        project_id = self.current_project_id
        if project_id is None and self.projects:
            # Default to first project if viewing all tasks
            project_id = self.projects[0].id

        if not project_id:
            return

        def check_add_task(result: Optional[Task]) -> None:
            """Callback when dialog is dismissed."""
            if result:
                # Save task
                self.storage.add_task(result)

                # Refresh display
                if self.current_project_id is None:
                    self._load_all_tasks()
                else:
                    self._load_project_tasks(self.current_project_id)

        self.push_screen(AddTaskDialog(project_id), check_add_task)

    def action_edit_task(self) -> None:
        """Show edit task dialog for current task."""
        if not self.current_task:
            return

        def check_edit_task(result: Optional[Task]) -> None:
            """Callback when dialog is dismissed."""
            if result:
                # Check if project was changed
                project_changed = result.project_id != self.current_task.project_id

                # Save task
                self.storage.update_task(result)

                # Refresh display
                if self.current_project_id is None:
                    self._load_all_tasks()
                else:
                    self._load_project_tasks(self.current_project_id)

                # If project changed and we're viewing a specific project,
                # clear detail panel since task is no longer in this project
                if (
                    project_changed
                    and self.current_project_id
                    and result.project_id != self.current_project_id
                ):
                    detail_panel = self.query_one("#task-detail-panel", TaskDetailPanel)
                    detail_panel.clear()
                    self.current_task = None
                else:
                    # Update detail panel with edited task
                    detail_panel = self.query_one("#task-detail-panel", TaskDetailPanel)
                    detail_panel.show_task(result)
                    self.current_task = result

        self.push_screen(
            EditTaskDialog(self.current_task, self.projects), check_edit_task
        )

    def action_delete_task(self) -> None:
        """Delete the current task."""
        if not self.current_task:
            return

        # Store reference to task since self.current_task might change
        task_to_delete = self.current_task

        def check_delete_task(confirmed: bool) -> None:
            """Callback when dialog is dismissed."""
            if confirmed:
                # Delete task
                self.storage.delete_task(task_to_delete.project_id, task_to_delete.id)

                # Refresh display
                if self.current_project_id is None:
                    self._load_all_tasks()
                else:
                    self._load_project_tasks(self.current_project_id)

                # Clear detail panel
                detail_panel = self.query_one("#task-detail-panel", TaskDetailPanel)
                detail_panel.clear()
                self.current_task = None

        self.push_screen(
            ConfirmDialog(f"Delete task '{task_to_delete.title}'?"), check_delete_task
        )

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

    def action_add_project(self) -> None:
        """Show add project dialog."""

        def check_add_project(result: Optional[Project]) -> None:
            """Callback when dialog is dismissed."""
            if result:
                # Save project
                self.storage.add_project(result)
                self.projects = self.storage.load_projects()

                # Update project list
                project_panel = self.query_one("#projects-panel", ProjectListPanel)
                project_panel.set_projects(self.projects)

        self.push_screen(AddProjectDialog(), check_add_project)

    def action_edit_project(self) -> None:
        """Show edit project dialog for current project."""
        if not self.current_project:
            return

        def check_edit_project(result: Optional[Project]) -> None:
            """Callback when dialog is dismissed."""
            if result:
                # Save project
                self.storage.update_project(result)
                self.projects = self.storage.load_projects()

                # Update project list
                project_panel = self.query_one("#projects-panel", ProjectListPanel)
                project_panel.set_projects(self.projects)

                # Update current project reference
                self.current_project = result

        self.push_screen(EditProjectDialog(self.current_project), check_edit_project)

    def action_delete_project(self) -> None:
        """Delete the current project after confirming task migration."""
        if not self.current_project:
            return

        # Don't allow deleting if it's the only project
        if len(self.projects) <= 1:
            # TODO: Show error message - need at least one project
            return

        # Store reference since self.current_project might change
        project_to_delete = self.current_project

        # Get tasks in this project
        tasks_to_migrate = self.storage.load_tasks(project_to_delete.id)
        task_count = len(tasks_to_migrate)

        if task_count > 0:
            # Show confirmation with migration info
            message = (
                f"Delete project '{project_to_delete.name}'?\n"
                f"{task_count} task(s) will be moved to the first remaining project."
            )
        else:
            message = f"Delete project '{project_to_delete.name}'?"

        def check_delete_project(confirmed: bool) -> None:
            """Callback when dialog is dismissed."""
            if confirmed:
                # If there are tasks, migrate them to first available project
                if task_count > 0:
                    # Find first project that's not the one being deleted
                    target_project = next(
                        (p for p in self.projects if p.id != project_to_delete.id), None
                    )
                    if target_project:
                        for task in tasks_to_migrate:
                            task.project_id = target_project.id
                            self.storage.update_task(task)

                # Delete the project
                self.storage.delete_project(project_to_delete.id)
                self.projects = self.storage.load_projects()

                # Update project list
                project_panel = self.query_one("#projects-panel", ProjectListPanel)
                project_panel.set_projects(self.projects)

                # Load all tasks view
                self._load_all_tasks()
                self.current_project = None

        self.push_screen(ConfirmDialog(message), check_delete_project)

    def action_move_task(self) -> None:
        """Show move task dialog for current task."""
        if not self.current_task:
            return

        # Can't move if not viewing a specific project
        if not self.current_project_id:
            # TODO: Show error message - select a project first
            return

        # Store reference since self.current_task might change
        task_to_move = self.current_task

        def check_move_task(result: Optional[str]) -> None:
            """Callback when dialog is dismissed with selected project_id."""
            if result:
                # Update task's project_id
                task_to_move.project_id = result
                self.storage.update_task(task_to_move)

                # Refresh display for current project
                self._load_project_tasks(self.current_project_id)

                # Clear detail panel since task is no longer in this project
                detail_panel = self.query_one("#task-detail-panel", TaskDetailPanel)
                detail_panel.clear()
                self.current_task = None

        self.push_screen(
            MoveTaskDialog(task_to_move, self.projects, self.current_project_id),
            check_move_task,
        )

    def on_key(self, event) -> None:
        """Handle context-aware keyboard shortcuts."""
        # Get the focused widget's parent to determine context
        focused = self.focused
        if not focused:
            return

        # Check if we're in the task list panel
        try:
            task_panel = self.query_one("#task-list-panel", TaskListPanel)
            if focused.has_ancestor(task_panel):
                if event.key == "m":
                    self.action_move_task()
                    event.prevent_default()
                # Note: enter, delete, and space are already bound globally
                # but they only work when there's a current task
                return
        except Exception:
            pass

    def action_help(self) -> None:
        """Show help information."""
        self.push_screen(HelpDialog())

    def on_button_pressed(self, event) -> None:
        """Handle button presses in task detail panel."""
        # Task detail panel buttons
        if event.button.id == "btn-edit-task":
            self.action_edit_task()
        elif event.button.id == "btn-toggle-task":
            self.action_toggle_task()
        elif event.button.id == "btn-delete-task":
            self.action_delete_task()


def main():
    """Run the Todo TUI application."""
    # Load environment variables from .env file
    load_dotenv()

    app = TodoApp()
    app.run()


def dev():
    """Run in development mode with auto-reload."""
    import subprocess
    import sys

    subprocess.run([sys.executable, "-m", "textual", "run", "--dev", __file__])
