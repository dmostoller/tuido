"""Dashboard widget showing metrics and statistics."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Optional

from textual.app import ComposeResult
from textual.color import Gradient
from textual.containers import Container, Grid, Vertical
from textual.theme import Theme
from textual.widgets import ProgressBar, Sparkline, Static

from ..icons import Icons
from ..models import Task
from ..themes import ALL_THEMES
from .clock_widget import ClockWidget
from .productivity_tabs import ProductivityTabs
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
        grid-rows: 8fr 12fr;
        grid-gutter: 0;
        height: 100%;
        padding: 0;
    }

    Dashboard #sparkline-container {
        height: 100%;
        width: 100%;
        border: round $panel;
        border-title-align: left;
        border-title-color: $accent-lighten-1;
        background: $background;
        padding: 0 1 0 1;
        min-width: 30;
        min-height: 10;
    }

    Dashboard .progress-label {
        color: $text-muted;
        text-align: center;
        padding: 1 0 0 0;
    }

    Dashboard ProgressBar {
        width: 100%;
        margin: 0 0;
    }

    Dashboard ProgressBar > Bar {
        width: 1fr;
    }

    /* Gradient colors are set programmatically via gradient property */
    /* Dashboard ProgressBar > .bar--bar {
        color: $success;
    }

    Dashboard ProgressBar > .bar--complete {
        color: $primary;
    } */
    """

    def __init__(self, id: str = "dashboard", show_weather: bool = True):
        super().__init__(id=id)
        self.tasks: List[Task] = []
        self.show_weather = show_weather

    def compose(self) -> ComposeResult:
        """Compose the dashboard with 2x2 grid layout."""
        with Grid():
            with Vertical(id="sparkline-container"):
                yield Sparkline([], summary_function=max, id="sparkline-quadrant")
                yield Static("", id="progress-label", classes="progress-label")
                yield ProgressBar(total=100, show_eta=False, id="completion-progress")
            yield ClockWidget(id="clock-quadrant")
            yield ProductivityTabs(
                id="productivity-quadrant", show_weather=self.show_weather
            )
            yield StatsCard(id="stats-quadrant")

    def on_mount(self) -> None:
        """Set up border title for sparkline container."""
        sparkline_container = self.query_one("#sparkline-container")
        sparkline_container.border_title = f"{Icons.CHART_LINE} Activity (14d)"

    def _get_current_theme(self) -> Optional[Theme]:
        """Get the current Theme object from ALL_THEMES.

        Returns:
            Theme: The current theme object, or the first theme as fallback.
                   Returns None if ALL_THEMES is empty.
        """
        theme_name = self.app.theme  # String like "catppuccin-mocha"
        for theme in ALL_THEMES:
            if theme.name == theme_name:
                return theme
        # Fallback to first theme if not found
        return ALL_THEMES[0] if ALL_THEMES else None

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

        # Update sparkline with completion data and subtle animation
        sparkline_data = self._calculate_sparkline_data(tasks)
        sparkline = self.query_one("#sparkline-quadrant", Sparkline)
        sparkline.data = sparkline_data

        # Subtle fade animation on sparkline update
        sparkline.styles.animate(
            "opacity",
            value=0.85,
            duration=0.2,
            easing="out_cubic",
            on_complete=lambda: sparkline.styles.animate(
                "opacity", value=1.0, duration=0.2, easing="in_cubic"
            ),
        )

        # Get theme object and extract colors for gradient and progress label
        theme = self._get_current_theme()

        # Defensive: handle case where themes failed to load
        if theme is None:
            # Log error - this should never happen in production
            self.app.log.warning("No themes available, using fallback colors")
            # Use sensible hex color fallbacks (Catppuccin Mocha defaults)
            primary_color = "#89b4fa"  # Blue
            accent_color = "#fab387"  # Peach
            secondary_color = "#cba6f7"  # Mauve
        else:
            primary_color = theme.primary
            accent_color = theme.accent
            secondary_color = theme.secondary

        # Update progress bar with animation and gradient
        progress_bar = self.query_one("#completion-progress", ProgressBar)
        progress_bar.update(progress=rate)

        # Create gradient: accent → secondary → primary (even transition)
        if theme is None:
            # Fallback hex colors
            gradient = Gradient.from_colors(
                "#fab387",  # Accent (peach) - 0%
                "#cba6f7",  # Secondary (mauve) - 50%
                "#89b4fa",  # Primary (blue) - 100%
                quality=100,
            )
        else:
            # Use theme colors for gradient
            gradient = Gradient.from_colors(
                accent_color,  # 0% - Starting color
                secondary_color,  # 50% - Middle transition
                primary_color,  # 100% - End color
                quality=100,
            )

        progress_bar.gradient = gradient

        # Animate progress bar container for visual feedback
        progress_bar.styles.animate(
            "opacity",
            value=0.8,
            duration=0.3,
            easing="in_out_cubic",
            on_complete=lambda: progress_bar.styles.animate(
                "opacity", value=1.0, duration=0.3, easing="in_out_cubic"
            ),
        )

        # Update progress label with rich markup using theme colors
        if rate >= 75:
            label_text = f"[bold {primary_color}]{Icons.CHECK_CIRCLE} {rate}% Complete - Excellent![/]"
        elif rate >= 50:
            label_text = (
                f"[bold {accent_color}]{Icons.TARGET} {rate}% Complete - Keep Going![/]"
            )
        elif rate >= 25:
            label_text = f"[bold {secondary_color}]{Icons.TARGET} {rate}% Complete[/]"
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
