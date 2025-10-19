"""Markdown syntax highlighting configuration for TextArea widget."""

from pathlib import Path

from rich.style import Style
from textual.widgets.text_area import TextAreaTheme
from tree_sitter import Language
import tree_sitter_markdown


def get_markdown_language():
    """Get the tree-sitter Language object for markdown.

    Returns:
        Language: The markdown tree-sitter language.
    """
    return Language(tree_sitter_markdown.language())


def get_markdown_highlight_query() -> str:
    """Load the markdown highlight query from Textual's bundled queries.

    Returns:
        str: The markdown highlight query in tree-sitter format.
    """
    # Textual bundles highlight queries - use the markdown one
    import textual

    textual_path = Path(textual.__file__).parent
    query_file = textual_path / "tree-sitter" / "highlights" / "markdown.scm"

    if query_file.exists():
        return query_file.read_text()

    # Fallback minimal query if file not found
    return """
    (atx_heading (inline) @heading)
    (setext_heading (paragraph) @heading)

    [
      (atx_h1_marker)
      (atx_h2_marker)
      (atx_h3_marker)
      (atx_h4_marker)
      (atx_h5_marker)
      (atx_h6_marker)
    ] @heading.marker

    [
      (link_title)
      (indented_code_block)
      (fenced_code_block)
    ] @text.literal

    [
      (link_destination)
    ] @link.uri

    [
      (list_marker_plus)
      (list_marker_minus)
      (list_marker_star)
    ] @list.marker
    """


# Catppuccin Mocha TextAreaTheme
catppuccin_mocha_markdown = TextAreaTheme(
    name="catppuccin-mocha",
    base_style=Style(color="#cdd6f4", bgcolor="#1e1e2e"),  # Text on Base
    gutter_style=Style(color="#6c7086", bgcolor="#1e1e2e"),  # Overlay0 on Base
    cursor_style=Style(color="#1e1e2e", bgcolor="#89b4fa"),  # Base on Blue
    cursor_line_style=Style(bgcolor="#313244"),  # Surface0
    selection_style=Style(bgcolor="#45475a"),  # Surface1
    syntax_styles={
        # Headings - Blue, bold
        "heading": Style(color="#89b4fa", bold=True),
        "heading.marker": Style(color="#89b4fa", dim=True),
        # Code blocks - Green background
        "text.literal": Style(color="#a6e3a1", bgcolor="#313244"),
        # Links - Mauve, underlined
        "link.uri": Style(color="#cba6f7", underline=True),
        "link.label": Style(color="#f5c2e7"),  # Pink
        # Lists - Peach
        "list.marker": Style(color="#fab387"),
        # Punctuation - Overlay1
        "punctuation.delimiter": Style(color="#7f849c"),
        "punctuation.special": Style(color="#7f849c"),  # Block quotes
        # Escape sequences - Yellow
        "string.escape": Style(color="#f9e2af"),
    },
)

# Nord TextAreaTheme
nord_markdown = TextAreaTheme(
    name="nord",
    base_style=Style(color="#eceff4", bgcolor="#2e3440"),  # Snow Storm on Polar Night
    gutter_style=Style(color="#4c566a", bgcolor="#2e3440"),
    cursor_style=Style(color="#2e3440", bgcolor="#88c0d0"),  # Frost
    cursor_line_style=Style(bgcolor="#3b4252"),
    selection_style=Style(bgcolor="#434c5e"),
    syntax_styles={
        "heading": Style(color="#88c0d0", bold=True),  # Frost
        "heading.marker": Style(color="#88c0d0", dim=True),
        "text.literal": Style(color="#a3be8c", bgcolor="#3b4252"),  # Green
        "link.uri": Style(color="#81a1c1", underline=True),  # Frost
        "link.label": Style(color="#b48ead"),  # Purple
        "list.marker": Style(color="#d08770"),  # Orange
        "punctuation.delimiter": Style(color="#616e88"),
        "punctuation.special": Style(color="#616e88"),
        "string.escape": Style(color="#ebcb8b"),  # Yellow
    },
)

# Gruvbox Dark TextAreaTheme
gruvbox_markdown = TextAreaTheme(
    name="gruvbox",
    base_style=Style(color="#ebdbb2", bgcolor="#282828"),
    gutter_style=Style(color="#665c54", bgcolor="#282828"),
    cursor_style=Style(color="#282828", bgcolor="#83a598"),  # Bright Blue
    cursor_line_style=Style(bgcolor="#3c3836"),
    selection_style=Style(bgcolor="#504945"),
    syntax_styles={
        "heading": Style(color="#83a598", bold=True),  # Bright Blue
        "heading.marker": Style(color="#83a598", dim=True),
        "text.literal": Style(color="#b8bb26", bgcolor="#3c3836"),  # Bright Green
        "link.uri": Style(color="#d3869b", underline=True),  # Bright Purple
        "link.label": Style(color="#d3869b"),
        "list.marker": Style(color="#fe8019"),  # Bright Orange
        "punctuation.delimiter": Style(color="#928374"),
        "punctuation.special": Style(color="#928374"),
        "string.escape": Style(color="#fabd2f"),  # Bright Yellow
    },
)

