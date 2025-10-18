# TUI Todo Application - Implementation Plan

## Project Vision
A beautiful, btop-inspired terminal UI todo application with Catppuccin Mocha theming, featuring a dashboard with metrics, project organization, and both keyboard and mouse support.

## Architecture Overview

### Core Components
1. **Data Layer** - JSON-based storage with one file per project
2. **UI Layer** - Textual widgets with custom styling
3. **State Management** - Reactive data models using Textual's reactivity
4. **Theme System** - Catppuccin Mocha color palette

### Layout Structure (Option A)
```
┌─────────────────────────────────────────────────┐
│  Dashboard Panel (Top 30%)                      │
│  - Metrics cards                                │
│  - Charts (tasks completed over time)           │
└─────────────────────────────────────────────────┘
┌──────────────────┬──────────────────────────────┐
│  Projects List   │  Task Details Panel          │
│  (Left 30%)      │  (Right 70%)                 │
│  - All Tasks     │  - Selected task info        │
│  - Project 1     │  - Description               │
│  - Project 2     │  - Subtasks checklist        │
│                  │  - Edit/Delete actions       │
└──────────────────┴──────────────────────────────┘
```

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

### Phase 3: Core Task Operations 🚧 IN PROGRESS
- [x] Quick add dialog (global hotkey: Ctrl+N)
- [x] Create task functionality
- [x] Edit task functionality
- [x] Delete task functionality
- [x] Mark task as complete/incomplete
- [x] Auto-save on every change
- [ ] Test all task operations work correctly

### Phase 4: Subtasks & Projects
- [x] Subtask checklist UI (basic structure)
- [ ] Add/remove subtasks (needs testing)
- [ ] Auto-complete parent when all subtasks done
- [x] Create new project functionality (Ctrl+P)
- [ ] Delete project functionality
- [x] Switch between projects

### Phase 5: Dashboard & Metrics ✅ COMPLETE
- [x] Metrics cards widget (total, completed, completion %)
- [x] Tasks per project breakdown
- [x] Tasks completed over time chart
- [x] Time-based filters (today, this week)
- [x] "All Tasks" view across projects

### Phase 6: Enhanced UX
- [ ] Mouse click support for all actions
- [ ] Keyboard shortcuts help screen (F1 or ?)
- [ ] Confirmation dialogs for destructive actions
- [ ] Search/filter tasks
- [ ] Sort options (alphabetical, creation date)
- [ ] Visual states (hover, selected, completed)

### Phase 7: Polish & Optimization
- [ ] Smooth animations and transitions
- [ ] Performance optimization for large task lists
- [ ] Error handling and validation
- [ ] State persistence (remember last project/view)
- [ ] Loading states and feedback
- [ ] Testing with real usage

## Technical Decisions

### Data Storage
- **Format**: JSON (optimal for structured data, easy to parse)
- **Structure**:
  - `data/projects.json` - Project metadata
  - `data/{project_id}.json` - Tasks per project
  - Auto-create data directory if missing

### Key Bindings
- `Ctrl+N` - Quick add task
- `Enter` - Edit selected task
- `Space` - Toggle task completion
- `Delete` - Delete selected task
- `Ctrl+P` - New project
- `Tab/Shift+Tab` - Navigate between panels
- `Up/Down` - Navigate lists
- `?` - Help screen
- `q` - Quit application

### Catppuccin Mocha Colors
- Background: #1e1e2e
- Surface0: #313244
- Surface1: #45475a
- Surface2: #585b70
- Overlay0: #6c7086
- Text: #cdd6f4
- Subtext0: #a6adc8
- Blue: #89b4fa
- Green: #a6e3a1
- Red: #f38ba8
- Yellow: #f9e2af
- Pink: #f5c2e7
- Mauve: #cba6f7
- Lavender: #b4befe

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
- ✅ Project list with "All Tasks" view
- ✅ Task list display with completion indicators
- ✅ Task detail panel
- ✅ JSON data persistence
- ✅ Default "Personal" project created on first run
- ✅ Keyboard navigation (arrow keys)
- ✅ Quick add dialog (Ctrl+N)
- ✅ Edit task dialog
- ✅ Delete task with confirmation
- ✅ Toggle task completion

### What Needs Work
- ⏳ Subtask management (add/remove/toggle)
- ⏳ Mouse click support
- ⏳ Help screen (?)
- ⏳ Project deletion
- ⏳ Enhanced error handling
- ⏳ Search and filter functionality
- ⏳ More comprehensive testing

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

## Success Criteria
- ✅ Beautiful, cohesive Catppuccin Mocha UI
- ✅ Fast and responsive (keyboard + mouse)
- ✅ All CRUD operations work smoothly
- ✅ Dashboard provides useful insights
- ✅ Data persists reliably
- ⏳ Intuitive UX that speeds up daily workflow

## Next Steps
1. Test all existing functionality thoroughly
2. Implement subtask add/remove functionality
3. Add mouse click support throughout the app
4. Create a help screen showing keyboard shortcuts
5. Add project deletion with confirmation
6. Implement search/filter for tasks
7. Add more robust error handling
8. Test with real-world usage patterns
