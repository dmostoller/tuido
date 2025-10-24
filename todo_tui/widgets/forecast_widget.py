"""5-day weather forecast widget displaying daily predictions."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static

from ..icons import Icons


class ForecastWidget(Container):
    """A widget displaying 5-day weather forecast."""

    DEFAULT_CSS = """
    ForecastWidget {
        height: 100%;
        width: 100%;
        border: round $accent;
        background: $surface;
        padding: 0 1 1 1;
        min-width: 30;
        min-height: 11;
    }

    ForecastWidget .forecast-header {
        layout: horizontal;
        height: auto;
        width: 100%;
        padding: 0 0 1 0;
    }

    ForecastWidget .forecast-title {
        color: $accent;
        text-style: bold;
        text-align: left;
        width: 1fr;
    }

    ForecastWidget .forecast-location {
        color: $text-muted;
        text-align: right;
        width: auto;
        content-align: right middle;
    }

    ForecastWidget .forecast-grid {
        layout: horizontal;
        height: auto;
        width: 100%;
    }

    ForecastWidget .day-card {
        layout: vertical;
        width: 1fr;
        height: auto;
        align: center top;
    }

    ForecastWidget .day-name {
        color: $accent;
        text-style: bold;
        text-align: center;
        width: 100%;
    }

    ForecastWidget .day-icon {
        color: $primary;
        text-style: bold;
        text-align: center;
        width: 100%;
        padding: 1 0 0 0;
    }

    ForecastWidget .day-temp-high {
        color: $primary;
        text-style: bold;
        text-align: center;
        width: 100%;
        padding: 1 0 0 0;
    }

    ForecastWidget .day-temp-low {
        color: $text-muted;
        text-align: center;
        width: 100%;
    }

    ForecastWidget .day-description {
        color: $text-muted;
        text-align: center;
        width: 100%;
        padding: 1 0 0 0;
    }
    """

    def __init__(self, id: str = None):
        super().__init__(id=id)
        self.forecast_data: Optional[dict] = None
        self.last_updated: Optional[datetime] = None
        self.update_interval = None
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "")
        # Location and unit will be loaded from settings
        self.location = "Philadelphia, US"
        self.use_fahrenheit = True

    def compose(self) -> ComposeResult:
        """Compose the forecast widget."""
        # Header
        with Horizontal(classes="forecast-header"):
            yield Static(f"{Icons.CALENDAR} 5-Day Forecast", classes="forecast-title")
            yield Static("--", id="forecast-location", classes="forecast-location")

        # 5-day grid
        with Horizontal(classes="forecast-grid"):
            # Day 1
            with Vertical(classes="day-card"):
                yield Static("--", id="day-0-name", classes="day-name")
                yield Static(Icons.CLOUD, id="day-0-icon", classes="day-icon")
                yield Static("--°", id="day-0-high", classes="day-temp-high")
                yield Static("--°", id="day-0-low", classes="day-temp-low")
                yield Static("Loading...", id="day-0-desc", classes="day-description")

            # Day 2
            with Vertical(classes="day-card"):
                yield Static("--", id="day-1-name", classes="day-name")
                yield Static(Icons.CLOUD, id="day-1-icon", classes="day-icon")
                yield Static("--°", id="day-1-high", classes="day-temp-high")
                yield Static("--°", id="day-1-low", classes="day-temp-low")
                yield Static("Loading...", id="day-1-desc", classes="day-description")

            # Day 3
            with Vertical(classes="day-card"):
                yield Static("--", id="day-2-name", classes="day-name")
                yield Static(Icons.CLOUD, id="day-2-icon", classes="day-icon")
                yield Static("--°", id="day-2-high", classes="day-temp-high")
                yield Static("--°", id="day-2-low", classes="day-temp-low")
                yield Static("Loading...", id="day-2-desc", classes="day-description")

            # Day 4
            with Vertical(classes="day-card"):
                yield Static("--", id="day-3-name", classes="day-name")
                yield Static(Icons.CLOUD, id="day-3-icon", classes="day-icon")
                yield Static("--°", id="day-3-high", classes="day-temp-high")
                yield Static("--°", id="day-3-low", classes="day-temp-low")
                yield Static("Loading...", id="day-3-desc", classes="day-description")

            # Day 5
            with Vertical(classes="day-card"):
                yield Static("--", id="day-4-name", classes="day-name")
                yield Static(Icons.CLOUD, id="day-4-icon", classes="day-icon")
                yield Static("--°", id="day-4-high", classes="day-temp-high")
                yield Static("--°", id="day-4-low", classes="day-temp-low")
                yield Static("Loading...", id="day-4-desc", classes="day-description")

    def _load_settings(self) -> None:
        """Load location and temperature unit from app settings."""
        try:
            settings = self.app.settings
            if settings:
                self.location = settings.weather_location
                self.use_fahrenheit = settings.weather_use_fahrenheit
        except AttributeError:
            # Fallback to environment variables for migration/backwards compatibility
            self.location = os.getenv("WEATHER_LOCATION", "Philadelphia, US")
            self.use_fahrenheit = os.getenv("WEATHER_UNIT", "F") == "F"

    def on_mount(self) -> None:
        """Initialize the forecast widget."""
        # Load settings before fetching forecast
        self._load_settings()
        # Set up automatic updates every 30 minutes
        self.update_interval = self.set_interval(1800.0, self.fetch_forecast)
        # Fetch forecast immediately
        self.fetch_forecast()

    def refresh_forecast_settings(self) -> None:
        """Refresh forecast settings and re-fetch data.

        Call this method when settings change to immediately apply new location/unit.
        """
        self._load_settings()
        self.fetch_forecast()

    def fetch_forecast(self) -> None:
        """Fetch 5-day forecast data from OpenWeatherMap API."""
        if not self.api_key or not self.location:
            self._display_no_config()
            return

        try:
            import requests

            # Determine units
            units = "imperial" if self.use_fahrenheit else "metric"
            temp_symbol = "°F" if self.use_fahrenheit else "°C"

            # Build API URL
            url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {
                "q": self.location,
                "appid": self.api_key,
                "units": units,
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            self.forecast_data = data
            self.last_updated = datetime.now()

            # Process forecast data
            city_name = data["city"]["name"]
            daily_forecasts = self._process_forecast_data(data["list"], temp_symbol)

            # Update display
            self._update_display(city_name, daily_forecasts)

        except ImportError:
            self._display_error("Install 'requests' library")
        except requests.exceptions.RequestException as e:
            self._display_error(f"API Error: {str(e)[:20]}")
        except Exception as e:
            self._display_error(f"Error: {str(e)[:20]}")

    def _process_forecast_data(
        self, forecast_list: list, temp_symbol: str
    ) -> list[dict]:
        """Process raw forecast data into daily summaries.

        Groups 3-hour forecasts by day and calculates daily high/low temps.

        Args:
            forecast_list: List of 3-hour forecast entries from API
            temp_symbol: Temperature symbol (°F or °C)

        Returns:
            List of 5 daily forecast dictionaries
        """
        from collections import defaultdict

        # Group forecasts by date
        daily_data = defaultdict(list)

        for entry in forecast_list:
            # Parse timestamp
            dt = datetime.fromtimestamp(entry["dt"])
            date_key = dt.strftime("%Y-%m-%d")
            daily_data[date_key].append(entry)

        # Process first 5 days
        daily_forecasts = []
        for i, (date_key, entries) in enumerate(sorted(daily_data.items())[:5]):
            # Calculate high/low
            temps = [e["main"]["temp"] for e in entries]
            temp_high = int(max(temps))
            temp_low = int(min(temps))

            # Find midday entry (around 12pm) for representative weather
            midday_entry = entries[len(entries) // 2]  # Approximate midday
            condition = midday_entry["weather"][0]["main"]
            description = midday_entry["weather"][0]["description"].title()

            # Format day name
            dt = datetime.fromtimestamp(entries[0]["dt"])
            if i == 0:
                day_name = "Today"
            elif i == 1:
                day_name = "Tomorrow"
            else:
                day_name = dt.strftime("%a")  # Mon, Tue, etc.

            daily_forecasts.append(
                {
                    "day_name": day_name,
                    "icon": self._get_weather_icon(condition),
                    "temp_high": f"{temp_high}{temp_symbol}",
                    "temp_low": f"{temp_low}{temp_symbol}",
                    "description": description,
                }
            )

        # Ensure we have exactly 5 days
        while len(daily_forecasts) < 5:
            daily_forecasts.append(
                {
                    "day_name": "--",
                    "icon": Icons.CLOUD,
                    "temp_high": "--°",
                    "temp_low": "--°",
                    "description": "--",
                }
            )

        return daily_forecasts[:5]

    def _update_display(self, city_name: str, daily_forecasts: list[dict]) -> None:
        """Update the widget display with forecast data."""
        # Update location
        self.query_one("#forecast-location", Static).update(city_name)

        # Update each day card
        for i, day_data in enumerate(daily_forecasts):
            self.query_one(f"#day-{i}-name", Static).update(day_data["day_name"])
            self.query_one(f"#day-{i}-icon", Static).update(day_data["icon"])
            self.query_one(f"#day-{i}-high", Static).update(day_data["temp_high"])
            self.query_one(f"#day-{i}-low", Static).update(day_data["temp_low"])
            self.query_one(f"#day-{i}-desc", Static).update(day_data["description"])

    def _display_no_config(self) -> None:
        """Display message when API key or location is not configured."""
        self.query_one("#forecast-location", Static).update("Not Set")
        for i in range(5):
            self.query_one(f"#day-{i}-name", Static).update("--")
            self.query_one(f"#day-{i}-icon", Static).update(Icons.QUESTION)
            self.query_one(f"#day-{i}-high", Static).update("--°")
            self.query_one(f"#day-{i}-low", Static).update("--°")
            self.query_one(f"#day-{i}-desc", Static).update("Not Configured")

    def _display_error(self, error_msg: str) -> None:
        """Display error message."""
        for i in range(5):
            self.query_one(f"#day-{i}-desc", Static).update(error_msg if i == 2 else "")

    def _get_weather_icon(self, condition: str) -> str:
        """Get the appropriate icon for the weather condition.

        Returns:
            Unicode icon from Icons class
        """
        condition_lower = condition.lower()

        # Map conditions to Icons
        if "clear" in condition_lower or "sun" in condition_lower:
            return Icons.SUN
        elif "cloud" in condition_lower:
            return Icons.CLOUD
        elif "rain" in condition_lower or "drizzle" in condition_lower:
            return Icons.RAIN
        elif "snow" in condition_lower:
            return Icons.SNOW
        elif "thunder" in condition_lower or "storm" in condition_lower:
            return Icons.THUNDERSTORM
        else:
            return Icons.CLOUD_SUN
