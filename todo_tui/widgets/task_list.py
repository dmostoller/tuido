"""Task list widget."""

from __future__ import annotations

from typing import List, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.message import Message
from textual.widgets import Input, ListItem, ListView, Static

from ..icons import Icons
from ..models import Task


class SortMode:
    """Sort mode constants for task list."""

    PRIORITY = "priority"
    ALPHABETICAL = "alphabetical"
    DATE = "date"
    MANUAL = "manual"


class TaskSelected(Message):
    """Message sent when a task is selected."""

    def __init__(self, task: Optional[Task]):
        super().__init__()
        self.task = task


class TaskListPanel(Container):
    """Panel displaying the list of tasks."""

    DEFAULT_CSS = """
    TaskListPanel {
        width: auto;
        border-title-align: left;
    }

    TaskListPanel #task-search-input {
        margin: 0;
    }
    """

    BINDINGS = [
        Binding("/", "focus_search", "Search", show=False),
        Binding("ctrl+f", "focus_search", "Search", show=False),
        Binding("ctrl+s", "cycle_sort", "Sort", show=True),
    ]

    def __init__(self, id: str = "task-list-panel"):
        super().__init__(id=id)
        self.tasks: List[Task] = []
        self.displayed_tasks: List[Task] = []
        self.selected_task: Optional[Task] = None
        self.search_query: str = ""
        self.current_sort_mode: str = SortMode.PRIORITY

    def compose(self) -> ComposeResult:
        """Compose the task list panel."""
        yield Input(
            placeholder=f"{Icons.SEARCH} Search tasks...", id="task-search-input"
        )
        yield ListView(id="task-list")

    def on_mount(self) -> None:
        """Set up initial border title."""
        self._update_header()

    def set_tasks(self, tasks: List[Task], show_completed: bool = True) -> None:
        """Set the list of tasks."""
        # Filter out completed tasks if setting is disabled
        if not show_completed:
            tasks = [t for t in tasks if not t.completed]

        self.tasks = tasks
        self._update_list()

    def _sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks based on current sort mode, with completed tasks at bottom."""
        # Separate incomplete and completed tasks
        incomplete = [t for t in tasks if not t.completed]
        completed = [t for t in tasks if t.completed]

        # Define sort key functions for each mode
        if self.current_sort_mode == SortMode.PRIORITY:
            # Priority order: High (3) -> Medium (2) -> Low (1) -> None (0)
            priority_map = {"high": 3, "medium": 2, "low": 1}

            def priority_key(task: Task) -> int:
                return priority_map.get(
                    task.priority.lower() if task.priority else "", 0
                )

            incomplete.sort(key=priority_key, reverse=True)
            completed.sort(key=priority_key, reverse=True)

        elif self.current_sort_mode == SortMode.ALPHABETICAL:
            incomplete.sort(key=lambda t: t.title.lower())
            completed.sort(key=lambda t: t.title.lower())

        elif self.current_sort_mode == SortMode.DATE:
            # Sort by created_at, oldest first (use epoch for missing dates)
            incomplete.sort(
                key=lambda t: getattr(t, "created_at", "1970-01-01T00:00:00")
            )
            completed.sort(
                key=lambda t: getattr(t, "created_at", "1970-01-01T00:00:00")
            )

        # MANUAL mode: no sorting, keep original order

        # Return incomplete tasks followed by completed tasks
        return incomplete + completed

    def _update_header(self) -> None:
        """Update the border title to show current sort mode."""
        # Map sort modes to display text
        sort_display = {
            SortMode.PRIORITY: f"{Icons.CHECK} Tasks",
            SortMode.ALPHABETICAL: f"{Icons.CHECK} Tasks (A-Z)",
            SortMode.DATE: f"{Icons.CHECK} Tasks (by Date)",
            SortMode.MANUAL: f"{Icons.CHECK} Tasks (Manual)",
        }

        self.border_title = sort_display.get(
            self.current_sort_mode, f"{Icons.CHECK} Tasks"
        )

    def _update_list(self) -> None:
        """Update the task list display."""
        list_view = self.query_one("#task-list", ListView)
        list_view.clear()

        if not self.tasks:
            self.displayed_tasks = []
            list_view.append(
                ListItem(
                    Static("No tasks yet. Press Ctrl+N to add one!", classes="muted")
                )
            )
            return

        # Filter tasks based on search query
        filtered_tasks = self.tasks
        if self.search_query:
            query_lower = self.search_query.lower()
            filtered_tasks = [
                t
                for t in self.tasks
                if query_lower in t.title.lower()
                or query_lower in t.description.lower()
            ]

        # Apply sorting
        filtered_tasks = self._sort_tasks(filtered_tasks)

        # Store the displayed tasks for selection logic
        self.displayed_tasks = filtered_tasks

        # Show message if no matches
        if not filtered_tasks:
            self.displayed_tasks = []
            list_view.append(
                ListItem(
                    Static(f"No tasks match '{self.search_query}'", classes="muted")
                )
            )
            return

        # Add tasks
        for task in filtered_tasks:
            checkbox = Icons.CHECK_SQUARE if task.completed else Icons.SQUARE_O
            title_class = "task-title completed" if task.completed else "task-title"

            # Get priority indicator
            priority_icon, _ = task.get_priority_display()
            priority_str = f"{priority_icon} " if priority_icon else ""

            # Show subtask progress if any
            subtask_info = ""
            if task.subtasks:
                completed_subtasks = sum(1 for s in task.subtasks if s.completed)
                subtask_info = f" ({completed_subtasks}/{len(task.subtasks)})"

            list_view.append(
                ListItem(
                    Static(
                        f"{priority_str}{checkbox} {task.title}{subtask_info}",
                        classes=title_class,
                    ),
                    classes="completed" if task.completed else "",
                )
            )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle task selection."""
        # Get the index of the selected item
        list_view = self.query_one("#task-list", ListView)
        index = list_view.index

        # Check if we have tasks and the index is valid
        if index is not None and 0 <= index < len(self.displayed_tasks):
            self.selected_task = self.displayed_tasks[index]
            self.post_message(TaskSelected(self.selected_task))
        else:
            # No valid task selected (e.g., "No tasks" placeholder)
            self.selected_task = None
            self.post_message(TaskSelected(None))

    def add_task(self, task: Task) -> None:
        """Add a new task to the list."""
        self.tasks.append(task)
        self._update_list()

    def update_task(self, task: Task) -> None:
        """Update an existing task in the list."""
        for i, t in enumerate(self.tasks):
            if t.id == task.id:
                self.tasks[i] = task
                break
        self._update_list()

    def remove_task(self, task_id: str) -> None:
        """Remove a task from the list."""
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self._update_list()

        # If removed task was selected, clear selection
        if self.selected_task and self.selected_task.id == task_id:
            self.selected_task = None
            self.post_message(TaskSelected(None))

    def refresh_display(self) -> None:
        """Refresh the task list display."""
        self._update_list()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "task-search-input":
            self.search_query = event.value
            self._update_list()

    def action_focus_search(self) -> None:
        """Focus the search input."""
        search_input = self.query_one("#task-search-input", Input)
        search_input.focus()

    def action_cycle_sort(self) -> None:
        """Cycle through sort modes."""
        # Define the cycle order
        sort_cycle = [
            SortMode.PRIORITY,
            SortMode.ALPHABETICAL,
            SortMode.DATE,
            SortMode.MANUAL,
        ]

        # Find current index and move to next
        try:
            current_index = sort_cycle.index(self.current_sort_mode)
            next_index = (current_index + 1) % len(sort_cycle)
        except ValueError:
            # If current mode is not in cycle, start from beginning
            next_index = 0

        self.current_sort_mode = sort_cycle[next_index]

        # Update the header to show current sort mode
        self._update_header()

        # Refresh the display with new sort order
        self._update_list()

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        search_input = self.query_one("#task-search-input", Input)

        # Clear search with Escape when search has focus
        if event.key == "escape" and search_input.has_focus:
            search_input.value = ""
            self.search_query = ""
            self._update_list()
            # Return focus to the list
            list_view = self.query_one("#task-list", ListView)
            list_view.focus()
            event.prevent_default()
