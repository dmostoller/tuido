"""Dashboard widget showing metrics and statistics."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import List

from textual.app import ComposeResult
from textual.containers import Container, Grid, Vertical
from textual.widgets import ProgressBar, Sparkline, Static

from ..icons import Icons
from ..models import Task
from .clock_widget import ClockWidget
from .pomodoro_widget import PomodoroWidget
from .stats_card import StatsCard


class Dashboard(Container):
    """Dashboard panel showing task metrics and statistics."""

    DEFAULT_CSS = """
    Dashboard {
        width: 100%;
    }

    Dashboard Grid {
        grid-size: 2 2;
        grid-columns: 1fr 1fr;
        grid-rows: 1fr 1fr;
        grid-gutter: 1 1;
        height: 100%;
        padding: 0;
    }

    Dashboard #sparkline-container {
        height: 100%;
        border: solid $accent;
        background: $surface;
        padding: 1 1 0 1;
        min-width: 30;
        min-height: 10;
    }

    Dashboard .sparkline-title {
        color: $accent;
        text-style: bold;
        text-align: center;
    }

    Dashboard .progress-label {
        color: $text-muted;
        text-align: center;
        padding: 1 0 0 0;
    }

    Dashboard ProgressBar {
        margin: 0 2;
    }

    Dashboard ProgressBar > .bar--bar {
        color: $success;
    }

    Dashboard ProgressBar > .bar--complete {
        color: $primary;
    }
    """

    def __init__(self, id: str = "dashboard"):
        super().__init__(id=id)
        self.tasks: List[Task] = []

    def compose(self) -> ComposeResult:
        """Compose the dashboard with 2x2 grid layout."""
        with Grid():
            with Vertical(id="sparkline-container"):
                yield Static(f"{Icons.CHART_LINE} Activity (14d)", classes="sparkline-title")
                yield Sparkline([], summary_function=max, id="sparkline-quadrant")
                yield Static("", id="progress-label", classes="progress-label")
                yield ProgressBar(total=100, show_eta=False, id="completion-progress")
            yield ClockWidget(id="clock-quadrant")
            yield StatsCard(id="stats-quadrant")
            yield PomodoroWidget(id="pomodoro-quadrant")

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

        # Update stats card
        stats_card = self.query_one("#stats-quadrant", StatsCard)
        stats_card.update_stats(total, rate, today_completed)

        # Update sparkline with completion data
        sparkline_data = self._calculate_sparkline_data(tasks)
        sparkline = self.query_one("#sparkline-quadrant", Sparkline)
        sparkline.data = sparkline_data

        # Update progress bar
        progress_bar = self.query_one("#completion-progress", ProgressBar)
        progress_bar.update(progress=rate)

        # Update progress label with rich markup
        if rate >= 75:
            label_text = f"[bold green]{Icons.CHECK_CIRCLE} {rate}% Complete - Excellent![/]"
        elif rate >= 50:
            label_text = f"[bold yellow]{Icons.TARGET} {rate}% Complete - Keep Going![/]"
        elif rate >= 25:
            label_text = f"[bold bright_magenta]{Icons.TARGET} {rate}% Complete[/]"
        else:
            label_text = f"[dim]{Icons.TARGET} {rate}% Complete[/]"

        self.query_one("#progress-label", Static).update(label_text)

    def _calculate_sparkline_data(self, tasks: List[Task]) -> List[float]:
        """Calculate daily completion counts for the last 14 days."""
        today = datetime.now().date()
        completions_by_day = defaultdict(int)

        # Count completions for each day
        for task in tasks:
            if task.completed and task.completed_at:
                try:
                    completed_date = datetime.fromisoformat(task.completed_at).date()
                    completions_by_day[completed_date] += 1
                except (ValueError, TypeError):
                    # Skip invalid dates
                    continue

        # Build list for last 14 days
        data = []
        for i in range(13, -1, -1):  # 14 days ago to today
            day = today - timedelta(days=i)
            count = completions_by_day.get(day, 0)
            data.append(float(count))

        # Return at least some data for display
        return data if data else [0.0] * 14
