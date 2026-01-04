"""Scratchpad panel widget for markdown notes."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

import pyperclip
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.css.query import NoMatches
from textual.message import Message
from textual.timer import Timer
from textual.widgets import (
    Button,
    ListItem,
    ListView,
    Markdown,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
)

from ..icons import Icons
from ..markdown_syntax import register_markdown_language
from ..models import Note
from .dialogs import AddNoteDialog, ConfirmDialog, InfoDialog, RenameNoteDialog

if TYPE_CHECKING:
    from ..storage import StorageManager


class NoteSelected(Message):
    """Message sent when a note is selected."""

    def __init__(self, note: Optional[Note]):
        super().__init__()
        self.note = note


class ScratchpadPanel(Container):
    """Panel for editing and previewing markdown notes."""

    DEFAULT_CSS = """
    ScratchpadPanel {
        width: 100%;
        height: 100%;
        layout: horizontal;
    }

    #note-list-section {
        width: 25%;
        height: 100%;
        border: round $panel;
        border-title-align: left;
        border-title-color: $primary;
        background: $background;
        padding: 1 0 0 0;
    }

    #note-list-section:focus-within {
        border: round $secondary;
    }

    #note-list-view {
        height: 1fr;
        width: 100%;
    }

    #note-list-buttons {
        dock: bottom;
        height: 3;
        layout: horizontal;
        align: left middle;
        background: $background;
        padding: 0 1;
    }

    .note-action-btn {
        min-width: 6;
        max-width: 6;
        margin: 0 1;
        text-align: center;
    }

    #scratchpad-content-tabs {
        width: 75%;
        height: 100%;
        border: round $panel;
        background: $background;
    }

    #scratchpad-content-tabs:focus-within {
        border: round $secondary;
    }

    #scratchpad-content-tabs > ContentSwitcher {
        height: 1fr;
        width: 100%;
    }

    #editor-tab {
        height: 100%;
        padding: 0;
    }

    #preview-tab {
        height: 100%;
        padding: 0;
    }

    #editor-container {
        height: 100%;
        width: 100%;
        padding: 0;
    }

    #preview-container {
        height: 100%;
        width: 100%;
        padding: 0;
    }

    #scratchpad-textarea {
        height: 1fr;
        width: 100%;
        background: $background;
        border: none;
        padding: 1;
    }

    #scratchpad-textarea:focus {
        border: none;
    }

    #editor-hint {
        dock: bottom;
        height: 1;
        width: 100%;
        background: $background;
        color: $text-muted;
        text-align: right;
        padding: 0 1;
        text-style: italic;
    }

    #scratchpad-markdown-viewer {
        height: 1fr;
        width: 100%;
        background: $background;
        padding: 1;
        overflow-y: auto;
    }

    #preview-actions {
        dock: bottom;
        height: 3;
        layout: horizontal;
        align: right middle;
        background: $background;
        padding: 0 1;
    }

    #btn-copy-all {
        min-width: 15;
        margin: 0 1;
    }

    .note-list-item {
        padding: 0 1;
    }

    .note-title {
        text-style: bold;
    }

    .note-timestamp {
        color: $text-muted;
        text-style: italic;
    }
    """

    BINDINGS = [
        Binding("ctrl+n", "add_note", "New Note", show=False),
        Binding("f2", "rename_note", "Rename Note", show=False),
        Binding("delete", "delete_note", "Delete Note", show=False),
        Binding("ctrl+shift+c", "copy_selected", "Copy Selected", show=False),
    ]

    def __init__(self, storage: StorageManager, id: str = "scratchpad-panel") -> None:
        """Initialize the scratchpad panel.

        Args:
            storage: The storage manager for loading/saving notes.
            id: The widget ID.
        """
        super().__init__(id=id)
        self.storage = storage
        self._debounce_timer: Timer | None = None
        self.notes: List[Note] = []
        self.current_note: Optional[Note] = None
        self._programmatic_change: bool = False  # Flag to suppress events

    def compose(self) -> ComposeResult:
        """Compose the scratchpad panel layout."""
        # Left column: Note list
        with Vertical(id="note-list-section"):
            yield ListView(id="note-list-view")
            with Horizontal(id="note-list-buttons"):
                yield Button(
                    f"{Icons.PLUS}",
                    id="btn-new-note",
                    variant="success",
                    classes="note-action-btn compact",
                )
                yield Button(
                    f"{Icons.PENCIL}",
                    id="btn-rename-note",
                    variant="default",
                    classes="note-action-btn compact",
                )
                yield Button(
                    f"{Icons.TRASH}",
                    id="btn-delete-note",
                    variant="error",
                    classes="note-action-btn compact",
                )

        # Right column: Tabbed content with Editor and Preview
        with TabbedContent(initial="editor-tab", id="scratchpad-content-tabs"):
            with TabPane(f"{Icons.PENCIL} Editor", id="editor-tab"):
                with Vertical(id="editor-container"):
                    yield TextArea(
                        "",
                        show_line_numbers=True,
                        id="scratchpad-textarea",
                    )
                    yield Static(
                        "Tip: Ctrl+Shift+C to copy selected text", id="editor-hint"
                    )
            with TabPane(f"{Icons.FILE} Preview", id="preview-tab"):
                with Vertical(id="preview-container"):
                    yield Markdown("", id="scratchpad-markdown-viewer")
                    with Horizontal(id="preview-actions"):
                        yield Button(
                            f"{Icons.COPY} Copy All",
                            id="btn-copy-all",
                            variant="primary",
                        )

    def on_mount(self) -> None:
        """Load notes when widget is mounted."""
        # Set up border title
        note_list_section = self.query_one("#note-list-section")
        note_list_section.border_title = f"{Icons.LIST} Notes"

        # Set up markdown syntax highlighting after widget is fully initialized
        def setup_markdown():
            textarea = self.query_one("#scratchpad-textarea", TextArea)
            # Use current app theme instead of hardcoded value
            current_theme = self.app.theme or "catppuccin-mocha"
            register_markdown_language(textarea, current_theme)

        # Defer markdown setup until after refresh
        self.call_after_refresh(setup_markdown)

        # Load all notes
        self.notes = self.storage.load_notes()
        self._update_note_list()

        # Select first note if available
        if self.notes:
            self._select_note(self.notes[0])

    def watch_app_theme(self) -> None:
        """Watch for app theme changes and update TextArea theme."""
        # This is called via app's theme watcher
        self._update_textarea_theme()

    def _update_textarea_theme(self) -> None:
        """Update the TextArea theme to match the current app theme."""
        try:
            textarea = self.query_one("#scratchpad-textarea", TextArea)
            current_theme = self.app.theme or "catppuccin-mocha"

            # Import the theme mapping
            from ..markdown_syntax import MARKDOWN_THEMES, catppuccin_mocha_markdown

            # Get the matching TextArea theme
            theme = MARKDOWN_THEMES.get(current_theme, catppuccin_mocha_markdown)

            # Register and apply the theme
            textarea.register_theme(theme)
            textarea.theme = theme.name
        except NoMatches:
            pass  # Widget might not be mounted yet

    def _update_note_list(self) -> None:
        """Update the note list view."""
        list_view = self.query_one("#note-list-view", ListView)
        list_view.clear()

        if not self.notes:
            list_view.append(
                ListItem(Static("No notes yet. Click 'New' to create one!"))
            )
            return

        for note in self.notes:
            # Format timestamp nicely
            try:
                updated = datetime.fromisoformat(note.updated_at)
                timestamp = updated.strftime("%b %d, %H:%M")
            except Exception:
                timestamp = "Unknown"

            # Create list item with title and timestamp
            content = Static(
                f"[bold]{Icons.FILE} {note.title}[/]\n[dim]{timestamp}[/]",
                classes="note-list-item",
                markup=True,
            )
            list_view.append(ListItem(content))

    def reload_notes(self) -> None:
        """Reload notes from storage and update UI.

        Called after cloud sync to refresh the scratchpad with synced notes.
        """
        # Save current note before reloading to prevent data loss
        if self.current_note:
            self._save_current_note()

        # Store current note ID to try to re-select it after reload
        current_note_id = self.current_note.id if self.current_note else None

        # Reload notes from storage
        self.notes = self.storage.load_notes()

        # Update the list view
        self._update_note_list()

        # Try to re-select the same note, or select first note if available
        note_to_select = None
        if current_note_id:
            # Try to find the same note in the reloaded list
            for note in self.notes:
                if note.id == current_note_id:
                    note_to_select = note
                    break

        # If we couldn't find the same note, select the first one
        if not note_to_select and self.notes:
            note_to_select = self.notes[0]

        if note_to_select:
            self._select_note(note_to_select)
        else:
            # Clear editor and preview if no notes
            textarea = self.query_one("#scratchpad-textarea", TextArea)
            textarea.text = ""
            markdown_viewer = self.query_one("#scratchpad-markdown-viewer", Markdown)
            markdown_viewer.update("")
            self.current_note = None

    def _select_note(self, note: Note) -> None:
        """Select and display a note.

        Args:
            note: The note to select.
        """
        # Cancel any pending timer before switching
        if self._debounce_timer is not None:
            self._debounce_timer.stop()
            self._debounce_timer = None

        self.current_note = note

        # Update editor content (suppress event handling for programmatic change)
        self._programmatic_change = True
        textarea = self.query_one("#scratchpad-textarea", TextArea)
        textarea.text = note.content
        self._programmatic_change = False

        # Update preview
        markdown_viewer = self.query_one("#scratchpad-markdown-viewer", Markdown)
        markdown_viewer.update(note.content)

        # Post message
        self.post_message(NoteSelected(note))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle note selection from list.

        Args:
            event: The selection event.
        """
        if event.list_view.id != "note-list-view":
            return

        index = event.list_view.index
        if index is not None and 0 <= index < len(self.notes):
            # Save current note before switching
            if self.current_note:
                self._save_current_note()

            self._select_note(self.notes[index])

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Handle text changes in the editor.

        Args:
            event: The text change event.
        """
        # Only handle changes from our textarea
        if event.text_area.id != "scratchpad-textarea":
            return

        # Ignore programmatic changes (when loading a note)
        if self._programmatic_change:
            return

        if not self.current_note:
            return

        # Update the markdown preview
        markdown_viewer = self.query_one("#scratchpad-markdown-viewer", Markdown)
        markdown_viewer.update(event.text_area.text)

        # Debounce save to avoid excessive writes
        # Cancel any existing timer
        if self._debounce_timer is not None:
            self._debounce_timer.stop()

        # Set new timer to save after 500ms of no typing
        self._debounce_timer = self.set_timer(0.5, lambda: self._save_current_note())

    def _save_current_note(self) -> None:
        """Save the current note's content to storage."""
        if not self.current_note:
            return

        textarea = self.query_one("#scratchpad-textarea", TextArea)
        self.current_note.content = textarea.text
        self.storage.update_note(self.current_note)

        # Properly stop and clear the debounce timer
        if self._debounce_timer is not None:
            self._debounce_timer.stop()
        self._debounce_timer = None

        # Don't refresh the list here to avoid race condition with list item clicks
        # The timestamp will be updated next time the list is naturally refreshed

    def action_add_note(self) -> None:
        """Show dialog to add a new note."""

        def check_add_note(result: Optional[Note]) -> None:
            """Callback when dialog is dismissed."""
            if result:
                # Save current note before reloading
                if self.current_note:
                    self._save_current_note()

                # Save new note
                self.storage.add_note(result)

                # Reload notes
                self.notes = self.storage.load_notes()
                self._update_note_list()

                # Find the newly added note in the reloaded list (should be last)
                if self.notes:
                    new_note = self.notes[-1]
                    self._select_note(new_note)

                    # Update list selection
                    list_view = self.query_one("#note-list-view", ListView)
                    list_view.index = len(self.notes) - 1

        self.app.push_screen(AddNoteDialog(), check_add_note)

    def action_rename_note(self) -> None:
        """Show dialog to rename the current note."""
        if not self.current_note:
            return

        # Store the note ID to find it after reload
        note_id = self.current_note.id

        def check_rename_note(result: Optional[Note]) -> None:
            """Callback when dialog is dismissed."""
            if result:
                # Save current note content before reloading
                if self.current_note:
                    self._save_current_note()

                # Save updated note
                self.storage.update_note(result)

                # Reload notes
                self.notes = self.storage.load_notes()
                self._update_note_list()

                # Re-select the renamed note from the reloaded list
                for i, note in enumerate(self.notes):
                    if note.id == note_id:
                        self._select_note(note)
                        list_view = self.query_one("#note-list-view", ListView)
                        list_view.index = i
                        break

        self.app.push_screen(RenameNoteDialog(self.current_note), check_rename_note)

    def action_delete_note(self) -> None:
        """Delete the current note after confirmation."""
        if not self.current_note:
            return

        # Don't allow deleting if it's the only note
        if len(self.notes) <= 1:
            self.app.push_screen(
                InfoDialog(
                    "Cannot delete the only note. You must have at least one note.",
                    "Cannot Delete Note",
                )
            )
            return

        note_to_delete = self.current_note

        def check_delete_note(confirmed: bool) -> None:
            """Callback when dialog is dismissed."""
            if confirmed:
                # Save current note before deletion (in case user made changes)
                if self.current_note:
                    self._save_current_note()

                # Delete note
                self.storage.delete_note(note_to_delete.id)

                # Reload notes
                self.notes = self.storage.load_notes()
                self._update_note_list()

                # Select first note from the reloaded list
                if self.notes:
                    self._select_note(self.notes[0])
                    list_view = self.query_one("#note-list-view", ListView)
                    list_view.index = 0

        self.app.push_screen(
            ConfirmDialog(f"Delete note '{note_to_delete.title}'?"),
            check_delete_note,
        )

    def action_copy_selected(self) -> None:
        """Copy selected text from the editor to clipboard."""

        textarea = self.query_one("#scratchpad-textarea", TextArea)
        selected_text = textarea.selected_text

        if not selected_text:
            self.app.notify("No text selected", severity="warning")
            return

        try:
            pyperclip.copy(selected_text)
            self.app.notify("✓ Selected text copied to clipboard", severity="success")
        except Exception as e:
            # Fallback to Textual's native clipboard (OSC 52)
            try:
                self.app.copy_to_clipboard(selected_text)
                self.app.notify("✓ Text copied (via OSC 52)", severity="success")
            except Exception:
                self.app.notify(f"Failed to copy: {str(e)}", severity="error")

    def action_copy_all(self) -> None:
        """Copy entire note content to clipboard."""

        if not self.current_note:
            self.app.notify("No note selected", severity="warning")
            return

        try:
            pyperclip.copy(self.current_note.content)
            self.app.notify("✓ Note copied to clipboard", severity="success")
        except Exception as e:
            # Fallback to Textual's native clipboard (OSC 52)
            try:
                self.app.copy_to_clipboard(self.current_note.content)
                self.app.notify("✓ Note copied (via OSC 52)", severity="success")
            except Exception:
                self.app.notify(f"Failed to copy: {str(e)}", severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: The button press event.
        """
        if event.button.id == "btn-new-note":
            self.action_add_note()
        elif event.button.id == "btn-rename-note":
            self.action_rename_note()
        elif event.button.id == "btn-delete-note":
            self.action_delete_note()
        elif event.button.id == "btn-copy-all":
            self.action_copy_all()
