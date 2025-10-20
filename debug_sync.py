"""Debug script to print out what data will be synced."""

import json

from todo_tui.storage import StorageManager

# Load storage
storage = StorageManager()
settings = StorageManager.load_settings()

# Load data
projects = storage.load_projects()
tasks_by_project = {}
for project in projects:
    tasks = storage.load_tasks(project.id)
    tasks_by_project[project.id] = [t.to_dict() for t in tasks]

notes = storage.load_notes()

data = {
    "timestamp": "2025-10-20T01:30:00.000Z",
    "projects": [p.to_dict() for p in projects],
    "tasks": tasks_by_project,
    "notes": [n.to_dict() for n in notes],
}

print("=" * 80)
print("DATA STRUCTURE THAT WILL BE UPLOADED:")
print("=" * 80)
print(json.dumps(data, indent=2))
print("=" * 80)
print(f"\nAPI URL: {settings.cloud_sync_url}")
print(f"Token configured: {'Yes' if settings.cloud_sync_token else 'No'}")
print(f"Cloud sync enabled: {settings.cloud_sync_enabled}")
