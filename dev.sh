#!/bin/bash
# Development script for running the Todo TUI app in dev mode

# Load .env file if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

uv run textual run --dev todo_tui.app:TodoApp
