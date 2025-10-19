# Settings Feature Implementation Plan

## Overview

Add a user-friendly settings dialog to configure application preferences with persistent storage. The settings will be accessible via the `,` (comma) keybinding.

## Core Settings (3 total)

1. **Theme Selection** - Choose from 7 available themes with immediate preview
2. **Nerd Fonts Display** - Enable/disable icon rendering (replaces env var approach)
3. **Show Completed Tasks** - Toggle visibility of completed tasks in lists

## Implementation Steps

### 1. Create Settings Model

**File:** `todo_tui/models.py`

Add a `Settings` dataclass:

```python
@dataclass
class Settings:
    """Application settings."""
    theme: str = "catppuccin-mocha"  # Default theme
    nerd_fonts_enabled: bool = True
    show_completed_tasks: bool = True

    def to_dict(self) -> dict:
        """Convert settings to dictionary."""
        return {
            "theme": self.theme,
            "nerd_fonts_enabled": self.nerd_fonts_enabled,
            "show_completed_tasks": self.show_completed_tasks,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Settings:
        """Create settings from dictionary."""
        return cls(
            theme=data.get("theme", "catppuccin-mocha"),
            nerd_fonts_enabled=data.get("nerd_fonts_enabled", True),
            show_completed_tasks=data.get("show_completed_tasks", True),
        )
```

### 2. Extend StorageManager

**File:** `todo_tui/storage.py`

Add settings file path in `__init__()`:
```python
self.settings_file = self.data_dir / "settings.json"
```

Add methods:
```python
def load_settings(self) -> Settings:
    """Load application settings."""
    if not self.settings_file.exists():
        # Return defaults if no settings file
        return Settings()

    data = self._load_json(self.settings_file)
    return Settings.from_dict(data)

def save_settings(self, settings: Settings) -> None:
    """Save application settings."""
    self._save_json(self.settings_file, settings.to_dict())
```

### 3. Create SettingsDialog

**File:** `todo_tui/widgets/dialogs.py`

Add new dialog class:

```python
class SettingsDialog(ModalScreen):
    """Modal dialog for application settings."""

    DEFAULT_CSS = """
    SettingsDialog {
        align: center middle;
    }

    #dialog-container {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }

    #dialog-buttons {
        height: auto;
        layout: horizontal;
        align: center middle;
    }

    .setting-row {
        height: auto;
        margin: 1 0;
    }
    """

    def __init__(self, current_settings: Settings, available_themes: List[str]):
        super().__init__()
        self.settings = current_settings
        self.available_themes = available_themes

    def compose(self) -> ComposeResult:
        """Compose the settings dialog."""
        with Container(id="dialog-container"):
            yield Label(f"{Icons.COG} Settings", classes="header")

            # Theme selection
            yield Label("Theme:")
            theme_options = [(name, name) for name in self.available_themes]
            yield Select(
                options=theme_options,
                value=self.settings.theme,
                id="theme-select"
            )

            # Nerd Fonts toggle
            yield Label("Enable Nerd Font Icons:")
            yield Switch(value=self.settings.nerd_fonts_enabled, id="nerd-fonts-switch")

            # Show completed tasks toggle
            yield Label("Show Completed Tasks:")
            yield Switch(value=self.settings.show_completed_tasks, id="show-completed-switch")

            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", id="btn-cancel", variant="default")
                yield Button("Save", id="btn-save", variant="success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            # Read current values
            theme_select = self.query_one("#theme-select", Select)
            nerd_fonts_switch = self.query_one("#nerd-fonts-switch", Switch)
            show_completed_switch = self.query_one("#show-completed-switch", Switch)

            # Update settings
            self.settings.theme = theme_select.value
            self.settings.nerd_fonts_enabled = nerd_fonts_switch.value
            self.settings.show_completed_tasks = show_completed_switch.value

            self.dismiss(self.settings)

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape":
            self.dismiss(None)
            event.prevent_default()
```

Don't forget to import `Switch` from textual.widgets at the top of the file.

### 4. Wire Up to TodoApp

**File:** `todo_tui/app.py`

**Add to imports:**
```python
from textual.widgets import Footer, Header, Switch  # Add Switch
from .widgets.dialogs import (
    # ... existing imports ...
    SettingsDialog,  # Add this
)
```

**Add to BINDINGS:**
```python
BINDINGS = [
    # ... existing bindings ...
    Binding(",", "settings", "Settings"),
]
```

