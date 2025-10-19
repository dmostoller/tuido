"""Weather widget displaying current conditions."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Digits, Static

from ..icons import Icons


class WeatherWidget(Container):
    """A widget displaying current weather conditions."""

    DEFAULT_CSS = """
    WeatherWidget {
        height: 100%;
        width: 100%;
        border: solid $accent;
        background: $surface;
        padding: 0 1 1 1;
        min-width: 30;
        min-height: 9;
    }

    WeatherWidget .weather-header {
        layout: horizontal;
        height: auto;
        width: 100%;
    }

    WeatherWidget .weather-title {
        color: $accent;
        text-style: bold;
        text-align: left;
        width: 1fr;
    }

    WeatherWidget .weather-location {
        color: $text-muted;
        text-align: right;
        width: auto;
        content-align: right middle;
    }

    WeatherWidget .weather-main-display {
        layout: horizontal;
        height: auto;
        align: center middle;
        width: 100%;
        padding: 1 0;
    }

    WeatherWidget Digits {
        color: $primary;
        width: auto;
        height: 3;
        text-style: bold;
        text-align: center;
    }

    WeatherWidget .weather-icon-large {
        color: $primary;
        text-style: bold;
        content-align: center middle;
        width: auto;
        padding: 0 2;
    }

    WeatherWidget .weather-footer {
        layout: horizontal;
        height: auto;
        width: 100%;
    }

    WeatherWidget .weather-condition {
        color: $text-muted;
        text-align: left;
        width: 1fr;
    }

    WeatherWidget .weather-details {
        color: $text-muted;
        text-align: right;
        width: auto;
    }
    """

    def __init__(self, id: str = None):
        super().__init__(id=id)
        self.weather_data: Optional[dict] = None
        self.last_updated: Optional[datetime] = None
        self.update_interval = None
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "")
        self.location = os.getenv("WEATHER_LOCATION", "")
        self.use_fahrenheit = os.getenv("WEATHER_UNIT", "F") == "F"

    def compose(self) -> ComposeResult:
        """Compose the weather widget."""
        with Horizontal(classes="weather-header"):
            yield Static(f"{Icons.CLOUD_SUN} Weather", classes="weather-title")
            yield Static("--", id="weather-location", classes="weather-location")

        # Main display: Large temperature Digits + Large weather icon
        with Horizontal(classes="weather-main-display"):
            yield Digits("--°", id="weather-temp")
            yield Static(Icons.CLOUD, id="weather-icon-large", classes="weather-icon-large")

        # Footer: Condition (left) + Details (right)
        with Horizontal(classes="weather-footer"):
            yield Static("Loading...", id="weather-condition", classes="weather-condition")
            yield Static("", id="weather-details", classes="weather-details")

    def on_mount(self) -> None:
        """Initialize the weather widget."""
        # Set up automatic updates every 30 minutes
        self.update_interval = self.set_interval(1800.0, self.fetch_weather)
        # Fetch weather immediately
        self.fetch_weather()

    def fetch_weather(self) -> None:
        """Fetch weather data from OpenWeatherMap API."""
        # TODO(human): Implement API call to OpenWeatherMap
        # For now, display placeholder data
        if not self.api_key or not self.location:
            self._display_no_config()
            return

        try:
            import requests

            # Determine units
            units = "imperial" if self.use_fahrenheit else "metric"
            temp_symbol = "°F" if self.use_fahrenheit else "°C"

            # Build API URL
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": self.location,
                "appid": self.api_key,
                "units": units,
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            self.weather_data = data
            self.last_updated = datetime.now()

            # Extract data
            temp = int(data["main"]["temp"])
            condition = data["weather"][0]["main"]
            description = data["weather"][0]["description"].title()
            humidity = data["main"]["humidity"]
            wind_speed = int(data["wind"]["speed"])
            city_name = data["name"]

            # Update display
            self._update_display(
                temp=temp,
                temp_symbol=temp_symbol,
                condition=condition,
                description=description,
                humidity=humidity,
                wind_speed=wind_speed,
                city_name=city_name,
            )

        except ImportError:
            self._display_error("Install 'requests' library")
        except requests.exceptions.RequestException as e:
            self._display_error(f"API Error: {str(e)[:20]}")
        except Exception as e:
            self._display_error(f"Error: {str(e)[:20]}")

    def _update_display(
        self,
        temp: int,
        temp_symbol: str,
        condition: str,
        description: str,
        humidity: int,
        wind_speed: int,
        city_name: str,
    ) -> None:
        """Update the widget display with weather data."""
        # Update location
        self.query_one("#weather-location", Static).update(city_name)

        # Update icon based on condition
        icon = self._get_weather_icon(condition)
        self.query_one("#weather-icon-large", Static).update(icon)

        # Update temperature in Digits
        self.query_one("#weather-temp", Digits).update(f"{temp}{temp_symbol}")

        # Update condition
        self.query_one("#weather-condition", Static).update(description)

        # Update details
        details = f"{Icons.WIND} {wind_speed}mph • 💧{humidity}%"
        self.query_one("#weather-details", Static).update(details)

    def _display_no_config(self) -> None:
        """Display message when API key or location is not configured."""
        self.query_one("#weather-location", Static).update("Not Set")
        self.query_one("#weather-icon-large", Static).update(Icons.QUESTION)
        self.query_one("#weather-temp", Digits).update("--°")
        self.query_one("#weather-condition", Static).update("Not Configured")
        self.query_one("#weather-details", Static).update(
            "Set API Key"
        )

    def _display_error(self, error_msg: str) -> None:
        """Display error message."""
        self.query_one("#weather-condition", Static).update(error_msg)
        self.query_one("#weather-details", Static).update("")

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
