"""Entry point for the Todo TUI application."""

import argparse
from pathlib import Path

from dotenv import load_dotenv

from todo_tui.app import TodoApp

# Load environment variables from .env file
load_dotenv()


def main():
    """Run the Todo TUI application."""
    parser = argparse.ArgumentParser(
        description="Tuido - A beautiful TUI todo application"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode with sample data (for screenshots/testing)",
    )
    args = parser.parse_args()

    demo_data_dir = None
    if args.demo:
        # Look for demo_data inside the todo_tui package
        demo_data_dir = Path(__file__).parent / "todo_tui" / "demo_data"
        if not demo_data_dir.exists():
            print(f"Error: Demo data directory not found at {demo_data_dir}")
            return

    app = TodoApp(demo_data_dir=demo_data_dir)
    app.run()


if __name__ == "__main__":
    main()
