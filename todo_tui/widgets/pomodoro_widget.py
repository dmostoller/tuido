"""Pomodoro timer widget for productivity tracking."""

from __future__ import annotations

from enum import Enum

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, Digits, Static

from ..icons import Icons


class PomodoroState(Enum):
    """Pomodoro timer states."""

    IDLE = "idle"
    WORK = "work"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"


class PomodoroWidget(Container):
    """A pomodoro timer for focused work sessions."""

    DEFAULT_CSS = """
    PomodoroWidget {
        height: 100%;
        width: 100%;
        border: round $accent;
        background: $background;
        padding: 0 1 1 1;
        min-width: 30;
        min-height: 8;
    }

    PomodoroWidget .pomo-header {
        layout: horizontal;
        height: 1;
        width: 100%;
    }

    PomodoroWidget .pomo-title {
        color: $accent;
        text-style: bold;
        text-align: left;
        width: auto;
    }

    PomodoroWidget .pomo-state {
        color: $text-muted;
        text-align: left;
        width: 1fr;
        margin-left: 1;
    }

    PomodoroWidget Digits {
        color: $accent;
        width: 100%;
        height: 3;
        text-style: bold;
        text-align: center;
    }

    PomodoroWidget .pomo-sessions {
        text-align: right;
        color: $text-muted;
        width: auto;
        content-align: right middle;
    }

    PomodoroWidget .pomo-controls {
        layout: horizontal;
        height: auto;
        align: center middle;
    }

    PomodoroWidget Button {
        margin: 0 1;
        min-width: 8;
    }
    """

    def __init__(self, id: str = None):
        super().__init__(id=id)
        self.pomo_state = PomodoroState.IDLE
        self.time_remaining = 0
        self.timer_running = False
        self.sessions_completed = 0
        self.timer_interval = None

    def _get_durations_from_settings(self) -> tuple[int, int, int]:
        """Get pomodoro durations from app settings.

        Returns:
            Tuple of (work_duration, short_break_duration, long_break_duration) in seconds
        """
        # Default durations if settings not available
        default_work = 25 * 60
        default_short_break = 5 * 60
        default_long_break = 15 * 60

        try:
            settings = self.app.settings
            if settings is None:
                return (default_work, default_short_break, default_long_break)

            return (
                settings.pomodoro_work_minutes * 60,
                settings.pomodoro_short_break_minutes * 60,
                settings.pomodoro_long_break_minutes * 60,
            )
        except AttributeError:
            # App or settings not available yet
            return (default_work, default_short_break, default_long_break)

    def compose(self) -> ComposeResult:
        """Compose the pomodoro widget."""
        with Horizontal(classes="pomo-header"):
            yield Static(f"{Icons.TOMATO}", id="pomo-icon", classes="pomo-title")
            yield Static("Ready to focus", id="pomo-state", classes="pomo-state")
            yield Static("●○○○", id="pomo-sessions", classes="pomo-sessions")
        yield Digits("25:00", id="pomo-timer")
        with Horizontal(classes="pomo-controls"):
            yield Button("Start", id="btn-pomo-start", variant="primary")
            yield Button("Reset", id="btn-pomo-reset", variant="default")
            yield Button(Icons.ARROWS_H, id="btn-pomo-toggle", variant="default")

    def on_mount(self) -> None:
        """Initialize the timer."""
        self.reset_timer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-pomo-start":
            self.toggle_timer()
        elif event.button.id == "btn-pomo-reset":
            self.reset_timer()
        elif event.button.id == "btn-pomo-toggle":
            self.toggle_stage()

    def toggle_timer(self) -> None:
        """Start or pause the timer."""
        if self.timer_running:
            # Pause
            self.timer_running = False
            if self.timer_interval is not None:
                self.timer_interval.pause()
            self.query_one("#btn-pomo-start", Button).label = "Start"
        else:
            # Start
            self.timer_running = True
            if self.pomo_state == PomodoroState.IDLE:
                self.start_work_session()
            else:
                if self.timer_interval is None:
                    self.timer_interval = self.set_interval(1.0, self.tick)
                else:
                    self.timer_interval.resume()
            self.query_one("#btn-pomo-start", Button).label = "Pause"

    def start_work_session(self) -> None:
        """Start a work session."""
        self.pomo_state = PomodoroState.WORK
        work_duration, _, _ = self._get_durations_from_settings()
        self.time_remaining = work_duration
        self.query_one("#pomo-icon", Static).update(Icons.TARGET)
        self.query_one("#pomo-state", Static).update("Focus Time")
        self.timer_interval = self.set_interval(1.0, self.tick)

    def reset_timer(self) -> None:
        """Reset the timer to initial state."""
        self.pomo_state = PomodoroState.IDLE
        work_duration, _, _ = self._get_durations_from_settings()
        self.time_remaining = work_duration
        self.timer_running = False

        if self.timer_interval is not None:
            self.timer_interval.stop()
            self.timer_interval = None

        self.query_one("#pomo-icon", Static).update(Icons.TOMATO)
        self.query_one("#pomo-state", Static).update("Ready to focus")
        self.query_one("#btn-pomo-start", Button).label = "Start"
        self.query_one("#btn-pomo-toggle", Button).label = Icons.ARROWS_H
        self.update_display()

    def toggle_stage(self) -> None:
        """Manually toggle between work and break stages."""
        work_duration, short_break_duration, _ = self._get_durations_from_settings()

        # Pause the timer if it's running
        if self.timer_running:
            self.timer_running = False
            if self.timer_interval is not None:
                self.timer_interval.pause()
            self.query_one("#btn-pomo-start", Button).label = "Start"

        # Toggle between WORK and SHORT_BREAK
        if self.pomo_state in (PomodoroState.WORK, PomodoroState.IDLE):
            # Switch to break
            self.pomo_state = PomodoroState.SHORT_BREAK
            self.time_remaining = short_break_duration
            self.query_one("#pomo-icon", Static).update(Icons.COFFEE)
            self.query_one("#pomo-state", Static).update("Short Break")
        else:
            # Switch to work
            self.pomo_state = PomodoroState.WORK
            self.time_remaining = work_duration
            self.query_one("#pomo-icon", Static).update(Icons.TARGET)
            self.query_one("#pomo-state", Static).update("Focus Time")

        self.update_display()

    def tick(self) -> None:
        """Decrement timer by one second."""
        if self.time_remaining > 0:
            self.time_remaining -= 1
            self.update_display()
        else:
            # Timer completed
            self.on_timer_complete()

    def on_timer_complete(self) -> None:
        """Handle timer completion."""
        work_duration, short_break_duration, _ = self._get_durations_from_settings()

        if self.pomo_state == PomodoroState.WORK:
            # Work session complete - take a short break
            self.sessions_completed += 1
            self.update_sessions_display()

            self.pomo_state = PomodoroState.SHORT_BREAK
            self.time_remaining = short_break_duration
            self.query_one("#pomo-icon", Static).update(Icons.COFFEE)
            self.query_one("#pomo-state", Static).update("Short Break")

        elif self.pomo_state == PomodoroState.SHORT_BREAK:
            # Break complete, back to work
            self.pomo_state = PomodoroState.WORK
            self.time_remaining = work_duration
            self.query_one("#pomo-icon", Static).update(Icons.TARGET)
            self.query_one("#pomo-state", Static).update("Focus Time")

        self.update_display()

    def update_display(self) -> None:
        """Update the timer display."""
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        self.query_one("#pomo-timer", Digits).update(time_str)

    def update_sessions_display(self) -> None:
        """Update the session indicator."""
        completed_in_cycle = self.sessions_completed % 4
        dots = "●" * completed_in_cycle + "○" * (4 - completed_in_cycle)
        self.query_one("#pomo-sessions", Static).update(dots)
