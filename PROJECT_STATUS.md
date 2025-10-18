# Todo TUI - Project Status

## Overview
A Terminal User Interface (TUI) todo application built with Textual Python framework. This document tracks all completed work and remaining tasks.

---

## ✅ Completed Work

### Initial Setup & Bug Fixes
Fixed multiple critical errors that prevented the app from running:

1. **DuplicateIds Errors** - Removed IDs from dynamically created widgets in:
   - `task_detail.py` - Placeholder widget and ListView items
   - `task_list.py` - ListItem widgets (switched to index-based lookup)
   - `project_list.py` - ListItem widgets (switched to index-based lookup)

2. **CSS Undefined Variables** - Replaced undefined variables in `dialogs.py`:
   - `$surface0` → `#313244`
   - `$blue` → `#89b4fa`
   - `$red` → `#f38ba8`

3. **NoActiveWorker Error** - Converted from async/await pattern to callback pattern:
   - Removed `@work` decorator (doesn't exist in Textual 6.2.1)
   - Changed `await push_screen()` to callback-based `push_screen(dialog, callback)`
   - Updated all action methods in `app.py`

4. **MountError Fixes** - Fixed widget mounting order:
   - Mount containers FIRST, then add children to them
   - Applied to button containers, ListViews, and other dynamic widgets

5. **AttributeError in EditTaskDialog** - Renamed `self.task` to `self.edit_task`:
   - ModalScreen has a property `task` that returns asyncio.Task
   - Avoids name collision

### Layout Reorganization
Changed from 3-column to 2-column layout for better space utilization:

**Before:**
```
[Projects 30%] [Tasks 35%] [Task Detail 35%]
```

**After:**
```
[Projects 33%     ] [Task Detail 67%]
[  (40% height)   ]
[Tasks 33%        ]
[  (60% height)   ]
```

**Files Modified:**
- `app.py:53-57` - Updated compose() with Vertical container for left column
- `theme.css` - Adjusted widths and heights for new layout

### Subtask Management
Implemented interactive subtask features:

1. **In Task Detail Panel** (`task_detail.py`):
   - Click/select subtask to toggle completion
   - Created `SubtaskToggled` message for app communication
   - Uses index-based selection

2. **In Edit Task Dialog** (`dialogs.py`):
   - Interactive ListView with keyboard shortcuts
   - Enter: Add new subtask (in input field)
   - Space: Toggle subtask completion
   - Delete: Remove subtask
   - Click/select: Toggle completion

---

## 🚀 Sprint 1: Essential CRUD Operations (COMPLETED)

### 1. Edit Project Name
**Location:** `dialogs.py:284-341`
**Trigger:** Press `e` when project is selected in projects panel

**Implementation:**
- Created `EditProjectDialog` with Input field pre-filled with current name
- Added `action_edit_project()` in `app.py:277-296`
- Updates storage and refreshes project list
- Context-aware keybinding via `on_key()` handler

### 2. Delete Project with Task Migration
**Location:** `app.py:298-350`
**Trigger:** Press `Delete` when project is selected

**Features:**
- Prevents deleting the last project (requires at least 1)
- Shows confirmation dialog with migration info
- Automatically migrates tasks to first remaining project
- Updates `task.project_id` for all tasks in deleted project
- Switches to "All Tasks" view after deletion

### 3. Move Task to Different Project
**Location:** `dialogs.py:387-465`, `app.py:352-383`
**Trigger:** Press `m` when task is selected in task list

**Implementation:**
- Created `MoveTaskDialog` showing available projects
- Excludes current project from list
- Updates task's `project_id` on move
- Refreshes task list and clears detail panel
- Context-aware keybinding for 'm' key

### 4. Context-Aware Keybindings
**Location:** `app.py:385-417`

**Implementation:**
- Added `on_key()` handler that checks focused widget's parent
- Different actions based on which panel has focus:

**Projects Panel:**
- `e` → Edit project name
- `Delete` → Delete project

**Task List Panel:**
- `m` → Move task to another project
- `Enter` → Edit task (global binding)
- `Space` → Toggle completion (global binding)
- `Delete` → Delete task (global binding)

---

## 🎨 Sprint 2: Enhanced UX (COMPLETED)

### 1. Project Dropdown in EditTaskDialog
**Location:** `dialogs.py:110-140`, `app.py:204`

**Features:**
- Select widget showing all projects
- Pre-selects task's current project
- Updates task's `project_id` when saved
- Handles project changes gracefully:
  - If moved out of current project view, clears detail panel
  - Otherwise updates detail panel with edited task

**Implementation:**
- Added `projects` parameter to `EditTaskDialog.__init__()`
- Created Select widget with `(project.name, project.id)` tuples
- Updated save handler to capture selected project

### 2. Task Counts in Project List
**Location:** `project_list.py:48-83`

**Features:**
- Shows format: `📁 Project Name (completed/total)`
- Example: `📁 Personal (2/5)` means 2 of 5 tasks completed
- "All Tasks" shows aggregate counts
- Updates automatically when tasks change

**Implementation:**
- Added `all_tasks` attribute to `ProjectListPanel`
- Created `update_tasks()` method called from `app.py` after task operations
- Changed to index-based selection (removed IDs to avoid duplicates)
- `_update_list()` calculates counts for each project

### 3. Help Dialog with Keyboard Shortcuts
**Location:** `dialogs.py:492-586`, `app.py:439-441`

**Sections:**
- **General:** Ctrl+N, Ctrl+P, ?, q
- **Tasks:** Enter, Space, Delete, m
- **Projects:** e, Delete
- **Subtasks:** Enter, Space, Delete
- **Navigation:** Tab, ↑/↓

**Styling:**
- Catppuccin mocha colors
- Bold yellow highlighting for keys (`.key` class)
- Clear sectioned layout
- Close button to dismiss

---

## 📋 Remaining Work (Sprint 3 - Optional Polish)

### 1. Selection Indicator Styling
**Suggested Implementation:**
- Add visual highlight for selected project in project list
- Add visual highlight for selected task in task list
- Use background color or border to indicate focus
- Update CSS with focused item styles

**Files to Modify:**
- `theme.css` - Add styles for selected/focused items
- Possibly `project_list.py` and `task_list.py` if custom styling needed

### 2. Empty State Messages
**When to Show:**
- No tasks in current project: "No tasks yet. Press Ctrl+N to add one!"
- No projects: "No projects yet. Press Ctrl+P to add one!"
- No subtasks: "No subtasks yet. Add one in the edit dialog."

**Files to Modify:**
- `task_list.py` - Add empty state display
- `project_list.py` - Add empty state display
- `task_detail.py` - Add empty state for subtasks

### 3. Tab Focus Cycling Improvements
**Current Behavior:**
- Tab cycles through all widgets including internal dialog widgets

**Desired Behavior:**
- Tab should cycle only between main panels: Projects → Tasks → Detail
- Skip internal widgets unless in a dialog

**Implementation:**
- Override focus cycling behavior
- Define explicit focus order for main panels
- Possibly use `can_focus` attribute on certain widgets

### 4. Dashboard Improvements (if needed)
**Current State:**
- Dashboard shows task overview and time
- May need styling updates or additional metrics

**Potential Enhancements:**
- Add project count
- Add completion percentage
- Add today's tasks count
- Visual progress bars

### 5. Additional Enhancements (Low Priority)
- **Confirmation for destructive actions:** Already implemented for delete project/task
- **Keyboard shortcut cheat sheet:** Already implemented as Help dialog
- **Task sorting options:** By date, priority, completion status
- **Task filtering:** Show only incomplete, only completed, etc.
- **Due dates:** Add due date field to tasks
- **Priority levels:** High, medium, low priority
- **Search/filter:** Quick search across tasks
- **Undo/redo:** For accidental deletions
- **Export/import:** JSON or CSV export

---

## 🏗️ Architecture Notes

### Framework
- **Textual 6.2.1** - Python TUI framework
- Reactive, event-driven programming model
- CSS-like styling
- Message-based component communication

### Key Patterns Used

**1. Callback Pattern (Not Async/Await):**
```python
def action_add_task(self) -> None:
    def check_add_task(result: Optional[Task]) -> None:
        if result:
            self.storage.add_task(result)
            self._load_all_tasks()
    self.push_screen(AddTaskDialog(project_id), check_add_task)
```

**2. Message-Based Communication:**
- `ProjectSelected` - When project is clicked
- `TaskSelected` - When task is clicked
- `SubtaskToggled` - When subtask is toggled
- Messages bubble up from widgets to app

**3. Index-Based Lookup (Avoid Duplicate IDs):**
```python
list_view = event.list_view
index = list_view.index
if index is not None and 0 <= index < len(items):
    item = items[index]
```

**4. Mount-Then-Populate:**
```python
# Wrong - will error
container = Horizontal()
container.mount(Button(...))  # Error!
content.mount(container)

# Correct
container = Horizontal()
content.mount(container)  # Mount first
container.mount(Button(...))  # Then populate
```

### File Structure
```
todo-tui/
├── main.py                    # Entry point
├── todo_tui/
│   ├── app.py                # Main app logic & coordination
│   ├── models.py             # Task, Project, Subtask dataclasses
│   ├── storage.py            # JSON file storage manager
│   ├── theme.css             # Global styles
│   └── widgets/
│       ├── dashboard.py      # Overview metrics
│       ├── dialogs.py        # All modal dialogs
│       ├── project_list.py   # Project list panel
│       ├── task_list.py      # Task list panel
│       ├── task_detail.py    # Task detail panel
│       └── clock_widget.py   # Time display
```

### Storage
- Each project stored as separate JSON file: `projects/{project_id}.json`
- Project metadata in `projects/index.json`
- Uses dataclasses with `asdict()` and manual parsing

---

## 🐛 Known Issues & Technical Debt

### 1. Dashboard Empty on Load
The dashboard panels appear empty in the terminal output. May need debugging of:
- `dashboard.py` - Check if widgets are mounting correctly
- Dashboard data loading in `app.py:on_mount()`

### 2. Error Handling
Currently uses broad `try/except` blocks. Should be more specific:
- Handle specific storage errors
- Validate user input more thoroughly
- Show user-friendly error messages

### 3. No Persistence of UI State
- Selected project not remembered between sessions
- Panel focus not restored
- Could save in a config file

### 4. TODO Comments in Code
Search for `# TODO:` to find inline notes:
- `app.py:305` - Show error message when trying to delete last project
- `app.py:359` - Show error message when trying to move task without project

---

## 📝 Development Guidelines

### Running the App
```bash
# Install dependencies
uv sync

# Run the app
uv run python main.py

# With Textual devtools (in separate terminals)
textual console
textual run --dev main.py
```

### Common Errors & Solutions

**DuplicateIds Error:**
- Never add IDs to dynamically created widgets
- Use index-based lookup instead

**MountError:**
- Mount containers before populating them
- Check that widgets are mounted before querying them

**AttributeError on ModalScreen.task:**
- Don't use `self.task` - it's reserved by asyncio
- Use a different name like `self.edit_task`

**NoActiveWorker:**
- Don't use `@work` decorator
- Don't use `await push_screen(..., wait_for_dismiss=True)`
- Use callback pattern instead

### Adding New Features

**1. New Dialog:**
```python
class MyDialog(ModalScreen):
    DEFAULT_CSS = """..."""

    def compose(self) -> ComposeResult:
        with Container(id="dialog-container"):
            yield Label("Title")
            # ... widgets ...
            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", id="btn-cancel")
                yield Button("OK", id="btn-ok")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-ok":
            self.dismiss(result_value)
```

**2. New Action in App:**
```python
def action_my_action(self) -> None:
    def check_result(result):
        if result:
            # Handle result
            pass
    self.push_screen(MyDialog(), check_result)
```

**3. New Keybinding:**
Add to `BINDINGS` in `app.py`:
```python
Binding("key", "action_name", "Description")
```

---

## 🎯 Next Session Priorities

If continuing development, suggested order:

1. **Fix Dashboard Display** - Ensure metrics show properly
2. **Add Empty States** - Better UX when no data exists
3. **Selection Indicators** - Visual feedback for current selection
4. **Tab Focus Cycling** - Improve keyboard navigation
5. **Additional Features** - Based on user needs

---

## 📊 Statistics

**Total Files Modified:** 8
- `app.py`
- `dialogs.py`
- `project_list.py`
- `task_list.py`
- `task_detail.py`
- `theme.css`
- `models.py` (if updated)
- `storage.py` (if updated)

**Total Features Implemented:**
- ✅ 8 Major features (bug fixes, layout, subtasks)
- ✅ 4 Sprint 1 features (CRUD operations)
- ✅ 3 Sprint 2 features (enhanced UX)

**Total Lines of Code Added:** ~500-700 lines (estimated)

---

## 📚 Resources

- [Textual Documentation](https://textual.textualize.io/)
- [Textual Widget Gallery](https://textual.textualize.io/widget_gallery/)
- [Catppuccin Mocha Colors](https://github.com/catppuccin/catppuccin)

---

*Last Updated: 2025-10-18*
*Status: Sprint 1 & 2 Complete, Sprint 3 Optional*
