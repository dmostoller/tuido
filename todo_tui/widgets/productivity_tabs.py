"""Productivity tabs widget combining Pomodoro timer and Weather display."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import TabPane, TabbedContent

from ..icons import Icons
from .pomodoro_widget import PomodoroWidget
from .weather_widget import WeatherWidget


class ProductivityTabs(Container):
    """A tabbed container for productivity widgets (Pomodoro and Weather)."""

    DEFAULT_CSS = """
    ProductivityTabs {
        height: 100%;
        width: 100%;
        background: $surface;
        border: solid $accent;
        padding: 0;
        min-width: 30;
        min-height: 9;
    }

    ProductivityTabs TabbedContent {
        height: 100%;
        width: 100%;
        background: $surface;
        border: none;
    }

    ProductivityTabs Tabs {
        background: $surface;
        border-bottom: solid $panel;
    }

    ProductivityTabs Tab {
        background: $surface;
        color: $text-muted;
        border: none;
        text-style: none;
    }

    ProductivityTabs Tab:hover {
        background: $panel;
        color: $foreground;
    }

    ProductivityTabs Tab.-active {
        background: $panel;
        color: $primary;
        text-style: bold;
    }

    ProductivityTabs TabPane {
        padding: 0;
        background: $surface;
    }

    /* Remove borders from child widgets since container has border */
    ProductivityTabs PomodoroWidget {
        border: none;
        background: $surface;
    }

    ProductivityTabs WeatherWidget {
        border: none;
        background: $surface;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the tabbed productivity widget."""
        with TabbedContent(initial="weather-tab"):
            with TabPane(f"{Icons.CLOUD_SUN} Weather", id="weather-tab"):
                yield WeatherWidget()
            with TabPane(f"{Icons.TOMATO} Pomodoro", id="pomodoro-tab"):
                yield PomodoroWidget()
            
