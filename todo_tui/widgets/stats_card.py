"""Compact stats card widget for dashboard."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static


class StatsCard(Container):
    """A compact card displaying key task statistics."""

    DEFAULT_CSS = """
    StatsCard {
        height: 100%;
        width: 100%;
        border: solid $accent;
        background: $surface;
        padding: 1;
    }

    StatsCard .stats-title {
        color: $accent;
        text-style: bold;
    }

    StatsCard .stat-row {
        height: auto;
        margin-top: 1;
    }

    StatsCard .stat-large {
        color: $primary;
        text-style: bold;
    }

    StatsCard .stat-label {
        color: $text-muted;
    }
    """

    def __init__(self, id: str = None):
        super().__init__(id=id)
        self.total_tasks = 0
        self.completion_rate = 0
        self.today_count = 0

    def compose(self) -> ComposeResult:
        """Compose the stats card."""
        yield Static("📊 Overview", classes="stats-title")
        yield Static("", id="stat-total", classes="stat-row")
        yield Static("", id="stat-rate", classes="stat-row")
        yield Static("", id="stat-today", classes="stat-row")

    def update_stats(self, total: int, rate: int, today: int) -> None:
        """Update the statistics display."""
        self.total_tasks = total
        self.completion_rate = rate
        self.today_count = today

        # Update displays with formatted text
        total_text = f"[bold]{total}[/bold] tasks"
        rate_text = f"[bold]{rate}%[/bold] complete"
        today_text = f"[bold]{today}[/bold] today"

        self.query_one("#stat-total", Static).update(total_text)
        self.query_one("#stat-rate", Static).update(rate_text)
        self.query_one("#stat-today", Static).update(today_text)
