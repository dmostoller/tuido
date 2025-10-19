"""Entry point for the Todo TUI application."""

from dotenv import load_dotenv

from todo_tui.app import TodoApp

# Load environment variables from .env file
load_dotenv()


def main():
    """Run the Todo TUI application."""
    app = TodoApp()
    app.run()


if __name__ == "__main__":
    main()
