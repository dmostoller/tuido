# TUI Todo Application - Implementation Plan

## Project Vision

A beautiful, btop-inspired terminal UI todo application with Catppuccin Mocha theming, featuring a dashboard with metrics, project organization, and both keyboard and mouse support.

## Architecture Overview

### Core Components

1. **Data Layer** - JSON-based storage with one file per project
2. **UI Layer** - Textual widgets with custom styling
3. **State Management** - Reactive data models using Textual's reactivity
4. **Theme System** - Catppuccin Mocha color palette

## Implementation Phases

### Phase 1: Foundation & Data Layer ✅ COMPLETE

- [x] Set up project structure
- [x] Create data models (Task, Project, TodoList)
- [x] Implement JSON storage manager
- [x] Add configuration for data directory
- [x] Create sample data for testing

### Phase 2: Basic UI Framework ✅ COMPLETE

- [x] Create main App class with layout
- [x] Implement Catppuccin Mocha CSS theme
- [x] Build project sidebar widget
- [x] Build task list widget
- [x] Build task detail panel widget
- [x] Add basic keyboard navigation (arrow keys, tab)

### Phase 3: Core Task Operations ✅ COMPLETE

- [x] Quick add dialog (global hotkey: Ctrl+N)
- [x] Create task functionality
- [x] Edit task functionality
- [x] Delete task functionality
- [x] Mark task as complete/incomplete
- [x] Auto-save on every change
- [x] Test all task operations work correctly

### Phase 4: Subtasks & Projects ✅ COMPLETE

- [x] Subtask checklist UI (basic structure)
- [x] Add/remove subtasks
- [x] Auto-complete parent when all subtasks done
- [x] Create new project functionality (Ctrl+P)
- [x] Delete project functionality (with error handling)
- [x] Switch between projects

### Phase 5: Dashboard & Metrics ✅ COMPLETE

- [x] Metrics cards widget (total, completed, completion %)
- [x] Tasks per project breakdown
- [x] Tasks completed over time chart
- [x] Time-based filters (today, this week)
- [x] "All Tasks" view across projects

### Phase 6: Enhanced UX ✅ COMPLETE

- [x] Mouse click support for all actions
- [x] Search/filter tasks (by title and description, Ctrl+F or /)
- [x] Task priority system (high/medium/low with bookmark icons)
- [x] Visual states (hover, selected, completed, enhanced highlighting)
- [x] Empty states for projects and subtasks
- [ ] Sort options (alphabetical, creation date) - deferred

### Phase 7: Polish & Optimization ✅ COMPLETE

- [x] Smooth animations and transitions (task toggle pulse, dashboard updates)
- [x] Error handling and validation (ErrorDialog, InfoDialog components)
- [x] Tab navigation improvements (leveraging Textual's built-in focus cycling)
- [x] Performance optimization for large task lists
- [ ] State persistence (remember last project/view) - deferred
- [ ] Loading states and feedback - deferred

## Technical Decisions

### Data Storage

- **Format**: JSON (optimal for structured data, easy to parse)
- **Structure**:
  - `data/projects.json` - Project metadata
  - `data/{project_id}.json` - Tasks per project
  - Auto-create data directory if missing


## File Structure

```
todo-tui/
├── main.py                 # Entry point
├── todo_tui/
│   ├── __init__.py
│   ├── app.py             # Main Textual App
│   ├── models.py          # Data models
│   ├── storage.py         # JSON storage manager
│   ├── theme.css          # Catppuccin Mocha theme
│   └── widgets/
│       ├── __init__.py
│       ├── dashboard.py   # Dashboard panel
│       ├── project_list.py
│       ├── task_list.py
│       ├── task_detail.py
│       └── dialogs.py     # Quick add, confirm, etc.
├── data/                  # Auto-created for storage
├── IMPLEMENTATION.md      # This file
└── pyproject.toml
```

## Current Status

### What's Working

- ✅ Beautiful Catppuccin Mocha themed UI
- ✅ Dashboard showing task metrics (total, completed, completion rate, today, this week)
- ✅ Project list with "All Tasks" view and task counts
- ✅ Task list display with completion indicators
- ✅ Task detail panel with priority and subtask information
- ✅ JSON data persistence with auto-save
- ✅ Default "Personal" project created on first run
- ✅ Full keyboard navigation (arrow keys, tab, shortcuts)
- ✅ Quick add dialog (Ctrl+N)
- ✅ Edit task dialog with priority selector
- ✅ Delete task with confirmation
- ✅ Toggle task completion with animation
- ✅ Search/filter tasks (Ctrl+F or /)
- ✅ Priority system (high/medium/low with colored bookmark icons)
- ✅ Subtask management (add/remove/toggle)
- ✅ Auto-complete parent task when all subtasks done
- ✅ Project creation and deletion with validation
- ✅ Error dialogs and user feedback (ErrorDialog, InfoDialog)
- ✅ Empty states for projects and subtasks
- ✅ Enhanced visual highlighting for selected items
- ✅ Smooth animations (task toggle, dashboard updates)

### What Needs Work (Optional Future Enhancements)

- ⏳ Help screen (?) - keyboard shortcuts reference
- ⏳ State persistence (remember last project/view)
- ⏳ Sort options (alphabetical, creation date, priority)
- ⏳ Loading states and feedback for async operations
- ⏳ Export/import functionality
- ⏳ Task due dates and reminders

## Running the Application

```bash
# Using uv (recommended)
uv run python main.py

# Or if dependencies are installed
python main.py

# With Textual devtools for debugging
textual console
# In another terminal:
textual run --dev main.py
```

## Success Criteria ✅ ALL ACHIEVED

- ✅ Beautiful, cohesive Catppuccin Mocha UI
- ✅ Fast and responsive (keyboard + mouse)
- ✅ All CRUD operations work smoothly
- ✅ Dashboard provides useful insights
- ✅ Data persists reliably
- ✅ Intuitive UX that speeds up daily workflow

## Next Steps (Optional Enhancements)

1. ✅ **Core functionality complete!** The app is fully functional and ready for daily use.
2. Future enhancements could include:
   - Help screen showing all keyboard shortcuts
   - State persistence to remember last selected project
   - Additional sort options (alphabetical, by priority)
   - Task due dates and reminders
   - Export/import functionality
   - Recurring tasks
   - Tags and labels
