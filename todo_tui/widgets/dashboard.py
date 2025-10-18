"""Dashboard widget showing metrics and statistics."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widget import Widget
from textual.widgets import Label, Static

from ..models import Task


class MetricCard(Widget):
    """A card displaying a single metric."""

    def __init__(self, label: str, value: str, id: str = None):
        super().__init__(id=id)
        self.label_text = label
        self.value_text = value

    def compose(self) -> ComposeResult:
        """Compose the metric card."""
        yield Static(self.value_text, classes="metric-value")
        yield Static(self.label_text, classes="metric-label")

    def update_value(self, value: str) -> None:
        """Update the metric value."""
        self.value_text = value
        self.query_one(".metric-value", Static).update(value)


class Dashboard(Container):
    """Dashboard panel showing task metrics and statistics."""

    DEFAULT_CSS = """
    Dashboard {
        height: auto;
    }
    """

    def __init__(self, id: str = "dashboard"):
        super().__init__(id=id)
        self.tasks: List[Task] = []

    def compose(self) -> ComposeResult:
        """Compose the dashboard."""
        yield Label("📊 Dashboard", classes="header")
        with Horizontal(id="metrics-container"):
            yield MetricCard("Total Tasks", "0", id="metric-total")
            yield MetricCard("Completed", "0", id="metric-completed")
            yield MetricCard("Completion Rate", "0%", id="metric-rate")
            yield MetricCard("Today", "0", id="metric-today")
            yield MetricCard("This Week", "0", id="metric-week")

    def update_metrics(self, tasks: List[Task]) -> None:
        """Update dashboard metrics with current tasks."""
        self.tasks = tasks

        total = len(tasks)
        completed = sum(1 for t in tasks if t.completed)
        rate = int((completed / total * 100)) if total > 0 else 0

        # Calculate today's completions
        today = datetime.now().date()
        today_completed = sum(
            1
            for t in tasks
            if t.completed
            and t.completed_at
            and datetime.fromisoformat(t.completed_at).date() == today
        )

        # Calculate this week's completions
        week_start = today - timedelta(days=today.weekday())
        week_completed = sum(
            1
            for t in tasks
            if t.completed
            and t.completed_at
            and datetime.fromisoformat(t.completed_at).date() >= week_start
        )

        # Update metric cards
        self.query_one("#metric-total", MetricCard).update_value(str(total))
        self.query_one("#metric-completed", MetricCard).update_value(str(completed))
        self.query_one("#metric-rate", MetricCard).update_value(f"{rate}%")
        self.query_one("#metric-today", MetricCard).update_value(str(today_completed))
        self.query_one("#metric-week", MetricCard).update_value(str(week_completed))
