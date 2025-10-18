"""Pomodoro timer widget for productivity tracking."""

from __future__ import annotations

from enum import Enum

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Static


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
        border: solid $accent;
        background: $surface;
        padding: 1;
    }

    PomodoroWidget .pomo-title {
        color: $accent;
        text-style: bold;
        text-align: center;
    }

    PomodoroWidget .pomo-state {
        color: $text-muted;
        text-align: center;
        margin-top: 1;
    }

    PomodoroWidget .pomo-timer {
        color: $primary;
        text-style: bold;
        text-align: center;
        margin-top: 1;
    }

    PomodoroWidget .pomo-sessions {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }

    PomodoroWidget .pomo-controls {
        layout: horizontal;
        height: auto;
        align: center middle;
        margin-top: 1;
    }

    PomodoroWidget Button {
        margin: 0 1;
        min-width: 8;
    }
    """

    # Durations in seconds
    WORK_DURATION = 25 * 60  # 25 minutes
    SHORT_BREAK_DURATION = 5 * 60  # 5 minutes
    LONG_BREAK_DURATION = 15 * 60  # 15 minutes

    def __init__(self, id: str = None):
        super().__init__(id=id)
        self.pomo_state = PomodoroState.IDLE
        self.time_remaining = 0
        self.timer_running = False
        self.sessions_completed = 0
        self.timer_interval = None

    def compose(self) -> ComposeResult:
        """Compose the pomodoro widget."""
        with Vertical():
            yield Static("🍅 Pomodoro", classes="pomo-title")
            yield Static("Ready to focus", id="pomo-state", classes="pomo-state")
            yield Static("25:00", id="pomo-timer", classes="pomo-timer")
            yield Static("●○○○", id="pomo-sessions", classes="pomo-sessions")
            with Horizontal(classes="pomo-controls"):
                yield Button("Start", id="btn-pomo-start", variant="primary")
                yield Button("Reset", id="btn-pomo-reset", variant="default")

    def on_mount(self) -> None:
        """Initialize the timer."""
        self.reset_timer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-pomo-start":
            self.toggle_timer()
        elif event.button.id == "btn-pomo-reset":
            self.reset_timer()

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
        self.time_remaining = self.WORK_DURATION
        self.query_one("#pomo-state", Static).update("🎯 Focus Time")
        self.timer_interval = self.set_interval(1.0, self.tick)

    def reset_timer(self) -> None:
        """Reset the timer to initial state."""
        self.pomo_state = PomodoroState.IDLE
        self.time_remaining = self.WORK_DURATION
        self.timer_running = False

        if self.timer_interval is not None:
            self.timer_interval.stop()
            self.timer_interval = None

        self.query_one("#pomo-state", Static).update("Ready to focus")
        self.query_one("#btn-pomo-start", Button).label = "Start"
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
        if self.pomo_state == PomodoroState.WORK:
            # Work session complete
            self.sessions_completed += 1
            self.update_sessions_display()

            # Determine break type
            if self.sessions_completed % 4 == 0:
                # Long break after 4 sessions
                self.pomo_state = PomodoroState.LONG_BREAK
                self.time_remaining = self.LONG_BREAK_DURATION
                self.query_one("#pomo-state", Static).update("☕ Long Break")
            else:
                # Short break
                self.pomo_state = PomodoroState.SHORT_BREAK
                self.time_remaining = self.SHORT_BREAK_DURATION
                self.query_one("#pomo-state", Static).update("☕ Short Break")

        elif self.pomo_state in (PomodoroState.SHORT_BREAK, PomodoroState.LONG_BREAK):
            # Break complete, back to work
            self.pomo_state = PomodoroState.WORK
            self.time_remaining = self.WORK_DURATION
            self.query_one("#pomo-state", Static).update("🎯 Focus Time")

        self.update_display()

    def update_display(self) -> None:
        """Update the timer display."""
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        self.query_one("#pomo-timer", Static).update(time_str)

    def update_sessions_display(self) -> None:
        """Update the session indicator."""
        completed_in_cycle = self.sessions_completed % 4
        dots = "●" * completed_in_cycle + "○" * (4 - completed_in_cycle)
        self.query_one("#pomo-sessions", Static).update(dots)
