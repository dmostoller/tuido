"""Entry point for the Todo TUI application."""

from todo_tui.app import TodoApp


def main():
    """Run the Todo TUI application."""
    app = TodoApp()
    app.run()


if __name__ == "__main__":
    main()
