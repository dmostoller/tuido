"""Snippets panel widget for managing code snippets."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

import pyperclip
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.widgets import Button, Input, Label, ListItem, ListView, Static, TextArea

from ..icons import Icons
from ..models import Snippet
from .dialogs import AddSnippetDialog, ConfirmDialog, EditSnippetDialog

if TYPE_CHECKING:
    from ..storage import StorageManager


def escape_markup(text: str) -> str:
    """Escape Rich markup characters to prevent markup injection.

    Args:
        text: Text that may contain markup characters

    Returns:
        Text with markup characters escaped
    """
    return text.replace("[", "[[").replace("]", "]]")


class SnippetSelected(Message):
    """Message sent when a snippet is selected."""

    def __init__(self, snippet: Optional[Snippet]):
        super().__init__()
        self.snippet = snippet


class SnippetsPanel(Container):
    """Panel for managing and copying code snippets."""

    DEFAULT_CSS = """
    SnippetsPanel {
        width: 100%;
        height: 100%;
        layout: horizontal;
    }

    #snippet-list-section {
        width: 30%;
        height: 100%;
        border: round $panel;
        background: $background;
        padding: 0;
    }

    #snippet-list-section:focus-within {
        border: round $secondary;
    }

    #snippet-list-header {
        dock: top;
        height: 1;
        background: $background;
        color: $text;
        text-style: bold;
        padding: 0 1;
    }

    #snippet-search-input {
        dock: top;
        width: 100%;
        margin: 0 1;
    }

    #snippet-list-view {
        height: 1fr;
        width: 100%;
    }

    #snippet-list-buttons {
        dock: bottom;
        height: 3;
        layout: horizontal;
        align: left middle;
        background: $background;
        padding: 0 1;
    }

    .snippet-action-btn {
        min-width: 6;
        margin: 0 1;
    }

    .snippet-list-item {
        padding: 0 1;
    }

    #snippet-detail-section {
        width: 70%;
        height: 100%;
        border: round $panel;
        background: $background;
        padding: 0;
    }

    #snippet-detail-section:focus-within {
        border: round $secondary;
    }

    #snippet-detail-header {
        dock: top;
        height: 1;
        text-style: bold;
        color: $primary;
        padding: 0 0 1 0;
    }

    #snippet-detail-meta {
        dock: top;
        height: 1;
        color: $text-muted;
        padding: 0 0 1 0;
    }

    #snippet-code-display {
        height: 1fr;
        width: 100%;
        background: $background;
        border: round $panel;
        padding: 1;
    }

    #snippet-detail-buttons {
        dock: bottom;
        height: 3;
        layout: horizontal;
        align: right middle;
        background: $background;
        padding: 0 1;
    }

    .empty-state {
        height: 100%;
        width: 100%;
        align: center middle;
        text-align: center;
        color: $text-muted;
        text-style: italic;
    }
    """

    BINDINGS = [
        Binding("enter", "copy_snippet", "Copy", show=True),
        Binding("a", "add_snippet", "Add", show=True),
        Binding("e", "edit_snippet", "Edit", show=True),
        Binding("d", "delete_snippet", "Delete", show=True),
        Binding("/", "focus_search", "Search", show=True),
        Binding("escape", "clear_search", "Clear", show=False),
    ]

    def __init__(self, storage: StorageManager, id: str = "snippets-panel") -> None:
        """Initialize the snippets panel.

        Args:
            storage: Storage manager for loading/saving snippets
            id: Widget ID
        """
        super().__init__(id=id)
        self.storage = storage
        self.snippets: List[Snippet] = []
        self.filtered_snippets: List[Snippet] = []
        self.current_snippet: Optional[Snippet] = None
        self.search_query: str = ""

    def compose(self) -> ComposeResult:
        """Compose the snippets panel layout."""
        # Left column: Snippet list
        with Vertical(id="snippet-list-section"):
            yield Label(f"{Icons.CODE} Snippets", id="snippet-list-header")
            yield Input(
                placeholder=f"{Icons.SEARCH} Search...",
                id="snippet-search-input",
            )
            yield ListView(id="snippet-list-view")
            with Horizontal(id="snippet-list-buttons"):
                yield Button(
                    f"{Icons.PLUS}",
                    id="btn-add-snippet",
                    variant="success",
                    classes="snippet-action-btn",
                )
                yield Button(
                    f"{Icons.PENCIL}",
                    id="btn-edit-snippet",
                    variant="default",
                    classes="snippet-action-btn",
                )
                yield Button(
                    f"{Icons.TRASH}",
                    id="btn-delete-snippet",
                    variant="error",
                    classes="snippet-action-btn",
                )

        # Right column: Snippet detail view
        with Vertical(id="snippet-detail-section"):
            yield Label("Select a snippet to view", id="snippet-detail-header")
            yield Static("", id="snippet-detail-meta")
            yield TextArea(
                "",
                read_only=True,
                show_line_numbers=True,
                id="snippet-code-display",
            )
            with Horizontal(id="snippet-detail-buttons"):
                yield Button(
                    f"{Icons.COPY} Copy to Clipboard",
                    id="btn-copy-clipboard",
                    variant="primary",
                )

    def on_mount(self) -> None:
        """Initialize after widget is mounted."""
        self.snippets = self.storage.load_snippets()
        self._update_list()

        # Show first snippet in detail view if available
        if self.filtered_snippets:
            self.current_snippet = self.filtered_snippets[0]
            self._update_detail_view(self.current_snippet)
            # Select first item in list
            list_view = self.query_one("#snippet-list-view", ListView)
            list_view.index = 0
        else:
            self._clear_detail_view()

    def _sort_snippets(self, snippets: List[Snippet]) -> List[Snippet]:
        """Sort snippets by usage count (descending).

        Args:
            snippets: List of snippets to sort

        Returns:
            Sorted list of snippets
        """
        return sorted(snippets, key=lambda s: s.uses, reverse=True)

    def _get_snippet_at_index(self, index: Optional[int]) -> Optional[Snippet]:
        """Get snippet at index if valid.

        Args:
            index: List index to check

        Returns:
            Snippet at index or None if invalid
        """
        if index is not None and 0 <= index < len(self.filtered_snippets):
            return self.filtered_snippets[index]
        return None

    def _filter_snippets(self) -> None:
        """Filter snippets based on search query."""
        if not self.search_query:
            self.filtered_snippets = self.snippets
        else:
            query = self.search_query.lower()
            self.filtered_snippets = [
                s
                for s in self.snippets
                if query in s.name.lower()
                or query in s.command.lower()
                or any(query in tag.lower() for tag in (s.tags or []))
            ]

    def _update_list(self) -> None:
        """Update the snippet list view."""
        # Filter first, then sort the filtered results
        self._filter_snippets()
        self.filtered_snippets = self._sort_snippets(self.filtered_snippets)

        # Get list view
        list_view = self.query_one("#snippet-list-view", ListView)
        list_view.clear()

        # Show empty state if no snippets
        if not self.filtered_snippets:
            if self.search_query:
                empty_msg = f"No snippets found for '{self.search_query}'"
            else:
                empty_msg = "No snippets yet. Press 'a' to add one!"
            list_view.append(
                ListItem(Static(empty_msg, classes="empty-state"), disabled=True)
            )
            return

        # Populate list with snippets
        for snippet in self.filtered_snippets:
            # Format tags
            tags_str = (
                " ".join(f"#{tag}" for tag in snippet.tags) if snippet.tags else ""
            )

            # Format usage count
            uses_str = f"({snippet.uses})" if snippet.uses > 0 else "(0)"

            # Create snippet item display with markup
            meta = f"{tags_str}  {uses_str}" if tags_str else uses_str
            # Escape snippet name to prevent markup injection
            escaped_name = escape_markup(snippet.name)
            content = Static(
                f"[bold]{Icons.CODE} {escaped_name}[/]\n[dim]{meta}[/]",
                classes="snippet-list-item",
                markup=True,
            )
            list_view.append(ListItem(content))

    def _update_detail_view(self, snippet: Snippet) -> None:
        """Update the detail view with the selected snippet.

        Args:
            snippet: The snippet to display
        """
        # Update header with snippet name (escape to prevent markup injection)
        header = self.query_one("#snippet-detail-header", Label)
        escaped_name = escape_markup(snippet.name)
        header.update(f"{Icons.CODE} {escaped_name}")

        # Update metadata
        meta = self.query_one("#snippet-detail-meta", Static)
        tags_str = " ".join(f"#{tag}" for tag in snippet.tags) if snippet.tags else ""

        # Format dates
        try:
            created = datetime.fromisoformat(snippet.created_at)
            created_str = created.strftime("%b %d, %Y")
        except Exception:
            created_str = "Unknown"

        last_used_str = ""
        if snippet.last_used:
            try:
                last_used = datetime.fromisoformat(snippet.last_used)
                last_used_str = f" • Last used: {last_used.strftime('%b %d, %H:%M')}"
            except Exception:
                pass

        meta_text = f"{tags_str}  •  Used {snippet.uses} times  •  Created: {created_str}{last_used_str}"
        meta.update(meta_text)

        # Update code display
        code_display = self.query_one("#snippet-code-display", TextArea)
        code_display.text = snippet.command

    def _clear_detail_view(self) -> None:
        """Clear the detail view when no snippet is selected."""
        header = self.query_one("#snippet-detail-header", Label)
        header.update("Select a snippet to view")

        meta = self.query_one("#snippet-detail-meta", Static)
        meta.update("")

        code_display = self.query_one("#snippet-code-display", TextArea)
        code_display.text = ""

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle snippet selection.

        Args:
            event: Selection event
        """
        if event.list_view.id != "snippet-list-view":
            return

        # Get selected snippet
        snippet = self._get_snippet_at_index(event.list_view.index)
        if snippet:
            self.current_snippet = snippet
            self._update_detail_view(snippet)
            self.post_message(SnippetSelected(snippet))

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes (real-time filtering).

        Args:
            event: Input change event
        """
        if event.input.id != "snippet-search-input":
            return

        self.search_query = event.value
        self._update_list()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: Button press event
        """
        if event.button.id == "btn-add-snippet":
            self.action_add_snippet()
        elif event.button.id == "btn-edit-snippet":
            self.action_edit_snippet()
        elif event.button.id == "btn-delete-snippet":
            self.action_delete_snippet()
        elif event.button.id == "btn-copy-clipboard":
            self.action_copy_snippet()

    def action_copy_snippet(self) -> None:
        """Copy selected snippet to clipboard."""
        if not self.current_snippet:
            self.app.notify("No snippet selected", severity="warning")
            return

        try:
            # Copy to clipboard
            pyperclip.copy(self.current_snippet.command)

            # Update usage stats
            self.current_snippet.uses += 1
            self.current_snippet.last_used = datetime.now().isoformat()

            # Save to storage
            self.storage.update_snippet(self.current_snippet)

            # Reload and refresh list (to re-sort)
            self.snippets = self.storage.load_snippets()
            self._update_list()

            # Refresh detail view to show updated usage count
            self._update_detail_view(self.current_snippet)

            # Show success notification
            preview = self.current_snippet.command[:50]
            if len(self.current_snippet.command) > 50:
                preview += "..."
            self.app.notify(f"✓ Copied: {preview}", severity="information")

        except Exception as e:
            self.app.notify(f"Failed to copy to clipboard: {str(e)}", severity="error")

    def action_add_snippet(self) -> None:
        """Show dialog to add a new snippet."""

        def check_add_snippet(snippet: Optional[Snippet]) -> None:
            if snippet:
                # Save snippet
                self.storage.add_snippet(snippet)

                # Reload and refresh list
                self.snippets = self.storage.load_snippets()
                self._update_list()

                # Select and show the new snippet
                self.current_snippet = snippet
                self._update_detail_view(snippet)

                self.app.notify(
                    f"Snippet '{snippet.name}' added successfully",
                    severity="information",
                )

        self.app.push_screen(AddSnippetDialog(), check_add_snippet)

    def action_edit_snippet(self) -> None:
        """Show dialog to edit the selected snippet."""
        if not self.current_snippet:
            self.app.notify("No snippet selected", severity="warning")
            return

        def check_edit_snippet(snippet: Optional[Snippet]) -> None:
            if snippet:
                # Save snippet
                self.storage.update_snippet(snippet)

                # Reload and refresh list
                self.snippets = self.storage.load_snippets()
                self._update_list()

                # Refresh detail view with updated snippet
                self.current_snippet = snippet
                self._update_detail_view(snippet)

                self.app.notify(
                    f"Snippet '{snippet.name}' updated successfully",
                    severity="information",
                )

        self.app.push_screen(
            EditSnippetDialog(self.current_snippet), check_edit_snippet
        )

    def action_delete_snippet(self) -> None:
        """Delete the selected snippet (with confirmation)."""
        if not self.current_snippet:
            self.app.notify("No snippet selected", severity="warning")
            return

        def check_delete(confirmed: bool) -> None:
            if confirmed and self.current_snippet:
                # Delete snippet
                snippet_name = self.current_snippet.name
                self.storage.delete_snippet(self.current_snippet.id)

                # Clear selection
                self.current_snippet = None

                # Reload and refresh list
                self.snippets = self.storage.load_snippets()
                self._update_list()

                # Show first snippet or clear detail view
                first_snippet = self._get_snippet_at_index(0)
                if first_snippet:
                    self.current_snippet = first_snippet
                    self._update_detail_view(first_snippet)
                    list_view = self.query_one("#snippet-list-view", ListView)
                    list_view.index = 0
                else:
                    self._clear_detail_view()

                self.app.notify(
                    f"Snippet '{snippet_name}' deleted", severity="information"
                )

        self.app.push_screen(
            ConfirmDialog(
                f"Delete snippet '{self.current_snippet.name}'?\n\nThis cannot be undone."
            ),
            check_delete,
        )

    def action_focus_search(self) -> None:
        """Focus the search input."""
        search_input = self.query_one("#snippet-search-input", Input)
        search_input.focus()

    def action_clear_search(self) -> None:
        """Clear the search query."""
        search_input = self.query_one("#snippet-search-input", Input)
        search_input.value = ""
        self.search_query = ""
        self._update_list()

    def reload_snippets(self) -> None:
        """Reload snippets from storage and update UI.

        Called after cloud sync to refresh the panel with synced snippets.
        """
        # Reload snippets from storage
        self.snippets = self.storage.load_snippets()

        # Update the list view
        self._update_list()

        # Select first snippet if available, otherwise clear detail view
        if self.filtered_snippets:
            self.current_snippet = self.filtered_snippets[0]
            self._update_detail_view(self.current_snippet)
        else:
            self._clear_detail_view()
