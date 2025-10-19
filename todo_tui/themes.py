"""Custom theme definitions for Todo TUI using official color palettes."""

from textual.theme import Theme

# Catppuccin Mocha - Official Colors
# https://catppuccin.com/palette
catppuccin_mocha = Theme(
    name="catppuccin-mocha",
    primary="#89b4fa",  # Blue
    secondary="#cba6f7",  # Mauve
    accent="#fab387",  # Peach
    foreground="#cdd6f4",  # Text
    background="#1e1e2e",  # Base
    success="#a6e3a1",  # Green
    warning="#f9e2af",  # Yellow
    error="#f38ba8",  # Red
    surface="#313244",  # Surface0
    panel="#45475a",  # Surface1
    dark=True,
    variables={
        # Text colors
        "foreground-muted": "#bac2de",  # Subtext1
        "foreground-disabled": "#6c7086",  # Overlay0

        # Border colors
        "border": "#89b4fa",  # Blue
        "border-blurred": "#585b70",  # Surface2

        # Scrollbar
        "scrollbar": "#45475a",  # Surface1
        "scrollbar-hover": "#585b70",  # Surface2
        "scrollbar-background": "#313244",  # Surface0

        # Input selection
        "input-selection-background": "#89b4fa 40%",  # Blue with transparency

        # Block cursor
        "block-cursor-background": "#89b4fa",  # Blue
        "block-cursor-foreground": "#1e1e2e",  # Base
    },
)

# Nord - Official Colors
# https://www.nordtheme.com/docs/colors-and-palettes
nord = Theme(
    name="nord",
    primary="#88c0d0",  # nord8 - Frost
    secondary="#81a1c1",  # nord9 - Frost
    accent="#5e81ac",  # nord10 - Frost
    foreground="#eceff4",  # nord6 - Snow Storm
    background="#2e3440",  # nord0 - Polar Night
    success="#a3be8c",  # nord14 - Aurora Green
    warning="#ebcb8b",  # nord13 - Aurora Yellow
    error="#bf616a",  # nord11 - Aurora Red
    surface="#3b4252",  # nord1 - Polar Night
    panel="#434c5e",  # nord2 - Polar Night
    dark=True,
    variables={
        # Text colors
        "foreground-muted": "#e5e9f0",  # nord5
        "foreground-disabled": "#4c566a",  # nord3

        # Border colors
        "border": "#88c0d0",  # nord8
        "border-blurred": "#4c566a",  # nord3

        # Scrollbar
        "scrollbar": "#434c5e",  # nord2
        "scrollbar-hover": "#4c566a",  # nord3
        "scrollbar-background": "#3b4252",  # nord1

        # Input selection
        "input-selection-background": "#88c0d0 35%",  # nord8 with transparency

        # Block cursor
        "block-cursor-background": "#88c0d0",  # nord8
        "block-cursor-foreground": "#2e3440",  # nord0
    },
)

# Gruvbox Dark - Official Colors
# https://github.com/morhetz/gruvbox
gruvbox = Theme(
    name="gruvbox",
    primary="#83a598",  # Bright Blue
    secondary="#d3869b",  # Bright Purple
    accent="#fe8019",  # Bright Orange
    foreground="#ebdbb2",  # fg
    background="#282828",  # bg0
    success="#b8bb26",  # Bright Green
    warning="#fabd2f",  # Bright Yellow
    error="#fb4934",  # Bright Red
    surface="#3c3836",  # bg1
    panel="#504945",  # bg2
    dark=True,
    variables={
        # Text colors
        "foreground-muted": "#a89984",  # fg4
        "foreground-disabled": "#665c54",  # bg3

        # Border colors
        "border": "#83a598",  # Bright Blue
        "border-blurred": "#504945",  # bg2

        # Scrollbar
        "scrollbar": "#504945",  # bg2
        "scrollbar-hover": "#665c54",  # bg3
        "scrollbar-background": "#3c3836",  # bg1

        # Input selection
        "input-selection-background": "#83a598 40%",  # Bright Blue with transparency

        # Block cursor
        "block-cursor-background": "#83a598",  # Bright Blue
        "block-cursor-foreground": "#282828",  # bg0
    },
)

# Tokyo Night - Official Colors
# https://github.com/tokyo-night/tokyo-night-vscode-theme
tokyo_night = Theme(
    name="tokyo-night",
    primary="#7aa2f7",  # Blue
    secondary="#bb9af7",  # Purple
    accent="#7dcfff",  # Cyan
    foreground="#c0caf5",  # Primary text
    background="#1a1b26",  # Night background
    success="#9ece6a",  # Green
    warning="#e0af68",  # Yellow
    error="#f7768e",  # Red
    surface="#24283b",  # Storm background
    panel="#414868",  # UI element
    dark=True,
    variables={
        # Text colors
        "foreground-muted": "#a9b1d6",  # Secondary text
        "foreground-disabled": "#565f89",  # Dimmed text

        # Border colors
        "border": "#7aa2f7",  # Blue
        "border-blurred": "#414868",  # UI element

        # Scrollbar
        "scrollbar": "#414868",  # UI element
        "scrollbar-hover": "#565f89",  # Dimmed
        "scrollbar-background": "#24283b",  # Storm background

        # Input selection
        "input-selection-background": "#7aa2f7 35%",  # Blue with transparency

        # Block cursor
        "block-cursor-background": "#7aa2f7",  # Blue
        "block-cursor-foreground": "#1a1b26",  # Night background
    },
)

