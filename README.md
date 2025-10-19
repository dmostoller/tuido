# Tuido

A Terminal User Interface (TUI) todo application built with Textual.
Manage your tasks efficiently from the comfort of your terminal!

## Features

- **Beautiful UI**: Multiple theme options with official color palettes
- **Theme Support**: 5 beautiful themes - Catppuccin Mocha, Nord, Gruvbox, Tokyo Night, and Solarized Light
- **Dashboard**: Real-time metrics showing task statistics (total, completed, completion rate, daily/weekly progress)
- **Weather Widget**: Current weather with ASCII art display (optional, requires OpenWeatherMap API)
- **Pomodoro Timer**: Built-in focus timer for productivity tracking
- **Project Organization**: Group tasks into projects for better organization
- **Full CRUD Operations**: Create, Read, Update, and Delete tasks with ease
- **Subtask Support**: Break down complex tasks into manageable subtasks
- **Persistent Storage**: JSON-based local storage - your data stays on your machine in `~/.local/share/tuido/`
- **Notes & Scratchpad**: Quick note-taking with markdown support for ideas and meeting notes
- **Keyboard & Mouse Support**: Navigate efficiently with keyboard shortcuts or mouse clicks
- **Quick Actions**: Fast task creation with a hotkey
- **Run from Anywhere**: Works from any directory - set up an alias for instant access

## Themes

Tuido comes with **5 carefully crafted themes** using official color palettes from popular color schemes. Switch between themes instantly with `Ctrl+P` → "Change theme".

### Available Themes

| Theme | Style | Colors | Best For |
|-------|-------|--------|----------|
| **Catppuccin Mocha** *(default)* | Dark | Soothing pastels with rich accents | Long coding sessions, low eye strain |
| **Nord** | Dark | Arctic, north-bluish palette | Clean, professional look |
| **Gruvbox** | Dark | Retro groove, warm colors | Vintage terminal aesthetic |
| **Tokyo Night** | Dark | Vibrant cyberpunk blues/purples | Modern, high-contrast displays |
| **Solarized Light** | Light | Precision colors for readability | Daytime use, bright environments |

### Switching Themes

1. Press `Ctrl+P` to open the Command Palette
2. Type "theme" or "Change theme"
3. Select your preferred theme
4. Colors update instantly across the entire interface

**Quick Theme Switching:**

```bash
# Default: Catppuccin Mocha
uv run python main.py
```

All themes use their **official color palettes** for authentic appearance:

