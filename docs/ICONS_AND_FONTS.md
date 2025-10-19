# Icons and Fonts in Python TUI Applications

Research findings for replacing emojis with proper icons and using JetBrains Mono font in Textual TUI applications.

## Summary

For Python TUI apps like this one, the equivalent of lucide.dev icons is **Nerd Fonts** - specifically using JetBrains Mono Nerd Font, which combines the JetBrains Mono typeface with 3,600+ iconic glyphs.

## Font Configuration

### Key Finding: Fonts are Terminal-Level, Not App-Level

Unlike web applications where fonts can be set programmatically, **Textual applications cannot control fonts directly**. Fonts are configured through your terminal emulator settings.

### Using JetBrains Mono

1. **Install JetBrains Mono Nerd Font**
   - Download from: <https://www.nerdfonts.com/font-downloads>
   - Look for "JetBrainsMono Nerd Font"
   - This includes both the JetBrains Mono typeface AND all Nerd Font icons

2. **Configure Your Terminal**
   - **macOS Terminal.app**: Settings → Profiles → Text tab → Change font to "JetBrainsMono Nerd Font"
   - **iTerm2**: Preferences → Profiles → Text → Font
   - **WezTerm**: Already bundles JetBrains Mono by default
   - **Alacritty**: Edit `~/.config/alacritty/alacritty.yml`:

     ```yaml
     font:
       normal:
         family: "JetBrainsMono Nerd Font"
     ```

3. **Recommended Terminal Settings**
   - Character spacing: 1.0
   - Line spacing: 0.805 (adjust as needed)
   - Font size: 12-14pt for readability

## Icon Solutions

### 1. Nerd Fonts (Recommended)

**What it is**: A collection of 3,600+ icons from Font Awesome, Material Design Icons, Octicons, and more, patched into popular developer fonts.

**How it works**:

- Icons are actual font glyphs in the Unicode Private Use Area (E000-F8FF)
- Once you install a Nerd Font, you can use icons directly as Unicode characters
- No library needed - just raw Unicode strings in your Python code

**Usage in Python**:

```python
# Direct Unicode usage
ICON_CLOCK = "\uF017"       #
ICON_CHECK = "\uF00C"       #
ICON_TIMES = "\uF00D"       #
ICON_CALENDAR = "\uF073"    #
ICON_TASK = "\uF0AE"        #
ICON_PROJECT = "\uF07C"     #
ICON_STATS = "\uF080"       #
ICON_FIRE = "\uF06D"        #
ICON_TROPHY = "\uF091"      #
```

**Finding Icons**:

- Cheat Sheet: <https://www.nerdfonts.com/cheat-sheet>
- Search by keyword, copy the icon code point

**Pros**:

- No dependencies
- Huge icon library (3,600+)
- Perfect terminal rendering
- Works across all terminal emulators that support the font

**Cons**:

- Requires users to install the Nerd Font
- Icon codes are not as readable as named constants

### 2. Python Nerd Font Libraries

There are Python packages that provide named constants for Nerd Fonts:

#### Option A: Create Your Own Icons Module

```python
# todo_tui/icons.py
"""Icon constants using Nerd Font glyphs."""

class Icons:
    # Time & Clock
    CLOCK = "\uF017"          #
    TIMER = "\uF252"          #
    HOURGLASS = "\uF254"      #

    # Tasks & Todos
    CHECK = "\uF00C"          #
    CHECK_CIRCLE = "\uF058"   #
    TIMES = "\uF00D"          #
    TIMES_CIRCLE = "\uF057"   #
    SQUARE = "\uF0C8"         #
    CHECK_SQUARE = "\uF14A"   #

    # Navigation & UI
    FOLDER = "\uF07C"         #
    FOLDER_OPEN = "\uF07B"    #
    FILE = "\uF15B"           #
    LIST = "\uF03A"           #

    # Stats & Metrics
    CHART_BAR = "\uF080"      #
    CHART_LINE = "\uF201"     #
    TROPHY = "\uF091"         #
    FIRE = "\uF06D"           #
    STAR = "\uF005"           #

    # Actions
    PLUS = "\uF067"           #
    EDIT = "\uF044"           #
    TRASH = "\uF1F8"          #
    SEARCH = "\uF002"         #

    # Calendar & Date
    CALENDAR = "\uF073"       #
    CALENDAR_CHECK = "\uF274"  #
    CALENDAR_TIMES = "\uF273"  #

    # Productivity
    POMODORO = "\uF500"       #
    BELL = "\uF0F3"           #
    FLAG = "\uF024"           #
    BOOKMARK = "\uF02E"       #
```

Usage:

```python
from todo_tui.icons import Icons

Static(f"{Icons.CLOCK} Time", classes="clock-title")
```

