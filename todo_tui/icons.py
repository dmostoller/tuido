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
    "CLOCK": "\uF017",
    "TIMER": "\uF252",
    "HOURGLASS": "\uF254",
    # Tasks & Todos
    "CHECK": "\uF00C",
    "CHECK_CIRCLE": "\uF058",
    "TIMES": "\uF00D",
    "TIMES_CIRCLE": "\uF057",
    "SQUARE": "\uF0C8",
    "CHECK_SQUARE": "\uF14A",
    "SQUARE_O": "\uF096",
    # Navigation & UI
    "FOLDER": "\uF07C",
    "FOLDER_OPEN": "\uF07B",
    "FILE": "\uF15B",
    "LIST": "\uF03A",
    "LIST_UL": "\uF0CA",
    # Stats & Metrics
    "CHART_BAR": "\uF080",
    "CHART_LINE": "\uF201",
    "TROPHY": "\uF091",
    "FIRE": "\uF06D",
    "STAR": "\uF005",
    # Actions
    "PLUS": "\uF067",
    "PLUS_CIRCLE": "\uF055",
    "EDIT": "\uF044",
    "PENCIL": "\uF040",
    "TRASH": "\uF1F8",
    "SEARCH": "\uF002",
    "COG": "\uF013",
    # Calendar & Date
    "CALENDAR": "\uF073",
    "CALENDAR_CHECK": "\uF274",
    "CALENDAR_TIMES": "\uF273",
    # Productivity & Pomodoro
    "POMODORO": "\uF500",
    "TOMATO": "\uF500",
    "BELL": "\uF0F3",
    "FLAG": "\uF024",
    "BOOKMARK": "\uF02E",
    "TARGET": "\uF140",
    "BULLSEYE": "\uF140",
    # Status & Alerts
    "WARNING": "\uF071",
    "EXCLAMATION": "\uF12A",
    "INFO": "\uF129",
    "QUESTION": "\uF128",
    # Miscellaneous
    "COFFEE": "\uF0F4",
    "LIGHTNING": "\uF0E7",
    "BOLT": "\uF0E7",
    "ROCKET": "\uF135",
    "LIGHTBULB": "\uF0EB",
    "MUSCLE": "\uF2C5",
    # Weather Icons
    "SUN": "\uE30D",
    "MOON": "\uE32A",
    "CLOUD": "\uE312",
    "CLOUD_SUN": "\uE302",
    "RAIN": "\uE318",
    "SNOW": "\uE31A",
    "THUNDERSTORM": "\uE31D",
    "WIND": "\uE34B",
    "THERMOMETER": "\uF2C7",
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
