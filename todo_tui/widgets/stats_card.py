"""Compact stats card widget for dashboard."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static

from ..icons import Icons


class StatsCard(Container):
    """A compact card displaying key task statistics."""

    DEFAULT_CSS = """
    StatsCard {
        height: 100%;
        width: 100%;
        border: solid $accent;
        background: $surface;
        padding: 1 2;
        min-width: 30;
        min-height: 10;
    }

    StatsCard .stats-title {
        color: $accent;
        text-style: bold;
        text-align: center;
    }

    StatsCard .stat-row {
        height: auto;
        padding: 1 0;
        text-align: center;
    }

    StatsCard .stat-divider {
        color: $primary-darken-2;
        height: 1;
        padding: 0;
    }
    """

    def __init__(self, id: str = None):
        super().__init__(id=id)
        self.total_tasks = 0
        self.completion_rate = 0
        self.today_count = 0

    def compose(self) -> ComposeResult:
        """Compose the stats card."""
        # yield Static(f"{Icons.CHART_BAR} Overview", classes="stats-title")
        yield Static("", id="stat-total", classes="stat-row")
        yield Static("─" * 50, classes="stat-divider")
        yield Static("", id="stat-today", classes="stat-row")

    def on_mount(self) -> None:
        """Update display after mounting."""
        self._update_display()

    def update_stats(self, total: int, rate: int, today: int) -> None:
        """Update the statistics display."""
        self.total_tasks = total
        self.completion_rate = rate
        self.today_count = today

        # Only update the display if we're mounted
        if self.is_mounted:
            self._update_display()

    def _update_display(self) -> None:
        """Update the visual display with current stats."""
        # Primary theme color (Catppuccin Mocha blue)
        primary_color = "#89b4fa"

        # Build rich markup text with icons and colors
        # Only the numbers use the primary theme color
        total_text = f"{Icons.LIST}  [bold {primary_color}]{self.total_tasks}[/] [dim]Total Tasks[/]"
        today_text = f"{Icons.CALENDAR}  [bold {primary_color}]{self.today_count}[/] [dim]Completed Today[/]"

        self.query_one("#stat-total", Static).update(total_text)
        self.query_one("#stat-today", Static).update(today_text)