#### Option B: Use Unicode Directly with Comments

```python
# In your widgets
ICON_CLOCK = "\uF017"    #  - For readability in code

Static(f"{ICON_CLOCK} Time", classes="clock-title")
```

### 3. Fallback for Users Without Nerd Fonts

```python
# todo_tui/icons.py
import os
import sys

def _has_nerd_font():
    """Check if terminal likely has Nerd Font support."""
    # Simple heuristic - check if we're in a known terminal
    # Real detection is complex, so we could also use env var
    return os.getenv("NERD_FONTS_ENABLED", "1") == "1"

class Icons:
    """Icon constants with fallback support."""

    if _has_nerd_font():
        CLOCK = "\uF017"
        CHECK = "\uF00C"
        TIMES = "\uF00D"
        # ... etc
    else:
        # ASCII fallbacks
        CLOCK = "[T]"
        CHECK = "[✓]"
        TIMES = "[✗]"
        # ... etc
```

## Implementation Strategy

### Step 1: Create Icons Module

Create `todo_tui/icons.py` with all Nerd Font icon constants needed for your app.

### Step 2: Replace Emojis

Find all emoji usage in the codebase:

- `clock_widget.py` - Line 50: `"🕐 Time"`
- `dialogs.py` - Various emojis in UI
- `pomodoro_widget.py` - Timer emojis
- `stats_card.py` - Metric emojis
- `dashboard.py` - Dashboard emojis
- `task_detail.py` - Action emojis
- `task_list.py` - Task status emojis

Replace with Nerd Font icons using the Icons constants.

### Step 3: Update Documentation

- Add Nerd Font requirement to README.md
- Document how to install JetBrains Mono Nerd Font
- Add note about terminal configuration

### Step 4: Test

Test with and without Nerd Font to ensure fallbacks work (if implemented).

## Recommended Icon Mappings

Based on the current emoji usage in the codebase:

| Current Emoji | Nerd Font Icon | Code Point | Description |
|--------------|----------------|------------|-------------|
| 🕐 | `` | `\uF017` | Clock/Time |
| 📊 | `` | `\uF080` | Statistics/Charts |
| ✓ | `` | `\uF00C` | Check/Complete |
| ✗ | `` | `\uF00D` | Times/Incomplete |
| ❌ | `` | `\uF057` | Times Circle |
| ⏱️ | `` | `\uF252` | Timer |
| 📝 | `` | `\uF044` | Edit/Pencil |
| 📅 | `` | `\uF073` | Calendar |
| ⚡ | `` | `\uF0E7` | Bolt/Lightning |
| 🔥 | `` | `\uF06D` | Fire |
| 💪 | `` | `\uF2C5` | Muscle/Strength |
| 🎉 | `` | `\uF005` | Star/Celebration |
| ⭐ | `` | `\uF005` | Star |
| 🚀 | `` | `\uF135` | Rocket |
| 💡 | `` | `\uF0EB` | Lightbulb |
| 📈 | `` | `\uF201` | Chart Line Up |
| 📉 | `` | `\uF200` | Chart Line Down |
| 🏆 | `` | `\uF091` | Trophy |
| 🎯 | `` | `\uF140` | Target/Bullseye |

## Resources

- **Nerd Fonts**: <https://www.nerdfonts.com/>
- **Cheat Sheet**: <https://www.nerdfonts.com/cheat-sheet>
- **JetBrains Mono**: <https://www.jetbrains.com/lp/mono/>
- **Textual Docs**: <https://textual.textualize.io/>

## Technical Notes

### Why Terminal-Level Fonts?

Textual is a TUI framework that renders within terminal emulators. Unlike GUI frameworks or web browsers that have their own rendering engines, TUIs rely entirely on the terminal emulator for:

- Font rendering
- Glyph support
- Color display
- Unicode handling

This is why font configuration must happen at the terminal level, not within the Textual application.

### Unicode Private Use Area

Nerd Fonts uses Unicode Private Use Areas (PUA), specifically:

- Range: E000-F8FF (and extended ranges)
- These code points are guaranteed to never be assigned official Unicode glyphs
- Perfect for custom icon fonts

### Performance

Using Nerd Font icons has zero performance impact compared to emojis:

- Both are Unicode characters
- No additional libraries or dependencies needed
- No runtime overhead
- Renders as fast as any other text

## Next Steps

1. Install JetBrains Mono Nerd Font on your system
2. Configure your terminal to use the font
3. Create `todo_tui/icons.py` module
4. Replace all emojis with Nerd Font icons
5. Update README.md with font requirements
6. Test the application

---

**Note**: This document was created to capture research findings for future implementation. No code changes have been made yet.