# Tokyo Night TextAreaTheme
tokyo_night_markdown = TextAreaTheme(
    name="tokyo-night",
    base_style=Style(color="#c0caf5", bgcolor="#1a1b26"),
    gutter_style=Style(color="#565f89", bgcolor="#1a1b26"),
    cursor_style=Style(color="#1a1b26", bgcolor="#7aa2f7"),  # Blue
    cursor_line_style=Style(bgcolor="#24283b"),
    selection_style=Style(bgcolor="#414868"),
    syntax_styles={
        "heading": Style(color="#7aa2f7", bold=True),  # Blue
        "heading.marker": Style(color="#7aa2f7", dim=True),
        "text.literal": Style(color="#9ece6a", bgcolor="#24283b"),  # Green
        "link.uri": Style(color="#bb9af7", underline=True),  # Purple
        "link.label": Style(color="#bb9af7"),
        "list.marker": Style(color="#ff9e64"),  # Orange
        "punctuation.delimiter": Style(color="#565f89"),
        "punctuation.special": Style(color="#565f89"),
        "string.escape": Style(color="#e0af68"),  # Yellow
    },
)

# Solarized Light TextAreaTheme
solarized_light_markdown = TextAreaTheme(
    name="solarized-light",
    base_style=Style(color="#657b83", bgcolor="#fdf6e3"),
    gutter_style=Style(color="#93a1a1", bgcolor="#fdf6e3"),
    cursor_style=Style(color="#fdf6e3", bgcolor="#268bd2"),  # Blue
    cursor_line_style=Style(bgcolor="#eee8d5"),
    selection_style=Style(bgcolor="#eee8d5"),
    syntax_styles={
        "heading": Style(color="#268bd2", bold=True),  # Blue
        "heading.marker": Style(color="#268bd2", dim=True),
        "text.literal": Style(color="#859900", bgcolor="#eee8d5"),  # Green
        "link.uri": Style(color="#6c71c4", underline=True),  # Violet
        "link.label": Style(color="#6c71c4"),
        "list.marker": Style(color="#cb4b16"),  # Orange
        "punctuation.delimiter": Style(color="#93a1a1"),
        "punctuation.special": Style(color="#93a1a1"),
        "string.escape": Style(color="#b58900"),  # Yellow
    },
)

# Tailwind Dark TextAreaTheme
tailwind_dark_markdown = TextAreaTheme(
    name="tailwind-dark",
    base_style=Style(color="#f9fafb", bgcolor="#101828"),
    gutter_style=Style(color="#6a7282", bgcolor="#101828"),
    cursor_style=Style(color="#101828", bgcolor="#00a6f4"),  # Bright Blue
    cursor_line_style=Style(bgcolor="#1e2939"),
    selection_style=Style(bgcolor="#364153"),
    syntax_styles={
        "heading": Style(color="#00a6f4", bold=True),  # Bright Blue
        "heading.marker": Style(color="#00a6f4", dim=True),
        "text.literal": Style(color="#00d492", bgcolor="#1e2939"),  # Cyan Green
        "link.uri": Style(color="#c27aff", underline=True),  # Purple
        "link.label": Style(color="#c27aff"),
        "list.marker": Style(color="#ffb900"),  # Yellow
        "punctuation.delimiter": Style(color="#99a1af"),
        "punctuation.special": Style(color="#99a1af"),
        "string.escape": Style(color="#ffb900"),
    },
)

# Tailwind Light TextAreaTheme
tailwind_light_markdown = TextAreaTheme(
    name="tailwind-light",
    base_style=Style(color="#1d293d", bgcolor="#ffffff"),
    gutter_style=Style(color="#90a1b9", bgcolor="#ffffff"),
    cursor_style=Style(color="#ffffff", bgcolor="#00a6f4"),  # Bright Blue
    cursor_line_style=Style(bgcolor="#f8fafc"),
    selection_style=Style(bgcolor="#f1f5f9"),
    syntax_styles={
        "heading": Style(color="#00a6f4", bold=True),  # Bright Blue
        "heading.marker": Style(color="#00a6f4", dim=True),
        "text.literal": Style(color="#009966", bgcolor="#f8fafc"),  # Green
        "link.uri": Style(color="#ad46ff", underline=True),  # Purple
        "link.label": Style(color="#ad46ff"),
        "list.marker": Style(color="#e17100"),  # Orange
        "punctuation.delimiter": Style(color="#62748e"),
        "punctuation.special": Style(color="#62748e"),
        "string.escape": Style(color="#e17100"),
    },
)

