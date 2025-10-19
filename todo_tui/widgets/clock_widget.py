"""Live clock widget for dashboard."""

from __future__ import annotations

from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Digits, Static

from ..icons import Icons


class ClockWidget(Container):
    """A live updating clock display."""

    DEFAULT_CSS = """
    ClockWidget {
        height: 100%;
        width: 100%;
        border: solid $accent;
        background: $surface;
        padding: 1 1 0 1;
        align: center middle;
        min-width: 30;
        min-height: 10;
    }

    ClockWidget .clock-title {
        color: $accent;
        text-style: bold;
        text-align: center;
    }

    ClockWidget Digits {
        color: $primary;
        width: 100%;
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
        yield Static(f"{Icons.CLOCK} Time", classes="clock-title")
        yield Digits("", id="clock-time")
        yield Static("", id="clock-date", classes="clock-date")

    def on_mount(self) -> None:
        """Set up live clock updates."""
        self.update_clock()
        self.set_interval(1.0, self.update_clock)

    def update_clock(self) -> None:
        """Update the clock display."""
        now = datetime.now()

        # Format time as HH:MM:SS
        time_str = now.strftime("%H:%M:%S")

        # Format date as "Day, Mon DD YYYY"
        date_str = now.strftime("%a, %b %d %Y")

        self.query_one("#clock-time", Digits).update(time_str)
        self.query_one("#clock-date", Static).update(date_str)
