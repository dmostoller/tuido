"""Icon constants using Nerd Font glyphs.

This module provides icon constants for the todo-tui application using Nerd Fonts.
Requires JetBrains Mono Nerd Font or another Nerd Font to be installed and configured
in your terminal emulator.

For more information about Nerd Fonts:
- Website: https://www.nerdfonts.com/
- Cheat Sheet: https://www.nerdfonts.com/cheat-sheet
- Download: https://www.nerdfonts.com/font-downloads
"""

import os

# Global variable for runtime Nerd Fonts control
# Initialized from environment variable, but can be changed at runtime
NERD_FONTS_ENABLED = os.getenv("NERD_FONTS_ENABLED", "1") == "1"


def _has_nerd_font() -> bool:
    """Check if terminal likely has Nerd Font support.

    Returns:
        bool: True if Nerd Fonts should be enabled (default), False otherwise.

    Note:
        Can be disabled by setting NERD_FONTS_ENABLED=0 environment variable.
        This function checks the global NERD_FONTS_ENABLED variable which can
        be modified at runtime.
    """
    return NERD_FONTS_ENABLED


# Icon definitions - Nerd Font glyphs and ASCII fallbacks
_ICONS_NERD = {
    # Time & Clock
    "CLOCK": "\uf017",
    "TIMER": "\uf252",
    "HOURGLASS": "\uf254",
    # Tasks & Todos
    "CHECK": "\uf00c",
    "CHECK_CIRCLE": "\uf058",
    "TIMES": "\uf00d",
    "TIMES_CIRCLE": "\uf057",
    "SQUARE": "\uf0c8",
    "CHECK_SQUARE": "\uf14a",
    "SQUARE_O": "\uf096",
    # Navigation & UI
    "FOLDER": "\uf07c",
    "FOLDER_OPEN": "\uf07b",
    "FILE": "\uf15b",
    "CODE": "\uf121",
    "LIST": "\uf03a",
    "LIST_UL": "\uf0ca",
    # Stats & Metrics
    "CHART_BAR": "\uf080",
    "CHART_LINE": "\uf201",
    "TROPHY": "\uf091",
    "FIRE": "\uf06d",
    "STAR": "\uf005",
    # Actions
    "PLUS": "\uf067",
    "PLUS_CIRCLE": "\uf055",
    "EDIT": "\uf044",
    "PENCIL": "\uf040",
    "TRASH": "\uf1f8",
    "SEARCH": "\uf002",
    "COG": "\uf013",
    "COPY": "\uf0c5",
    "SWAP": "\uf362",
    "EXCHANGE": "\uf362",
    "ARROWS_H": "\uf07e",
    # Calendar & Date
    "CALENDAR": "\uf073",
    "CALENDAR_CHECK": "\uf274",
    "CALENDAR_TIMES": "\uf273",
    # Productivity & Pomodoro
    "POMODORO": "\uf500",
    "TOMATO": "\uf500",
    "BELL": "\uf0f3",
    "FLAG": "\uf024",
    "BOOKMARK": "\uf02e",
    "TARGET": "\uf140",
    "BULLSEYE": "\uf140",
    # Status & Alerts
    "WARNING": "\uf071",
    "EXCLAMATION": "\uf12a",
    "INFO": "\uf129",
    "QUESTION": "\uf128",
    # Miscellaneous
    "COFFEE": "\uf0f4",
    "LIGHTNING": "\uf0e7",
    "BOLT": "\uf0e7",
    "ROCKET": "\uf135",
    "LIGHTBULB": "\uf0eb",
    "MUSCLE": "\uf2c5",
    "PALETTE": "\uf53f",
    "DOWNLOAD": "\uf019",
    "LINK": "\uf0c1",
    "CLOUD_DOWNLOAD": "\uf0ed",
    # Weather Icons
    "SUN": "\ue30d",
    "MOON": "\ue32a",
    "CLOUD": "\ue312",
    "CLOUD_SUN": "\ue302",
    "RAIN": "\ue318",
    "SNOW": "\ue31a",
    "THUNDERSTORM": "\ue31d",
    "WIND": "\ue34b",
    "THERMOMETER": "\uf2c7",
    "DROPLET": "\uf043",
}

