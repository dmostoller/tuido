"""Compact card widget with rotating programmer wisdom quotes."""

from __future__ import annotations

import random

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static

from ..icons import Icons

PROGRAMMER_QUOTES = [
    ("Premature optimization is the root of all evil.", "Donald Knuth"),
    ("The best way to predict the future is to invent it.", "Alan Kay"),
    (
        "Programs must be written for people to read, and only incidentally for machines to execute.",
        "Abelson & Sussman",
    ),
    ("First, solve the problem. Then, write the code.", "John Johnson"),
    ("Simplicity is prerequisite for reliability.", "Edsger Dijkstra"),
    ("Make it work, make it right, make it fast.", "Kent Beck"),
    (
        "Any fool can write code that a computer can understand. Good programmers write code that humans can understand.",
        "Martin Fowler",
    ),
    (
        "The most effective debugging tool is still careful thought, coupled with judiciously placed print statements.",
        "Brian Kernighan",
    ),
    ("Code never lies, comments sometimes do.", "Ron Jeffries"),
    ("Talk is cheap. Show me the code.", "Linus Torvalds"),
    (
        "The function of good software is to make the complex appear to be simple.",
        "Grady Booch",
    ),
    (
        "You can't have great software without a great team, and most software teams behave like dysfunctional families.",
        "Jim McCarthy",
    ),
    (
        "One of my most productive days was throwing away 1000 lines of code.",
        "Ken Thompson",
    ),
    (
        "When to use iterative development? You should use iterative development only on projects that you want to succeed.",
        "Martin Fowler",
    ),
    (
        "The cheapest, fastest, and most reliable components are those that aren't there.",
        "Gordon Bell",
    ),
    ("Deleted code is debugged code.", "Jeff Sickel"),
    (
        "If debugging is the process of removing bugs, then programming must be the process of putting them in.",
        "Edsger Dijkstra",
    ),
    ("Before software can be reusable it first has to be usable.", "Ralph Johnson"),
    (
        "Walking on water and developing software from a specification are easy if both are frozen.",
        "Edward Berard",
    ),
    (
        "The purpose of software engineering is to control complexity, not to create it.",
        "Pamela Zave",
    ),
    (
        "A language that doesn't affect the way you think about programming is not worth knowing.",
        "Alan Perlis",
    ),
    ("Don't comment bad code—rewrite it.", "Brian Kernighan"),
    (
        "Measuring programming progress by lines of code is like measuring aircraft building progress by weight.",
        "Bill Gates",
    ),
    (
        "Controlling complexity is the essence of computer programming.",
        "Brian Kernighan",
    ),
    (
        "The best performance improvement is the transition from the nonworking state to the working state.",
        "John Ousterhout",
    ),
    (
        "Sometimes it pays to stay in bed on Monday, rather than spending the rest of the week debugging Monday's code.",
        "Dan Salomon",
    ),
    (
        "Inside every large program is a small program struggling to get out.",
        "Tony Hoare",
    ),
    (
        "A good programmer is someone who always looks both ways before crossing a one-way street.",
        "Doug Linder",
    ),
    (
        "There are only two hard things in Computer Science: cache invalidation and naming things.",
        "Phil Karlton",
    ),
    (
        "Debugging is twice as hard as writing the code in the first place. Therefore, if you write the code as cleverly as possible, you are, by definition, not smart enough to debug it.",
        "Brian Kernighan",
    ),
    (
        "Curse of the self-taught: fear that you know only points here and there, islands of knowledge, and between them are chasms into which you will fall in humiliating failure, a fear that followed me from the first time I learned how to code.",
        "Ellen Ullman",
    ),
    (
        "The most dangerous phrase in the language is, 'We've always done it this way.'",
        "Grace Hopper",
    ),
    (
        "Programming isn't about what you know; it's about what you can figure out.",
        "Chris Pine",
    ),
    (
        "Code is read much more often than it is written.",
        "Guido Van Rossum",
    ),
    (
        "You might not think that programmers are artists, but programming is an extremely creative profession. It's logic-based creativity.",
        "John Romero",
    ),
    (
        "This was one of the best parts of being a coder, and an artist: the thrill of being in the middle of creating something delightful. It's like the anticipation of eating freshly baked bread after its aroma fills the room.",
        "Dr. Joy Buolamwini",
    ),
    (
        "Every great developer you know got there by solving problems they were unqualified to solve until they actually did it.",
        "Patrick McKenzie",
    ),
    (
        "The code you write makes you a programmer. The code you delete makes you a good one. The code you don't have to write makes you a great one.",
        "Mario Fusco",
    ),
    (
        "Code is like humor. When you have to explain it, it's bad.",
        "Cory House",
    ),
    (
        "The more I study, the more insatiable do I feel my genius for it to be.",
        "Ada Lovelace",
    ),
    (
        "Learning to write programs stretches your mind, and helps you think better, creates a way of thinking about things that I think is helpful in all domains.",
        "Bill Gates",
    ),
    (
        "In the beginner's mind, there are many possibilities; in the expert's mind, there are few.",
        "Shunryu Suzuki",
    ),
    (
        "People think that computer science is the art of geniuses but the actual reality is the opposite, just many people doing things that build on each other, like a wall of mini stones.",
        "Donald Knuth",
    ),
    (
        "First learn computer science and all the theory. Next develop a programming style. Then forget all that and just hack.",
        "George Carrette",
    ),
    (
        "To iterate is human, to recurse divine.",
        "L. Peter Deutsch",
    ),
    (
        "On two occasions I have been asked [by members of Parliament]: 'Pray, Mr. Babbage, if you put into the machine wrong figures, will the right answers come out?' I am not able rightly to apprehend the kind of confusion of ideas that could provoke such a question.",
        "Charles Babbage",
    ),
    (
        "Most good programmers do programming not because they expect to get paid or get adulation by the public, but because it is fun to program.",
        "Linus Torvalds",
    ),
    (
        "There are two ways of constructing a software design. One way is to make it so simple that there are obviously no deficiencies. And the other way is to make it so complicated that there are no obvious deficiencies.",
        "C.A.R. Hoare",
    ),
]


