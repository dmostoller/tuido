"""Scratchpad panel widget for markdown notes."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.timer import Timer
from textual.widgets import (
    Button,
    Label,
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
        border: solid $panel;
        background: $surface;
        padding: 0;
    }

    #note-list-section:focus-within {
        border: solid $secondary;
    }

    #note-list-header {
        dock: top;
        height: 1;
        background: $surface;
        color: $text;
        text-style: bold;
        padding: 0;
    }

    #note-list-view {
        height: 1fr;
        width: 100%;
    }

    #note-list-buttons {
        dock: bottom;
        height: 3;
        layout: horizontal;
        align: center middle;
        background: $surface;
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
        border: solid $panel;
        background: $surface;
    }

    #scratchpad-content-tabs:focus-within {
        border: solid $secondary;
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
        height: 100%;
        width: 100%;
        background: $surface;
        border: none;
        padding: 1;
    }

    #scratchpad-textarea:focus {
        border: none;
    }

    #scratchpad-markdown-viewer {
        height: 100%;
        width: 100%;
        background: $surface;
        padding: 1;
        overflow-y: auto;
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

    def compose(self) -> ComposeResult:
        """Compose the scratchpad panel layout."""
        # Left column: Note list
        with Vertical(id="note-list-section"):
            yield Label(f"{Icons.LIST} Notes", id="note-list-header")
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
            with TabPane(f"{Icons.FILE} Preview", id="preview-tab"):
                with Vertical(id="preview-container"):
                    yield Markdown("", id="scratchpad-markdown-viewer")

    def on_mount(self) -> None:
        """Load notes when widget is mounted."""

        # Set up markdown syntax highlighting after widget is fully initialized
        def setup_markdown():
            textarea = self.query_one("#scratchpad-textarea", TextArea)
            register_markdown_language(textarea, "catppuccin-mocha")

        # Defer markdown setup until after refresh
        self.call_after_refresh(setup_markdown)

        # Load all notes
        self.notes = self.storage.load_notes()
        self._update_note_list()

        # Select first note if available
        if self.notes:
            self._select_note(self.notes[0])

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
        # Reload notes from storage
        self.notes = self.storage.load_notes()

        # Update the list view
        self._update_note_list()

        # Select first note if available, otherwise clear the editor
        if self.notes:
            self._select_note(self.notes[0])
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
        self.current_note = note

        # Update editor content
        textarea = self.query_one("#scratchpad-textarea", TextArea)
        textarea.text = note.content

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
        self._debounce_timer = None

        # Refresh note list to update timestamp
        self._update_note_list()

    def action_add_note(self) -> None:
        """Show dialog to add a new note."""

        def check_add_note(result: Optional[Note]) -> None:
            """Callback when dialog is dismissed."""
            if result:
                # Save note
                self.storage.add_note(result)

                # Reload notes
                self.notes = self.storage.load_notes()
                self._update_note_list()

                # Select the new note
                self._select_note(result)

                # Update list selection
                list_view = self.query_one("#note-list-view", ListView)
                list_view.index = len(self.notes) - 1

        self.app.push_screen(AddNoteDialog(), check_add_note)

    def action_rename_note(self) -> None:
        """Show dialog to rename the current note."""
        if not self.current_note:
            return

        def check_rename_note(result: Optional[Note]) -> None:
            """Callback when dialog is dismissed."""
            if result:
                # Save updated note
                self.storage.update_note(result)

                # Reload notes
                self.notes = self.storage.load_notes()
                self._update_note_list()

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
                # Delete note
                self.storage.delete_note(note_to_delete.id)

                # Reload notes
                self.notes = self.storage.load_notes()
                self._update_note_list()

                # Select first note
                if self.notes:
                    self._select_note(self.notes[0])
                    list_view = self.query_one("#note-list-view", ListView)
                    list_view.index = 0

        self.app.push_screen(
            ConfirmDialog(f"Delete note '{note_to_delete.title}'?"),
            check_delete_note,
        )

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
