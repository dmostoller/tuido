"""Productivity tabs widget combining Pomodoro timer and Weather display."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import TabbedContent, TabPane

from ..icons import Icons
from .forecast_widget import ForecastWidget
from .pomodoro_widget import PomodoroWidget
from .weather_widget import WeatherWidget


class ProductivityTabs(Container):
    """A tabbed container for productivity widgets (Pomodoro, Weather, and Forecast).

    Args:
        show_weather: If True, show Weather and Forecast tabs alongside Pomodoro.
                      If False, show only the Pomodoro timer without tabs.
    """

    DEFAULT_CSS = """
    ProductivityTabs {
        height: 100%;
        width: 100%;
        background: $background;
        border: round $accent;
        padding: 0;
        min-width: 30;
        min-height: 9;
    }

    ProductivityTabs TabbedContent {
        height: 100%;
        width: 100%;
        background: $background;
        border: none;
    }

    /* Tab styling (Tabs, Tab, TabPane) is in theme.css as #productivity-quadrant for consistency */

    /* Remove borders from child widgets since container has border */
    ProductivityTabs PomodoroWidget {
        border: none;
        background: $background;
    }

    ProductivityTabs WeatherWidget {
        border: none;
        background: $background;
    }

    ProductivityTabs ForecastWidget {
        border: none;
        background: $background;
    }
    """

    def __init__(self, show_weather: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.show_weather = show_weather

    def compose(self) -> ComposeResult:
        """Compose the tabbed productivity widget."""
        if self.show_weather:
            # Show all tabs: Weather, Forecast, Pomodoro
            with TabbedContent(initial="weather-tab"):
                with TabPane(f"{Icons.CLOUD_SUN} Weather", id="weather-tab"):
                    yield WeatherWidget()
                with TabPane(f"{Icons.CALENDAR} Forecast", id="forecast-tab"):
                    yield ForecastWidget()
                with TabPane(f"{Icons.TOMATO} Pomodoro", id="pomodoro-tab"):
                    yield PomodoroWidget()
        else:
            # Weather disabled: Just show Pomodoro timer without tabs
            yield PomodoroWidget()
