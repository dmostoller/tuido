"""Project list widget."""

from __future__ import annotations

from typing import List, Optional

from textual.app import ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.widgets import Label, ListItem, ListView, Static

from ..models import Project


class ProjectSelected(Message):
    """Message sent when a project is selected."""

    def __init__(self, project_id: Optional[str]):
        super().__init__()
        self.project_id = project_id


class ProjectListPanel(Container):
    """Panel displaying the list of projects."""

    DEFAULT_CSS = """
    ProjectListPanel {
        width: auto;
    }
    """

    def __init__(self, id: str = "projects-panel"):
        super().__init__(id=id)
        self.projects: List[Project] = []
        self.selected_project_id: Optional[str] = None

    def compose(self) -> ComposeResult:
        """Compose the project list panel."""
        yield Label("📁 Projects", classes="header")
        yield ListView(id="project-list")

    def set_projects(self, projects: List[Project]) -> None:
        """Set the list of projects."""
        self.projects = projects
        self._update_list()

    def _update_list(self) -> None:
        """Update the project list display."""
        list_view = self.query_one("#project-list", ListView)
        list_view.clear()

        # Add "All Tasks" option
        list_view.append(
            ListItem(Static("📋 All Tasks", classes="all-tasks"), id="project-all")
        )

        # Add projects
        for project in self.projects:
            list_view.append(
                ListItem(Static(f"📁 {project.name}"), id=f"project-{project.id}")
            )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle project selection."""
        item_id = event.item.id

        if item_id == "project-all":
            self.selected_project_id = None
            self.post_message(ProjectSelected(None))
        elif item_id and item_id.startswith("project-"):
            project_id = item_id.replace("project-", "")
            self.selected_project_id = project_id
            self.post_message(ProjectSelected(project_id))

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
