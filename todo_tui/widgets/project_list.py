"""Project list widget."""

from __future__ import annotations

from typing import List, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.message import Message
from textual.widgets import Label, ListItem, ListView, Static

from ..icons import Icons
from ..models import Project, Task


class ProjectSelected(Message):
    """Message sent when a project is selected."""

    def __init__(self, project_id: Optional[str]):
        super().__init__()
        self.project_id = project_id


class EditProjectRequested(Message):
    """Message sent when user wants to edit a project."""

    def __init__(self, project_id: str):
        super().__init__()
        self.project_id = project_id


class DeleteProjectRequested(Message):
    """Message sent when user wants to delete a project."""

    def __init__(self, project_id: str):
        super().__init__()
        self.project_id = project_id


class ProjectListPanel(Container):
    """Panel displaying the list of projects."""

    DEFAULT_CSS = """
    ProjectListPanel {
        width: auto;
    }
    """

    BINDINGS = [
        Binding("e", "edit_project", "Edit Project", show=False),
        Binding("d", "delete_project", "Delete Project", show=False),
    ]

    def __init__(self, id: str = "projects-panel"):
        super().__init__(id=id)
        self.projects: List[Project] = []
        self.all_tasks: List[Task] = []
        self.selected_project_id: Optional[str] = None

    def compose(self) -> ComposeResult:
        """Compose the project list panel."""
        yield Label(
            f"{Icons.FOLDER} Projects", classes="header", id="project-header-title"
        )
        yield ListView(id="project-list")

    def set_projects(self, projects: List[Project]) -> None:
        """Set the list of projects."""
        self.projects = projects
        self._update_list()

    def update_tasks(self, tasks: List[Task]) -> None:
        """Update the task list and refresh display."""
        self.all_tasks = tasks
        self._update_list()

    def _update_list(self) -> None:
        """Update the project list display."""
        try:
            list_view = self.query_one("#project-list", ListView)
        except Exception:
            # ListView not yet mounted
            return

        list_view.clear()

        # Check if there are no projects (shouldn't happen, but good fallback)
        if not self.projects:
            list_view.append(
                ListItem(
                    Static("No projects yet. Press 'p' to add one!", classes="muted")
                )
            )
            return

        # Calculate total task count for "All Tasks"
        total_count = len(self.all_tasks)
        total_completed = sum(1 for t in self.all_tasks if t.completed)

        # Add "All Tasks" option with count
        all_tasks_label = f"{Icons.LIST} All Tasks ({total_completed}/{total_count})"
        list_view.append(ListItem(Static(all_tasks_label)))

        # Add projects with task counts
        for project in self.projects:
            # Count tasks for this project
            project_tasks = [t for t in self.all_tasks if t.project_id == project.id]
            task_count = len(project_tasks)
            completed_count = sum(1 for t in project_tasks if t.completed)

            project_label = (
                f"{Icons.FOLDER} {project.name} ({completed_count}/{task_count})"
            )
            list_view.append(ListItem(Static(project_label)))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle project selection."""
        list_view = event.list_view
        index = list_view.index

        if index is None:
            return

        if index == 0:
            # First item is "All Tasks"
            self.selected_project_id = None
            self.post_message(ProjectSelected(None))
        elif 0 < index <= len(self.projects):
            # Project items (index 1+ maps to projects[0+])
            project = self.projects[index - 1]
            self.selected_project_id = project.id
            self.post_message(ProjectSelected(project.id))

    def add_project(self, project: Project) -> None:
        """Add a new project to the list."""
        self.projects.append(project)
        self._update_list()

    def remove_project(self, project_id: str) -> None:
        """Remove a project from the list."""
        self.projects = [p for p in self.projects if p.id != project_id]
        self._update_list()

        # If removed project was selected, select "All Tasks"
        if self.selected_project_id == project_id:
            self.selected_project_id = None
            list_view = self.query_one("#project-list", ListView)
            list_view.index = 0

    def action_edit_project(self) -> None:
        """Trigger edit project action in parent app."""
        if self.selected_project_id:
            self.post_message(EditProjectRequested(self.selected_project_id))

    def action_delete_project(self) -> None:
        """Trigger delete project action in parent app."""
        if self.selected_project_id:
            self.post_message(DeleteProjectRequested(self.selected_project_id))