# Solarized Light - Official Colors
# https://ethanschoonover.com/solarized/
solarized_light = Theme(
    name="solarized-light",
    primary="#268bd2",  # Blue
    secondary="#6c71c4",  # Violet
    accent="#2aa198",  # Cyan
    foreground="#657b83",  # base00
    background="#fdf6e3",  # base3
    success="#859900",  # Green
    warning="#b58900",  # Yellow
    error="#dc322f",  # Red
    surface="#eee8d5",  # base2
    panel="#93a1a1",  # base1
    dark=False,
    variables={
        # Text colors
        "foreground-muted": "#93a1a1",  # base1
        "foreground-disabled": "#93a1a1",  # base1

        # Border colors
        "border": "#268bd2",  # Blue
        "border-blurred": "#93a1a1",  # base1

        # Scrollbar
        "scrollbar": "#93a1a1",  # base1
        "scrollbar-hover": "#839496",  # base0
        "scrollbar-background": "#eee8d5",  # base2

        # Input selection
        "input-selection-background": "#268bd2 30%",  # Blue with transparency

        # Block cursor
        "block-cursor-background": "#268bd2",  # Blue
        "block-cursor-foreground": "#fdf6e3",  # base3
    },
)

# Tailwind CSS Dark (Enhanced) - Official Colors
# https://github.com/tailwindlabs/tailwindcss-vscode-theme
tailwind_dark = Theme(
    name="tailwind-dark",
    primary="#00a6f4",  # Bright Blue
    secondary="#00bcff",  # Cyan
    accent="#c27aff",  # Purple
    foreground="#f9fafb",  # Bright White
    background="#101828",  # Deep Navy
    success="#00d492",  # Cyan Green
    warning="#ffb900",  # Yellow
    error="#ff637e",  # Pink Red
    surface="#1e2939",  # Dark Navy
    panel="#364153",  # Medium Navy
    dark=True,
    variables={
        # Text colors
        "foreground-muted": "#99a1af",  # Subdued gray
        "foreground-disabled": "#6a7282",  # Dimmed gray

        # Border colors
        "border": "#00a6f4",  # Bright Blue
        "border-blurred": "#364153",  # Medium Navy

        # Scrollbar
        "scrollbar": "#364153",  # Medium Navy
        "scrollbar-hover": "#4a5565",  # Lighter Navy
        "scrollbar-background": "#1e2939",  # Dark Navy

        # Input selection
        "input-selection-background": "#00a6f4 35%",  # Blue with transparency

        # Block cursor
        "block-cursor-background": "#00a6f4",  # Bright Blue
        "block-cursor-foreground": "#101828",  # Deep Navy
    },
)

# Tailwind CSS Light (Enhanced) - Official Colors
# https://github.com/tailwindlabs/tailwindcss-vscode-theme
tailwind_light = Theme(
    name="tailwind-light",
    primary="#00a6f4",  # Bright Blue
    secondary="#0084d1",  # Darker Blue
    accent="#ad46ff",  # Purple
    foreground="#1d293d",  # Dark Navy
    background="#ffffff",  # White
    success="#009966",  # Green
    warning="#e17100",  # Orange
    error="#ec003f",  # Red
    surface="#f8fafc",  # Light Gray
    panel="#f1f5f9",  # Slightly Darker Gray
    dark=False,
    variables={
        # Text colors
        "foreground-muted": "#62748e",  # Subdued blue-gray
        "foreground-disabled": "#90a1b9",  # Lighter gray

        # Border colors
        "border": "#00a6f4",  # Bright Blue
        "border-blurred": "#cad5e2",  # Light border

        # Scrollbar
        "scrollbar": "#cad5e2",  # Light border
        "scrollbar-hover": "#90a1b9",  # Gray
        "scrollbar-background": "#f8fafc",  # Light Gray

        # Input selection
        "input-selection-background": "#2b7fff 40%",  # Blue with transparency

        # Block cursor
        "block-cursor-background": "#00a6f4",  # Bright Blue
        "block-cursor-foreground": "#ffffff",  # White
    },
)

# Export all themes
ALL_THEMES = [
    catppuccin_mocha,
    nord,
    gruvbox,
    tokyo_night,
    solarized_light,
    tailwind_dark,
    tailwind_light,
]
