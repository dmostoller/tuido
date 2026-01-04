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

### Quick Install (Recommended)

Install Tuido with [pipx](https://pipx.pypa.io/) for isolated, system-wide access:

```bash
# Install pipx if you don't have it
brew install pipx && pipx ensurepath  # macOS
# or: pip install pipx && pipx ensurepath  # Other platforms

# Install Tuido
pipx install tuido-tui

# Run from anywhere
tuido
```

**Update to latest version:**
```bash
pipx upgrade tuido-tui
```

### Prerequisites

- Python 3.12 or higher
- **JetBrains Mono Nerd Font** (required for proper icon display)

### First-Run Setup Wizard

On first launch, Tuido will guide you through setup with an interactive wizard:

1. **Font Setup**:
   - Automatically detects your terminal (VS Code, Ghostty, iTerm2, etc.)
   - Shows test icons so you can verify fonts are working
   - Provides terminal-specific configuration instructions
   - One-click button to download JetBrains Mono Nerd Font
2. **Weather Widget** (optional): Configure the weather display with a free API key

The setup wizard can be re-run anytime from **Settings → General → Run Setup Wizard** or by pressing `Ctrl+Shift+W`.

### Font Setup (Manual)

If you prefer to set up fonts manually, or need to troubleshoot:

1. **Download JetBrains Mono Nerd Font** from [nerdfonts.com/font-downloads](https://www.nerdfonts.com/font-downloads)
2. **Install the font** by double-clicking the downloaded `.ttf` files
3. **Configure your terminal** to use "JetBrainsMono Nerd Font":
   - **VS Code**: Settings → `terminal.integrated.fontFamily` → `JetBrainsMono Nerd Font`
   - **iTerm2**: Preferences → Profiles → Text → Font
   - **macOS Terminal**: Preferences → Profiles → Text → Change Font
4. **Restart your terminal** completely

> **Seeing rectangles?** See [Troubleshooting](#troubleshooting) or run the setup wizard (`Ctrl+Shift+W`).

### Development Setup

For contributors or running from source:

```bash
# Clone the repository
git clone https://github.com/dmostoller/tuido.git
cd tuido

# Install dependencies with uv (recommended)
uv sync

# Run the application
uv run tuido
# or: uv run python main.py
```

## Usage

After installation, run Tuido from any terminal:

```bash
tuido
```

### Data Storage

Your data is stored in `~/.local/share/tuido/` - run `tuido` from any directory and your tasks are always available.

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | Create new task |
| `Ctrl+P` | Create new project |
| `Ctrl+Shift+S` | Sync with cloud |
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

The dashboard includes an optional weather widget that displays current conditions and a 5-day forecast. To enable it:

1. **Get a free API key** from [OpenWeatherMap](https://openweathermap.org/api):
   - Sign up at <https://home.openweathermap.org/users/sign_up>
   - Get your API key from the dashboard (free tier allows 60 calls/min)

2. **Configure in the app** (no environment variables needed!):
   - Press `s` to open Settings → go to the **Weather** tab
   - Paste your API key
   - Enter your location (e.g., "San Francisco" or "London,UK")
   - Toggle temperature unit between Fahrenheit (°F) and Celsius (°C)
   - Save settings

   Or use the **Setup Wizard** on first launch to configure everything at once!

3. **Disable weather** if you don't want it:
   - Settings → Weather → Toggle off "Enable Weather Widget"
   - Only the Pomodoro timer will be shown in the dashboard

The weather widget updates automatically every 30 minutes.

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

### Cloud Sync (Optional)

Sync your tasks across devices with end-to-end encryption:

1. **Link Your Device**: Press `s` to open Settings, go to the Cloud Sync tab, and click **Link Device**
2. **Authorize in Browser**: Visit the URL shown in Tuido, sign in with Google, and enter the verification code displayed in the app
3. **Set Encryption Password**: Enter a password for end-to-end encryption - your data is encrypted before upload
4. **Sync**: Press `Ctrl+Shift+S` to manually sync, or data syncs automatically on exit

**Privacy & Security:**

- All data is encrypted on your device using AES-256-GCM before upload
- Keys are derived using Argon2id from your encryption password
- The server only stores encrypted blobs that cannot be decrypted without your password
- Your encryption password is stored securely in your system keyring (macOS Keychain, etc.)
- **Important**: There is no password recovery - if you forget your password, your cloud data cannot be recovered

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

### Icons Showing as Rectangles

If you see rectangles (□) instead of icons, your terminal isn't using a Nerd Font.

**Quick Fix:**

1. Run the **Setup Wizard** (`Ctrl+Shift+W`) - it detects your terminal and shows specific configuration instructions
2. The wizard displays test icons so you can verify they work before proceeding
3. Install the font and configure your terminal, then **restart your terminal completely**

**Terminal-Specific Configuration:**

The setup wizard automatically detects your terminal and provides tailored instructions. Here's a reference for common terminals:

| Terminal | Configuration |
|----------|--------------|
| **VS Code** | Settings → Search `terminal.integrated.fontFamily` → Set to `JetBrainsMono Nerd Font` |
| **Ghostty** | `~/.config/ghostty/config` → Add `font-family = JetBrainsMono Nerd Font` |
| **iTerm2** | Preferences → Profiles → Text → Font |
| **macOS Terminal** | Preferences → Profiles → Text → Change Font |
| **Kitty** | `~/.config/kitty/kitty.conf` → `font_family JetBrainsMono Nerd Font` |
| **Alacritty** | `~/.config/alacritty/alacritty.yml` → `font.normal.family: JetBrainsMono Nerd Font` |
| **WezTerm** | `~/.wezterm.lua` → `config.font = wezterm.font('JetBrainsMono Nerd Font')` |
| **Hyper** | `~/.hyper.js` → `fontFamily: 'JetBrainsMono Nerd Font'` |

> **Note:** Icons may work in one terminal (e.g., Ghostty) but not another (e.g., VS Code integrated terminal). Each terminal needs to be configured separately.

**Manual Download:**

1. Download from [nerdfonts.com/font-downloads](https://www.nerdfonts.com/font-downloads) - get "JetBrainsMono Nerd Font" (NOT regular JetBrains Mono)
2. Install all `.ttf` files by double-clicking them
3. Configure your terminal using the table above
4. Restart your terminal completely

### ASCII Fallback Mode

If you can't install Nerd Fonts, use ASCII mode:

```bash
NERD_FONTS_ENABLED=0 tuido
```

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