# Textual Dark (Default) TextAreaTheme
textual_dark_markdown = TextAreaTheme(
    name="textual-dark",
    base_style=Style(color="#e0e0e0", bgcolor="#0d1117"),
    gutter_style=Style(color="#7d8590", bgcolor="#0d1117"),
    cursor_style=Style(color="#0d1117", bgcolor="#0178D4"),  # Textual primary
    cursor_line_style=Style(bgcolor="#161b22"),
    selection_style=Style(bgcolor="#264466"),
    syntax_styles={
        "heading": Style(color="#0178D4", bold=True),  # Primary blue
        "heading.marker": Style(color="#0178D4", dim=True),
        "text.literal": Style(color="#4EBF71", bgcolor="#161b22"),  # Success green
        "link.uri": Style(color="#ffa62b", underline=True),  # Accent/warning
        "link.label": Style(color="#ffa62b"),
        "list.marker": Style(color="#ffa62b"),  # Accent
        "punctuation.delimiter": Style(color="#7d8590"),
        "punctuation.special": Style(color="#7d8590"),
        "string.escape": Style(color="#ffa62b"),
    },
)

# Textual Light TextAreaTheme
textual_light_markdown = TextAreaTheme(
    name="textual-light",
    base_style=Style(color="#24292e", bgcolor="#ffffff"),
    gutter_style=Style(color="#6a737d", bgcolor="#ffffff"),
    cursor_style=Style(color="#ffffff", bgcolor="#0178D4"),  # Textual primary
    cursor_line_style=Style(bgcolor="#f6f8fa"),
    selection_style=Style(bgcolor="#c8e1ff"),
    syntax_styles={
        "heading": Style(color="#0178D4", bold=True),  # Primary blue
        "heading.marker": Style(color="#0178D4", dim=True),
        "text.literal": Style(color="#22863a", bgcolor="#f6f8fa"),  # Green
        "link.uri": Style(color="#e17100", underline=True),  # Orange
        "link.label": Style(color="#e17100"),
        "list.marker": Style(color="#e17100"),  # Orange
        "punctuation.delimiter": Style(color="#6a737d"),
        "punctuation.special": Style(color="#6a737d"),
        "string.escape": Style(color="#e17100"),
    },
)

# Textual Ansi (Terminal colors) TextAreaTheme
textual_ansi_markdown = TextAreaTheme(
    name="textual-ansi",
    base_style=Style(color="bright_white", bgcolor="black"),
    gutter_style=Style(color="bright_black", bgcolor="black"),
    cursor_style=Style(color="black", bgcolor="bright_blue"),
    cursor_line_style=Style(bgcolor="rgb(20,20,20)"),
    selection_style=Style(bgcolor="blue"),
    syntax_styles={
        "heading": Style(color="bright_blue", bold=True),
        "heading.marker": Style(color="blue", dim=True),
        "text.literal": Style(color="bright_green", bgcolor="rgb(20,20,20)"),
        "link.uri": Style(color="bright_magenta", underline=True),
        "link.label": Style(color="magenta"),
        "list.marker": Style(color="bright_yellow"),
        "punctuation.delimiter": Style(color="bright_black"),
        "punctuation.special": Style(color="bright_black"),
        "string.escape": Style(color="yellow"),
    },
)

# Map theme names to TextAreaTheme objects
MARKDOWN_THEMES = {
    # Custom app themes
    "catppuccin-mocha": catppuccin_mocha_markdown,
    "nord": nord_markdown,
    "gruvbox": gruvbox_markdown,
    "tokyo-night": tokyo_night_markdown,
    "solarized-light": solarized_light_markdown,
    "tailwind-dark": tailwind_dark_markdown,
    "tailwind-light": tailwind_light_markdown,
    # Textual built-in themes
    "textual-dark": textual_dark_markdown,
    "textual-light": textual_light_markdown,
    "textual-ansi": textual_ansi_markdown,
}


def register_markdown_language(textarea, theme_name: str = "catppuccin-mocha"):
    """Register markdown language with a TextArea and apply theme.

    Args:
        textarea: The TextArea widget to register markdown with.
        theme_name: The name of the theme to apply (default: "catppuccin-mocha").
    """
    # Get markdown language and highlight query
    markdown_lang = get_markdown_language()
    highlight_query = get_markdown_highlight_query()

    # Register the language
    textarea.register_language("markdown", markdown_lang, highlight_query)

    # Get the appropriate theme
    theme = MARKDOWN_THEMES.get(theme_name, catppuccin_mocha_markdown)

    # Register the theme
    textarea.register_theme(theme)

    # Set the language and theme
    textarea.language = "markdown"
    # Use the actual theme name from the TextAreaTheme object
    textarea.theme = theme.name