_ICONS_ASCII = {
    # Time & Clock
    "CLOCK": "[T]",
    "TIMER": "[t]",
    "HOURGLASS": "[h]",
    # Tasks & Todos
    "CHECK": "[✓]",
    "CHECK_CIRCLE": "(✓)",
    "TIMES": "[✗]",
    "TIMES_CIRCLE": "(✗)",
    "SQUARE": "[ ]",
    "CHECK_SQUARE": "[✓]",
    "SQUARE_O": "[ ]",
    # Navigation & UI
    "FOLDER": "[F]",
    "FOLDER_OPEN": "[f]",
    "FILE": "[f]",
    "CODE": "[<>]",
    "LIST": "[L]",
    "LIST_UL": "[L]",
    # Stats & Metrics
    "CHART_BAR": "[#]",
    "CHART_LINE": "[/]",
    "TROPHY": "[T]",
    "FIRE": "[*]",
    "STAR": "[*]",
    # Actions
    "PLUS": "[+]",
    "PLUS_CIRCLE": "(+)",
    "EDIT": "[e]",
    "PENCIL": "[p]",
    "TRASH": "[D]",
    "SEARCH": "[?]",
    "COG": "[*]",
    "COPY": "[C]",
    "SWAP": "[<>]",
    "EXCHANGE": "[<>]",
    "ARROWS_H": "[<->]",
    # Calendar & Date
    "CALENDAR": "[C]",
    "CALENDAR_CHECK": "[C✓]",
    "CALENDAR_TIMES": "[C✗]",
    # Productivity & Pomodoro
    "POMODORO": "[P]",
    "TOMATO": "[P]",
    "BELL": "[!]",
    "FLAG": "[>]",
    "BOOKMARK": "[B]",
    "TARGET": "[O]",
    "BULLSEYE": "[O]",
    # Status & Alerts
    "WARNING": "[!]",
    "EXCLAMATION": "[!]",
    "INFO": "[i]",
    "QUESTION": "[?]",
    # Miscellaneous
    "COFFEE": "[c]",
    "LIGHTNING": "[~]",
    "BOLT": "[~]",
    "ROCKET": "[R]",
    "LIGHTBULB": "[i]",
    "MUSCLE": "[M]",
    "PALETTE": "[P]",
    "DOWNLOAD": "[v]",
    "LINK": "[>]",
    "CLOUD_DOWNLOAD": "[v]",
    # Weather Icons
    "SUN": "[O]",
    "MOON": "[)]",
    "CLOUD": "[~]",
    "CLOUD_SUN": "[O~]",
    "RAIN": "[||]",
    "SNOW": "[*]",
    "THUNDERSTORM": "[~!]",
    "WIND": "[>>]",
    "THERMOMETER": "[T]",
    "DROPLET": "[~]",
}


class IconsMeta(type):
    """Metaclass that provides dynamic attribute access for icons."""

    def __getattribute__(cls, name: str):
        # Allow access to special attributes and methods
        if name.startswith("_") or name in ("__class__", "__doc__"):
            return super().__getattribute__(name)

        # Dynamically return the appropriate icon based on NERD_FONTS_ENABLED
        if NERD_FONTS_ENABLED:
            return _ICONS_NERD.get(name, f"[{name}]")
        else:
            return _ICONS_ASCII.get(name, f"[{name}]")


class Icons(metaclass=IconsMeta):
    """Icon constants with fallback support for terminals without Nerd Fonts.

    Icons are accessed as class attributes (e.g., Icons.CHECK) and will
    dynamically return either Nerd Font glyphs or ASCII fallbacks based on
    the global NERD_FONTS_ENABLED setting.
    """

    pass
