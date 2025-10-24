"""Live clock widget for dashboard."""

from __future__ import annotations

from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Digits, Static

from ..icons import Icons


class ClockWidget(Container):
    """A live updating clock display."""

    DEFAULT_CSS = """
    ClockWidget {
        height: 100%;
        width: 100%;
        border: round $accent;
        border-title-align: right;
        background: $surface;
        padding: 0;
        layout: vertical;
        align: center middle;
    }

    ClockWidget .clock-content {
        height: auto;
        width: auto;
    }

    ClockWidget .clock-timezone {
        color: $text-muted;
        text-align: center;
        text-style: italic;
    }

    ClockWidget Digits {
        color: $primary;
        height: auto;
        text-style: bold;
        text-align: center;
    }

    ClockWidget .clock-date {
        color: $text-muted;
        text-align: center;
    }
    """

    def __init__(self, id: str = None):
        super().__init__(id=id)

    def compose(self) -> ComposeResult:
        """Compose the clock widget."""
        with Vertical(classes="clock-content"):
            yield Static("", id="clock-timezone", classes="clock-timezone")
            yield Digits("", id="clock-time")
            yield Static("", id="clock-date", classes="clock-date")

    def on_mount(self) -> None:
        """Set up live clock updates."""
        self.border_title = f"{Icons.CLOCK} Time"
        self.update_clock()
        self.set_interval(1.0, self.update_clock)

    def update_clock(self) -> None:
        """Update the clock display."""
        now = datetime.now()

        # Get timezone info
        tz_name = now.astimezone().tzname()
        utc_offset = now.astimezone().utcoffset()
        if utc_offset:
            total_seconds = int(utc_offset.total_seconds())
            hours = total_seconds // 3600
            minutes = abs(total_seconds % 3600) // 60
            offset_str = f"{hours:+d}:{minutes:02d}"
        else:
            offset_str = "+0:00"
        timezone_str = f"{tz_name} - UTC{offset_str}"

        # Format time as HH:MM:SS
        time_str = now.strftime("%H:%M:%S")

        # Format date as "Day, Mon DD YYYY"
        date_str = now.strftime("%a, %b %d %Y")

        self.query_one("#clock-timezone", Static).update(timezone_str)
        self.query_one("#clock-time", Digits).update(time_str)
        self.query_one("#clock-date", Static).update(date_str)
