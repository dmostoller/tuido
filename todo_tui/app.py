"""Main Textual application."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from dotenv import load_dotenv
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, TabbedContent, TabPane

from .icons import Icons
from .models import Project, Settings, Task
from .storage import StorageManager
from .themes import ALL_THEMES
from .widgets.dashboard import Dashboard
from .widgets.dialogs import (
    AddProjectDialog,
    AddTaskDialog,
    ConfirmDialog,
    EditProjectDialog,
    EditTaskDialog,
    ErrorDialog,
    HelpDialog,
    InfoDialog,
    MoveTaskDialog,
    SettingsDialog,
)
from .widgets.pomodoro_widget import PomodoroWidget
from .widgets.project_list import (
    DeleteProjectRequested,
    EditProjectRequested,
    ProjectListPanel,
    ProjectSelected,
)
from .widgets.scratchpad import ScratchpadPanel
from .widgets.task_detail import SubtaskToggled, TaskDetailPanel
from .widgets.task_list import TaskListPanel, TaskSelected


class TodoApp(App):
    """A Terminal User Interface for managing tasks."""

    CSS_PATH = "theme.css"

    BINDINGS = [
        Binding("n", "add_task", "Add Task", priority=True),
        Binding("p", "add_project", "Add Project"),
        Binding("space", "toggle_task", "Toggle Complete"),
        Binding("s", "settings", "Settings"),
        Binding("ctrl+shift+s", "cloud_sync", "Cloud Sync"),
        Binding("q", "quit", "Quit"),
        Binding("?", "help", "Help"),
    ]

    def __init__(self):
        super().__init__()
        # Load settings from fixed config location
        self.settings = StorageManager.load_settings()
        # Initialize storage with default data directory
        self.storage = StorageManager()

        self.projects: List[Project] = []
        self.current_project_id: Optional[str] = None
        self.current_project: Optional[Project] = None
        self.current_task: Optional[Task] = None

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header()
        yield Dashboard(id="dashboard")
        with TabbedContent(initial="tasks-tab", id="main-tabs"):
            with TabPane(f"{Icons.LIST} Tasks", id="tasks-tab"):
                with Horizontal(id="main-content"):
                    with Vertical(id="left-column"):
                        yield ProjectListPanel(id="projects-panel")
                        yield TaskListPanel(id="task-list-panel")
                    yield TaskDetailPanel(id="task-detail-panel")
            with TabPane(f"{Icons.PENCIL} Scratchpad", id="scratchpad-tab"):
                yield ScratchpadPanel(self.storage, id="scratchpad-panel")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the application on mount."""
        self.title = "Tuido"
        self.sub_title = "TUI To-Do List"

        # Register custom themes with official color palettes
        for theme in ALL_THEMES:
            self.register_theme(theme)

        # Apply saved theme (loaded in __init__)
        self.theme = self.settings.theme

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

        # Startup cloud sync (if enabled)
        if self.settings.cloud_sync_enabled and self.settings.cloud_sync_token:
            self.run_worker(self._startup_sync(), exclusive=True)

    def _load_all_tasks(self) -> None:
        """Load and display all tasks across all projects."""
        all_tasks = self.storage.load_all_tasks()
        task_panel = self.query_one("#task-list-panel", TaskListPanel)
        task_panel.set_tasks(
            all_tasks, self.settings.show_completed_tasks if self.settings else True
        )

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
        task_panel.set_tasks(
            tasks, self.settings.show_completed_tasks if self.settings else True
        )

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

        # Refresh display with pulse animation
        task_panel = self.query_one("#task-list-panel", TaskListPanel)
        task_panel.refresh_display()

        # Pulse animation on task panel
        task_panel.styles.animate(
            "opacity",
            value=0.7,
            duration=0.2,
            easing="in_out_cubic",
            on_complete=lambda: task_panel.styles.animate(
                "opacity", value=1.0, duration=0.2, easing="in_out_cubic"
            ),
        )

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
            self.push_screen(
                ErrorDialog(
                    "Cannot delete the only project. You must have at least one project.",
                    "Cannot Delete Project",
                )
            )
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
            self.push_screen(
                InfoDialog(
                    "Please select a specific project first. You cannot move tasks from the 'All Tasks' view.",
                    "Select a Project",
                )
            )
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

    def action_settings(self) -> None:
        """Show settings dialog."""
        # Get list of available theme names
        theme_names = [theme.name for theme in ALL_THEMES]

        def check_settings(result: Optional[Settings]) -> None:
            """Callback when dialog is dismissed."""
            if result:
                # Save settings (using static method)
                StorageManager.save_settings(result)
                self.settings = result

                # Apply theme change
                self.theme = result.theme

                # Reload task list if show_completed_tasks changed
                if self.current_project_id is None:
                    self._load_all_tasks()
                else:
                    self._load_project_tasks(self.current_project_id)

                # Reset pomodoro timer to apply new durations
                try:
                    pomo_widget = self.query_one(PomodoroWidget)
                    pomo_widget.reset_timer()
                except Exception:
                    pass  # Widget might not be mounted yet

                # Refresh weather widget with new settings
                try:
                    from .widgets.weather_widget import WeatherWidget

                    weather_widget = self.query_one(WeatherWidget)
                    weather_widget.refresh_weather_settings()
                except Exception:
                    pass  # Widget might not be mounted yet

        self.push_screen(SettingsDialog(self.settings, theme_names), check_settings)

    def action_help(self) -> None:
        """Show help information."""
        self.push_screen(HelpDialog())

    async def action_quit(self) -> None:
        """Quit the application with cloud sync on exit."""
        # If cloud sync enabled, upload on exit
        if self.settings.cloud_sync_enabled and self.settings.cloud_sync_token:
            # Await sync before exit
            await self._exit_sync()

        # Exit the app
        self.exit()

    def action_cloud_sync(self) -> None:
        """Manually trigger cloud sync."""
        if not self.settings.cloud_sync_enabled:
            self.notify(
                "Cloud sync is disabled. Enable it in Settings.", severity="warning"
            )
            return

        if not self.settings.cloud_sync_token:
            self.notify(
                "No API token set. Configure cloud sync in Settings.", severity="error"
            )
            return

        # Run sync in background worker
        self.run_worker(self._manual_sync(), exclusive=True)

    async def _startup_sync(self) -> None:
        """Sync on app startup (download from cloud)."""
        from .cloud_sync import CloudSyncClient

        try:
            client = CloudSyncClient(
                api_url=self.settings.cloud_sync_url,
                api_token=self.settings.cloud_sync_token,
            )

            # Download latest from cloud
            success, message = await client.download(self.storage)

            if success:
                # Update last sync time
                self.settings.last_cloud_sync = datetime.now().isoformat()
                StorageManager.save_settings(self.settings)

                # Reload UI with synced data
                self.projects = self.storage.load_projects()
                self._load_all_tasks()

                self.notify(f"☁️  {message}", severity="information")
            else:
                # Don't show error on startup if no cloud data exists yet
                if "No cloud data found" not in message:
                    self.notify(f"Cloud sync: {message}", severity="warning")

        except Exception as e:
            self.notify(f"Startup sync failed: {str(e)}", severity="error")

    async def _manual_sync(self) -> None:
        """Manual sync triggered by user."""
        from .cloud_sync import CloudSyncClient

        try:
            self.notify("☁️  Syncing...", severity="information")

            client = CloudSyncClient(
                api_url=self.settings.cloud_sync_url,
                api_token=self.settings.cloud_sync_token,
            )

            # Smart sync (compares timestamps)
            success, message = await client.sync(self.storage)

            if success:
                # Update last sync time
                self.settings.last_cloud_sync = datetime.now().isoformat()
                StorageManager.save_settings(self.settings)

                # Reload UI
                self.projects = self.storage.load_projects()
                self._load_all_tasks()

                self.notify(f"☁️  {message}", severity="success")
            else:
                self.notify(f"❌ {message}", severity="error")

        except Exception as e:
            self.notify(f"Sync failed: {str(e)}", severity="error")

    async def _exit_sync(self) -> None:
        """Sync on app exit (upload to cloud)."""
        from .cloud_sync import CloudSyncClient
        import sys

        try:
            client = CloudSyncClient(
                api_url=self.settings.cloud_sync_url,
                api_token=self.settings.cloud_sync_token,
            )

            # Upload to cloud
            success, message = await client.upload(self.storage)

            if success:
                # Update last sync time
                self.settings.last_cloud_sync = datetime.now().isoformat()
                StorageManager.save_settings(self.settings)

        except Exception as e:
            # Log error but don't block app closing
            # Error is written to stderr for debugging without interrupting user
            print(f"Cloud sync on exit failed: {type(e).__name__}: {e}", file=sys.stderr)
            pass

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