**Add settings instance variable in `__init__()`:**
```python
def __init__(self):
    super().__init__()
    self.storage = StorageManager()
    self.settings = None  # Will be loaded in on_mount
    # ... rest of init
```

**Load and apply settings in `on_mount()`:**
```python
def on_mount(self) -> None:
    """Initialize the application on mount."""
    self.title = "Tuido"
    self.sub_title = "Terminal Task Manager"

    # Load settings
    self.settings = self.storage.load_settings()

    # Register custom themes
    for theme in ALL_THEMES:
        self.register_theme(theme)

    # Apply saved theme
    self.theme = self.settings.theme

    # Apply Nerd Fonts setting to Icons module
    import todo_tui.icons as icons
    icons.NERD_FONTS_ENABLED = self.settings.nerd_fonts_enabled

    # ... rest of on_mount
```

**Add settings action:**
```python
def action_settings(self) -> None:
    """Show settings dialog."""
    # Get list of available theme names
    theme_names = [theme.name for theme in ALL_THEMES]

    def check_settings(result: Optional[Settings]) -> None:
        """Callback when dialog is dismissed."""
        if result:
            # Save settings
            self.storage.save_settings(result)
            self.settings = result

            # Apply theme change
            self.theme = result.theme

            # Apply Nerd Fonts change
            import todo_tui.icons as icons
            icons.NERD_FONTS_ENABLED = result.nerd_fonts_enabled

            # Refresh UI to apply icon changes
            self.refresh()

            # Reload task list if show_completed_tasks changed
            if self.current_project_id is None:
                self._load_all_tasks()
            else:
                self._load_project_tasks(self.current_project_id)

    self.push_screen(
        SettingsDialog(self.settings, theme_names),
        check_settings
    )
```

### 5. Update Icons Module (Optional Enhancement)

**File:** `todo_tui/icons.py`

Make the `NERD_FONTS_ENABLED` variable mutable and check it dynamically:

```python
# At the top of the file, change from reading env var once to using a global
NERD_FONTS_ENABLED = os.getenv("NERD_FONTS_ENABLED", "1") == "1"

# Then the Icons class can reference this global
class Icons:
    """Icon definitions with Nerd Font and ASCII fallbacks."""

    @staticmethod
    def _get_icon(nerd: str, ascii_fallback: str) -> str:
        """Get icon based on current NERD_FONTS_ENABLED setting."""
        return nerd if NERD_FONTS_ENABLED else ascii_fallback

    # Change all icon definitions to use the dynamic method
    CHECK = property(lambda self: Icons._get_icon("", "[x]"))
    # ... etc for all icons
```

### 6. Filter Completed Tasks (Task List)

**File:** `todo_tui/widgets/task_list.py`

Modify `set_tasks()` method to respect the setting:

```python
def set_tasks(self, tasks: List[Task], show_completed: bool = True) -> None:
    """Set the tasks to display."""
    # Filter out completed tasks if setting is disabled
    if not show_completed:
        tasks = [t for t in tasks if not t.completed]

    self.tasks = tasks
    self._refresh_list()
```

Update calls in `app.py` to pass the setting:
```python
task_panel.set_tasks(all_tasks, self.settings.show_completed_tasks)
```

## File Structure

New/Modified files:
- `todo_tui/models.py` - Add `Settings` dataclass
- `todo_tui/storage.py` - Add settings load/save methods
- `todo_tui/widgets/dialogs.py` - Add `SettingsDialog` class
- `todo_tui/app.py` - Wire up settings system
- `~/.local/share/tuido/settings.json` - Created on first save (auto-managed)

## Testing Checklist

- [ ] Settings dialog opens with `,` keybinding
- [ ] Theme changes apply immediately when saved
- [ ] Nerd Fonts toggle works (icons appear/disappear)
- [ ] Show completed tasks toggle filters task list
- [ ] Settings persist after app restart
- [ ] Default settings work for new users (no settings file)
- [ ] All 7 themes selectable and functional
- [ ] Cancel button discards changes
- [ ] Escape key closes dialog without saving

## Future Enhancements (Not in Scope)

- Default project selection for new tasks
- Pomodoro timer duration customization
- Task sort order preferences
- Confirm-on-delete toggle
- Auto-save interval settings
- Dashboard widget visibility toggles

---

**Implementation Priority:** Medium
**Estimated Complexity:** Low-Medium
**Dependencies:** None (uses existing dialog patterns)