- **Catppuccin Mocha**: [catppuccin.com](https://catppuccin.com/palette)
- **Nord**: [nordtheme.com](https://www.nordtheme.com/docs/colors-and-palettes)
- **Gruvbox**: [github.com/morhetz/gruvbox](https://github.com/morhetz/gruvbox)
- **Tokyo Night**: [github.com/tokyo-night](https://github.com/tokyo-night/tokyo-night-vscode-theme)
- **Solarized**: [ethanschoonover.com/solarized](https://ethanschoonover.com/solarized/)

## Screenshots

The app features a three-panel layout:

- **Top Panel**: Dashboard with task metrics (2×2 grid)
  - **Activity Chart** - 14-day completion sparkline with progress bar
  - **Clock** - Real-time clock display
  - **Stats** - Total tasks, completion rate, today's completions
  - **Productivity Tabs** - Tabbed widget with Pomodoro timer and Weather display
- **Left Panel**: Projects list with "All Tasks" view
- **Center Panel**: Task list with completion indicators
- **Right Panel**: Detailed task information with actions

## Installation

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip
- **JetBrains Mono Nerd Font** (required for proper icon display)

### Setup

1. **Install JetBrains Mono Nerd Font**

   This application uses Nerd Font icons for a beautiful visual experience. You need to install and configure JetBrains Mono Nerd Font in your terminal.

   **Download and Install:**
   - Visit [Nerd Fonts Downloads](https://www.nerdfonts.com/font-downloads)
   - Download "JetBrainsMono Nerd Font"
   - Install the font on your system

   **Configure Your Terminal:**
   - **macOS Terminal.app**: Preferences → Profiles → Text → Change font to "JetBrainsMono Nerd Font"
   - **iTerm2**: Preferences → Profiles → Text → Font → Select "JetBrainsMono Nerd Font"
   - **WezTerm**: Already bundles JetBrains Mono by default
   - **Alacritty**: Edit `~/.config/alacritty/alacritty.yml`:

     ```yaml
     font:
       normal:
         family: "JetBrainsMono Nerd Font"
     ```

   - **VS Code Terminal**: Settings → Terminal › Integrated: Font Family → `JetBrainsMono Nerd Font`

   > **Important**: After configuring the font, **restart your terminal completely** for changes to take effect.
   >
   > **Seeing rectangles instead of icons?** See the [Troubleshooting](#troubleshooting) section below.

   **Testing Your Setup:**

   After installation and configuration, test that icons are working:

   ```bash
   python test_icons.py
   ```

   If you see proper icons in the test output, you're all set! If you see rectangles, check the [Troubleshooting](#troubleshooting) section.

2. Clone the repository:

   ```bash
   git clone https://github.com/dmostoller/tuido.git
   cd tuido
   ```

   > **Note**: Replace `yourusername` with the actual repository owner when the repo is published.

3. Install dependencies:

Using uv (recommended):

   ```bash
   uv sync
   ```

   Or using pip:

   ```bash
   pip install textual textual-dev
   ```

## Usage

### Running the Application

```bash
# With uv (recommended)
uv run python main.py

# Or directly
python main.py
```

### Running from Anywhere

Since data is stored in `~/.local/share/tuido/`, you can run the app from any directory. Set up a shell alias for quick access:

**Bash/Zsh** (add to `~/.bashrc` or `~/.zshrc`):

```bash
alias todo='cd /path/to/tuido && uv run python main.py'
```

**Or with a function for better path handling:**

```bash
todo() {
    (cd /path/to/tuido && uv run python main.py)
}
```

After adding the alias, reload your shell configuration:

```bash
source ~/.bashrc  # or source ~/.zshrc
```

Now you can simply type `todo` from any directory to launch the app!

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | Create new task |
| `Ctrl+P` | Create new project |
| `n` | Open notes/scratchpad |
| `s` | Open settings |
| `Enter` | Edit selected task |
| `Space` | Toggle task completion |
| `Delete` | Delete selected task |
| `Tab` / `Shift+Tab` | Navigate between panels |
| `↑` / `↓` | Navigate lists |
| `q` | Quit application |

### Basic Workflow

1. **Create a Task**: Press `Ctrl+N` to open the quick add dialog
2. **Organize by Project**: Press `Ctrl+P` to create a new project, then add tasks to it
3. **Manage Tasks**:
   - Select a task to view details in the right panel
   - Press `Enter` to edit
   - Press `Space` to mark as complete
   - Press `Delete` to remove
4. **Add Subtasks**: Edit a task and add subtasks for complex work
5. **Track Progress**: View your productivity metrics in the dashboard

### Weather Widget (Optional)

The dashboard includes an optional weather widget that displays current conditions with ASCII art. To enable it:

1. **Get a free API key** from [OpenWeatherMap](https://openweathermap.org/api):
   - Sign up at <https://home.openweathermap.org/users/sign_up>
   - Get your API key from the dashboard (free tier allows 60 calls/min)

2. **Set your API key** as an environment variable:

   ```bash
   export OPENWEATHER_API_KEY="your-api-key-here"
   ```

   Or create a `.env` file in the project root:

   ```text
   OPENWEATHER_API_KEY=your-api-key-here
   ```

3. **Configure location and temperature unit** in the app:
   - Run the app: `uv run python main.py`
   - Press `s` to open Settings
   - Enter your location (e.g., "San Francisco" or "London,UK")
   - Toggle temperature unit between Fahrenheit (°F) and Celsius (°C)
   - Save settings

The weather widget will update automatically every 30 minutes.

**Without configuration**, the weather widget displays "Not Configured" - the app works perfectly fine without it!

### Notes & Scratchpad

The app includes a built-in notes feature for quick note-taking, meeting notes, or brainstorming:

1. **Open Notes**: Press `n` from anywhere in the app
2. **Create Notes**: Click "New Note" button or use the keyboard shortcut
3. **Markdown Support**: Full markdown formatting for rich text
4. **Multiple Notes**: Organize different topics into separate notes
5. **Quick Access**: Your notes are always one keypress away

Notes are stored in `~/.local/share/tuido/notes.json` and sync automatically as you type.

**Use Cases:**

- Quick capture during standups
- Meeting notes with tasks
- Brainstorming ideas
- Code snippets or commands
- Project planning drafts

## Development

### Project Structure

```
tuido/
├── main.py                 # Entry point
├── todo_tui/
│   ├── app.py             # Main Textual application
│   ├── models.py          # Data models (Task, Project, Subtask)
│   ├── storage.py         # JSON storage manager
│   ├── theme.css          # Theme definitions
│   └── widgets/           # UI components
│       ├── dashboard.py   # Metrics dashboard
│       ├── project_list.py
│       ├── task_list.py
│       ├── task_detail.py
│       └── dialogs.py     # Modal dialogs
└── pyproject.toml         # Project dependencies
```

### Running with Textual DevTools

For debugging and live development:

```bash
# Terminal 1: Start the devtools console
textual console

# Terminal 2: Run the app in dev mode
textual run --dev main.py
```

### Data Storage

All data is stored locally on your machine following the **XDG Base Directory Specification**:

**Storage Location:** `~/.local/share/tuido/`

This means your data persists in a central location regardless of where you run the app from. The storage includes:

- `projects.json` - Project metadata
- `{project-id}.json` - Tasks for each project
- `notes.json` - Your notes and scratchpad content
- `settings.json` - App preferences (theme, weather location, etc.)

All data is stored in human-readable JSON format.

**Migration from Old Location:**

If you previously used this app with data stored in the relative `data/` directory, the app will automatically migrate your data to the new location on first run. The old directory can be safely deleted after migration.

## Troubleshooting

### Icons Showing as Rectangles or Question Marks

If you see rectangles (□), question marks (?), or other placeholder characters instead of icons, this means your terminal isn't configured to use a Nerd Font.

**Quick Test:**

Run the icon test script to verify your font configuration:

```bash
python test_icons.py
```

This will display all icons used in the app. If you see proper icons, your setup is working! If you see rectangles, follow the steps below.

**Solution:**

1. **Verify Font Installation**
   - JetBrains Mono Nerd Font must be installed on your system
   - Download from: <https://www.nerdfonts.com/font-downloads>
   - Look for "JetBrainsMono Nerd Font" (NOT regular JetBrains Mono)
   - Install all font files (.ttf or .otf) by double-clicking them

2. **Configure Your Terminal** (CRITICAL STEP)

   The font must be set in your terminal emulator's preferences:

   **VS Code Terminal** (most common):
   - Open Settings (Cmd+, or Ctrl+,)
   - Search for: `terminal.integrated.fontFamily`
   - Set to: `JetBrainsMono Nerd Font`
   - **Restart VS Code completely**

   **macOS Terminal.app**:
   - Terminal → Preferences (Cmd+,)
   - Profiles tab → Text section
   - Click "Change" button under Font
   - Select "JetBrainsMono Nerd Font"
   - Set size to 12-14pt for best results

   **iTerm2**:
   - Preferences → Profiles → Text
   - Change Font to "JetBrainsMono Nerd Font"

   **Alacritty**:
   - Edit `~/.config/alacritty/alacritty.yml`:

     ```yaml
     font:
       normal:
         family: "JetBrainsMono Nerd Font"
     ```

3. **Restart Your Terminal**
   - Completely close and reopen your terminal
   - Run `python test_icons.py` again to verify

**Still Not Working?**

- Make sure you installed **Nerd Font** version, not regular JetBrains Mono
- Check that your terminal is actually using the font (some terminals have separate settings for different profiles)
- Try setting a different Nerd Font to test (e.g., "FiraCode Nerd Font")

### Temporary Workaround: ASCII Fallback Mode

If you can't install Nerd Fonts, you can use ASCII fallback characters:

```bash
NERD_FONTS_ENABLED=0 uv run python main.py
```

This will replace all icons with simple ASCII characters like `[✓]`, `[✗]`, etc.

## Contributing

This is a personal project, but suggestions and improvements are welcome! Feel free to open an issue or submit a pull request.

## License

MIT License - feel free to use this project however you'd like!

## Acknowledgments

- Built with [Textual](https://textual.textualize.io/) - Amazing Python TUI framework
- Styled with [Catppuccin](https://github.com/catppuccin/catppuccin) - Soothing pastel theme
- Inspired by [btop](https://github.com/aristocratos/btop) - Beautiful system monitor

## Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#troubleshooting) section above for common issues
2. Review the [keyboard shortcuts](#keyboard-shortcuts) for navigation help
3. Run with `textual run --dev main.py` to see detailed logs and debug output

---

Happy task managing! 🎉