class QuotesCard(Container):
    """A compact card displaying  rotating programmer wisdom."""

    DEFAULT_CSS = """
    QuotesCard {
        height: 100%;
        width: 100%;
        border: round $accent;
        background: $surface;
        padding: 1 2;
        layout: vertical;
        content-align: center middle;
        min-width: 30;
        min-height: 10;
    }

    QuotesCard Vertical {
        height: 100%;
        width: 100%;
        content-align: center middle;
    }

    QuotesCard .stats-line {
        color: $foreground;
        text-align: center;
        padding: 0 0 0 0;
        height: auto;
    }

    QuotesCard .stat-divider {
        color: $primary-darken-2;
        height: 1;
        padding: 0;
        margin: 0;
    }

    QuotesCard .quote-container {
        height: 1fr;
        width: 100%;
        padding: 1 1 0 1;
        layout: vertical;
        content-align: center middle;
    }

    QuotesCard .quote-text {
        color: $text-muted;
        text-style: italic;
        text-align: center;
        width: 100%;
    }

    QuotesCard .quote-author {
        color: $primary-darken-1;
        text-align: center;
        padding: 1 0 0 0;
        width: 100%;
    }
    """

    def __init__(self, id: str = None):
        super().__init__(id=id)
        self.total_tasks = 0
        self.completion_rate = 0
        self.today_count = 0
        self.current_quote_index = 0

    def compose(self) -> ComposeResult:
        """Compose the stats card with compact stats and quote."""
        with Vertical():
            yield Static("", id="stats-line", classes="stats-line")
            # yield Static("─" * 50, classes="stat-divider")
            with Vertical(classes="quote-container"):
                yield Static("", id="quote-text", classes="quote-text")
                yield Static("", id="quote-author", classes="quote-author")

    def on_mount(self) -> None:
        """Initialize the widget after mounting."""
        self._update_display()
        self._rotate_quote()
        # Rotate quote every 60 seconds
        self.set_interval(60.0, self._rotate_quote)

    def update_stats(self, total: int, rate: int, today: int) -> None:
        """Update the statistics display."""
        self.total_tasks = total
        self.completion_rate = rate
        self.today_count = today

        # Only update the display if we're mounted
        if self.is_mounted:
            self._update_display()

    def _update_display(self) -> None:
        """Update the visual display with current stats."""
        # Primary theme color (Catppuccin Mocha blue)
        primary_color = "#89b4fa"

        # Build compact single-line stats
        stats_text = (
            f"{Icons.LIST} [bold {primary_color}]{self.total_tasks}[/] [dim]Total[/]  "
            f"[dim]|[/]  "
            f"{Icons.CALENDAR} [bold {primary_color}]{self.today_count}[/] [dim]Today[/]"
        )

        self.query_one("#stats-line", Static).update(stats_text)

    def _rotate_quote(self) -> None:
        """Rotate to a new random quote."""
        # Pick a random quote
        quote_text, quote_author = random.choice(PROGRAMMER_QUOTES)

        # Update the display
        self.query_one("#quote-text", Static).update(f'"{quote_text}"')
        self.query_one("#quote-author", Static).update(f"— {quote_author}")
