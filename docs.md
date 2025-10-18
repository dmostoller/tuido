Tutorial¶
Welcome to the Textual Tutorial!

By the end of this page you should have a solid understanding of app development with Textual.

Quote

If you want people to build things, make it fun.

— Will McGugan (creator of Rich and Textual)

Video series¶
This tutorial has an accompanying video series which covers the same content.

Stopwatch Application¶
We're going to build a stopwatch application. This application should show a list of stopwatches with buttons to start, stop, and reset the stopwatches. We also want the user to be able to add and remove stopwatches as required.

This will be a simple yet fully featured app — you could distribute this app if you wanted to!

Here's what the finished app will look like:

stopwatch.py
⭘
StopwatchApp
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
╭─╮╭─╮   ╭─╮╭─╮   ╶╮ ╭─╴ ╭─╮╭─╮
 Stop 
│ ││ │ : │ ││ │ :  │ ├─╮ │ ││ │
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
╰─╯╰─╯   ╰─╯╰─╯   ╶┴╴╰─╯•╰─╯╰─╯
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
╭─╮╭─╮   ╭─╮╭─╮   ╶╮ ╶╮  ╭─╮╷ ╷
 Stop 
│ ││ │ : │ ││ │ :  │  │  ╰─┤╰─┤
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
╰─╯╰─╯   ╰─╯╰─╯   ╶┴╴╶┴╴•╶─╯  ╵
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
╭─╮╭─╮   ╭─╮╭─╮   ╭─╮╶─┐ ╭─╮╶─┐
 Stop 
│ ││ │ : │ ││ │ : │ │  │ ├─┤  │
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
╰─╯╰─╯   ╰─╯╰─╯   ╰─╯  ╵•╰─╯  ╵
 d 
Toggle dark mode 
 a 
Add 
 r 
Remove 
▏
^p
 palette

Info

Did you notice the ^p palette at the bottom right hand corner? This is the Command Palette. You can think of it as a dedicated command prompt for your app.

Get the code¶
If you want to try the finished Stopwatch app and follow along with the code, first make sure you have Textual installed then check out the Textual repository:


HTTPS
SSH
GitHub CLI

git clone https://github.com/Textualize/textual.git

With the repository cloned, navigate to docs/examples/tutorial and run stopwatch.py.


cd textual/docs/examples/tutorial
python stopwatch.py
Type hints (in brief)¶
Tip

Type hints are entirely optional in Textual. We've included them in the example code but it's up to you whether you add them to your own projects.

We're a big fan of Python type hints at Textualize. If you haven't encountered type hinting, it's a way to express the types of your data, parameters, and return values. Type hinting allows tools like mypy to catch bugs before your code runs.

The following function contains type hints:


def repeat(text: str, count: int) -> str:
    """Repeat a string a given number of times."""
    return text * count
Parameter types follow a colon. So text: str indicates that text requires a string and count: int means that count requires an integer.

Return types follow ->. So -> str: indicates this method returns a string.

The App class¶
The first step in building a Textual app is to import and extend the App class. Here's a basic app class we will use as a starting point for the stopwatch app.

stopwatch01.py

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header


class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    app = StopwatchApp()
    app.run()
If you run this code, you should see something like the following:

stopwatch01.py
⭘
StopwatchApp
 d 
Toggle dark mode 
▏
^p
 palette

Hit the D key to toggle between light and dark themes.

stopwatch01.py
⭘
StopwatchApp
 d 
Toggle dark mode 
▏
^p
 palette

Hit Ctrl+Q to exit the app and return to the command prompt.

A closer look at the App class¶
Let's examine stopwatch01.py in more detail.

stopwatch01.py

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header


class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    app = StopwatchApp()
    app.run()
The first line imports App class, which is the base class for all Textual apps. The second line imports two builtin widgets: Footer which shows a bar at the bottom of the screen with bound keys, and Header which shows a title at the top of the screen. Widgets are re-usable components responsible for managing a part of the screen. We will cover how to build widgets in this tutorial.

The following lines define the app itself:

stopwatch01.py

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header


class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    app = StopwatchApp()
    app.run()
The App class is where most of the logic of Textual apps is written. It is responsible for loading configuration, setting up widgets, handling keys, and more.

Here's what the above app defines:

BINDINGS is a list of tuples that maps (or binds) keys to actions in your app. The first value in the tuple is the key; the second value is the name of the action; the final value is a short description. We have a single binding which maps the D key on to the "toggle_dark" action. See key bindings in the guide for details.

compose() is where we construct a user interface with widgets. The compose() method may return a list of widgets, but it is generally easier to yield them (making this method a generator). In the example code we yield an instance of each of the widget classes we imported, i.e. Header() and Footer().

action_toggle_dark() defines an action method. Actions are methods beginning with action_ followed by the name of the action. The BINDINGS list above tells Textual to run this action when the user hits the D key. See actions in the guide for details.

stopwatch01.py

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header


class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    app = StopwatchApp()
    app.run()
The final three lines create an instance of the app and calls the run() method which puts your terminal into application mode and runs the app until you exit with Ctrl+Q. This happens within a __name__ == "__main__" block so we could run the app with python stopwatch01.py or import it as part of a larger project.

Designing a UI with widgets¶
Textual has a large number of builtin widgets. For our app we will need new widgets, which we can create by extending and combining the builtin widgets.

Before we dive into building widgets, let's first sketch a design for the app — so we know what we're aiming for.

Stop
Reset
00:00:07.21
Start
00:00:00.00
Header
Footer
Start
00:00:00.00
Stopwatch
Stopwatch
(started)
Reset
Custom widgets¶
We need a Stopwatch widget composed of the following child widgets:

A "Start" button
A "Stop" button
A "Reset" button
A time display
Let's add those to the app. Just a skeleton for now, we will add the rest of the features as we go.

stopwatch02.py

from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Button, Digits, Footer, Header


class TimeDisplay(Digits):
    """A widget to display elapsed time."""


class Stopwatch(HorizontalGroup):
    """A stopwatch widget."""

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        yield TimeDisplay("00:00:00.00")


class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield VerticalScroll(Stopwatch(), Stopwatch(), Stopwatch())

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    app = StopwatchApp()
    app.run()
We've imported two new widgets in this code: Button for the buttons and Digits for the time display. Additionally, we've imported HorizontalGroup and VerticalScroll from textual.containers (as the name of the module suggests, containers are widgets which contain other widgets). We will use these container widgets to define the general layout of our interface.

The TimeDisplay is currently very simple, all it does is extend Digits without adding any new features. We will flesh this out later.

The Stopwatch widget class extends the HorizontalGroup container class, which will arrange its children into a horizontal row. The Stopwatch's compose() adds those children, which correspond to the components from the sketch above.

Coordinating widgets

If you are building custom widgets of your own, be sure to see guide on coordinating widgets.

The buttons¶
The Button constructor takes a label to be displayed in the button ("Start", "Stop", or "Reset"). Additionally, some of the buttons set the following parameters:

id is an identifier we can use to tell the buttons apart in code and apply styles. More on that later.
variant is a string which selects a default style. The "success" variant makes the button green, and the "error" variant makes it red.
Composing the widgets¶
The new line in StopwatchApp.compose() yields a single VerticalScroll which will scroll if the contents don't quite fit. This widget also takes care of key bindings required for scrolling, like Up, Down, Page Down, Page Up, Home, End, etc.

When widgets contain other widgets (like VerticalScroll) they will typically accept their child widgets as positional arguments. So the line yield VerticalScroll(Stopwatch(), Stopwatch(), Stopwatch()) creates a VerticalScroll containing three Stopwatch widgets.

The unstyled app¶
Let's see what happens when we run stopwatch02.py.

stopwatch02.py
⭘
StopwatchApp
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
╭─╮╭─╮   ╭─╮╭─╮   ╭─╮╭─╮ ╭─╮╭─╮
 Start 
 Stop 
 Reset 
│ ││ │ : │ ││ │ : │ ││ │ │ ││ │
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
╰─╯╰─╯   ╰─╯╰─╯   ╰─╯╰─╯•╰─╯╰─╯
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
╭─╮╭─╮   ╭─╮╭─╮   ╭─╮╭─╮ ╭─╮╭─╮
 Start 
 Stop 
 Reset 
│ ││ │ : │ ││ │ : │ ││ │ │ ││ │
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
╰─╯╰─╯   ╰─╯╰─╯   ╰─╯╰─╯•╰─╯╰─╯
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
╭─╮╭─╮   ╭─╮╭─╮   ╭─╮╭─╮ ╭─╮╭─╮
 Start 
 Stop 
 Reset 
│ ││ │ : │ ││ │ : │ ││ │ │ ││ │
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
╰─╯╰─╯   ╰─╯╰─╯   ╰─╯╰─╯•╰─╯╰─╯
 d 
Toggle dark mode 
▏
^p
 palette

The elements of the stopwatch application are there, but it doesn't look much like the sketch. This is because we have yet to apply any styles to our new widgets.

Writing Textual CSS¶
Every widget has a styles object with a number of attributes that impact how the widget will appear. Here's how you might set white text and a blue background for a widget:


self.styles.background = "blue"
self.styles.color = "white"
While it's possible to set all styles for an app this way, it is rarely necessary. Textual has support for CSS (Cascading Style Sheets), a technology used by web browsers. CSS files are data files loaded by your app which contain information about styles to apply to your widgets.

Info

The dialect of CSS used in Textual is greatly simplified over web based CSS and easier to learn.

CSS makes it easy to iterate on the design of your app and enables live-editing — you can edit CSS and see the changes without restarting the app!

Let's add a CSS file to our application.

stopwatch03.py

from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Button, Digits, Footer, Header


class TimeDisplay(Digits):
    """A widget to display elapsed time."""


class Stopwatch(HorizontalGroup):
    """A stopwatch widget."""

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        yield TimeDisplay("00:00:00.00")


class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "stopwatch03.tcss"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield VerticalScroll(Stopwatch(), Stopwatch(), Stopwatch())

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    app = StopwatchApp()
    app.run()
Adding the CSS_PATH class variable tells Textual to load the following file when the app starts:

stopwatch03.tcss

Stopwatch {   
    background: $boost;
    height: 5;
    margin: 1;
    min-width: 50;
    padding: 1;
}

TimeDisplay {   
    text-align: center;
    color: $foreground-muted;
    height: 3;
}

Button {
    width: 16;
}

#start {
    dock: left;
}

#stop {
    dock: left;
    display: none;
}

#reset {
    dock: right;
}
If we run the app now, it will look very different.

stopwatch03.py
⭘
StopwatchApp
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
╭─╮╭─╮   ╭─╮╭─╮   ╭─╮╭─╮ ╭─╮╭─╮
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
 Start 
│ ││ │ : │ ││ │ : │ ││ │ │ ││ │
 Reset 
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
╰─╯╰─╯   ╰─╯╰─╯   ╰─╯╰─╯•╰─╯╰─╯
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
╭─╮╭─╮   ╭─╮╭─╮   ╭─╮╭─╮ ╭─╮╭─╮
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
 Start 
│ ││ │ : │ ││ │ : │ ││ │ │ ││ │
 Reset 
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
╰─╯╰─╯   ╰─╯╰─╯   ╰─╯╰─╯•╰─╯╰─╯
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
╭─╮╭─╮   ╭─╮╭─╮   ╭─╮╭─╮ ╭─╮╭─╮
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
 Start 
│ ││ │ : │ ││ │ : │ ││ │ │ ││ │
 Reset 
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
╰─╯╰─╯   ╰─╯╰─╯   ╰─╯╰─╯•╰─╯╰─╯
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
 d 
Toggle dark mode 
▏
^p
 palette

This app looks much more like our sketch. Let's look at how Textual uses stopwatch03.tcss to apply styles.

CSS basics¶
CSS files contain a number of declaration blocks. Here's the first such block from stopwatch03.tcss again:


Stopwatch {
    background: $boost;
    height: 5;
    margin: 1;
    min-width: 50;
    padding: 1;
}
The first line tells Textual that the styles should apply to the Stopwatch widget. The lines between the curly brackets contain the styles themselves.

Here's how this CSS code changes how the Stopwatch widget is displayed.

Start
00:00:00.00
Reset
5 lines
horizontal layout
1 cell margin
1 cell padding
around buttons
background color
is $boost
background: $boost sets the background color to $boost. The $ prefix picks a pre-defined color from the builtin theme. There are other ways to specify colors such as "blue" or rgb(20,46,210).
height: 5 sets the height of our widget to 5 lines of text.
margin: 1 sets a margin of 1 cell around the Stopwatch widget to create a little space between widgets in the list.
min-width: 50 sets the minimum width of our widget to 50 cells.
padding: 1 sets a padding of 1 cell around the child widgets.
Here's the rest of stopwatch03.tcss which contains further declaration blocks:


TimeDisplay {   
    text-align: center;
    color: $foreground-muted;
    height: 3;
}

Button {
    width: 16;
}

#start {
    dock: left;
}

#stop {
    dock: left;
    display: none;
}

#reset {
    dock: right;
}
The TimeDisplay block aligns text to the center (text-align:), sets its color (color:), and sets its height (height:) to 3 lines.

The Button block sets the width (width:) of buttons to 16 cells (character widths).

The last 3 blocks have a slightly different format. When the declaration begins with a # then the styles will be applied to widgets with a matching "id" attribute. We've set an ID on the Button widgets we yielded in compose. For instance the first button has id="start" which matches #start in the CSS.

The buttons have a dock style which aligns the widget to a given edge. The start and stop buttons are docked to the left edge, while the reset button is docked to the right edge.

You may have noticed that the stop button (#stop in the CSS) has display: none;. This tells Textual to not show the button. We do this because we don't want to display the stop button when the timer is not running. Similarly, we don't want to show the start button when the timer is running. We will cover how to manage such dynamic user interfaces in the next section.

Dynamic CSS¶
We want our Stopwatch widget to have two states: a default state with a Start and Reset button; and a started state with a Stop button. When a stopwatch is started it should also have a green background to indicate it is currently active.

Stop
00:00:00.00
Reset
Start
00:00:00.00
Stopwatch
Started Stopwatch
We can accomplish this with a CSS class. Not to be confused with a Python class, a CSS class is like a tag you can add to a widget to modify its styles. A widget may have any number of CSS classes, which may be added and removed to change its appearance.

Here's the new CSS:

stopwatch04.tcss

Stopwatch {
    background: $boost;
    height: 5;
    margin: 1;
    min-width: 50;
    padding: 1;
}

TimeDisplay {   
    text-align: center;
    color: $foreground-muted;
    height: 3;
}

Button {
    width: 16;
}

#start {
    dock: left;
}

#stop {
    dock: left;
    display: none;
}

#reset {
    dock: right;
}

.started {
    background: $success-muted;
    color: $text;
}

.started TimeDisplay {
    color: $foreground;
}

.started #start {
    display: none
}

.started #stop {
    display: block
}

.started #reset {
    visibility: hidden
}
These new rules are prefixed with .started. The . indicates that .started refers to a CSS class called "started". The new styles will be applied only to widgets that have this CSS class.

Some of the new styles have more than one selector separated by a space. The space indicates that the rule should match the second selector if it is a child of the first. Let's look at one of these styles:


.started #start {
    display: none
}
The .started selector matches any widget with a "started" CSS class. While #start matches a widget with an ID of "start". Combining the two selectors with a space (.started #start) creates a new selector that will match the start button only if it is also inside a container with a CSS class of "started".

As before, the display: none rule will cause any matching widgets to be hidden from view.

If we were to write this in English, it would be something like: "Hide the start button if the widget is already started".

Manipulating classes¶
Modifying a widget's CSS classes is a convenient way to update visuals without introducing a lot of messy display related code.

You can add and remove CSS classes with the add_class() and remove_class() methods. We will use these methods to connect the started state to the Start / Stop buttons.

The following code will start or stop the stopwatches in response to clicking a button:

stopwatch04.py

from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Button, Digits, Footer, Header


class TimeDisplay(Digits):
    """A widget to display elapsed time."""


class Stopwatch(HorizontalGroup):
    """A stopwatch widget."""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "start":
            self.add_class("started")
        elif event.button.id == "stop":
            self.remove_class("started")

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        yield TimeDisplay("00:00:00.00")


class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "stopwatch04.tcss"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield VerticalScroll(Stopwatch(), Stopwatch(), Stopwatch())

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    app = StopwatchApp()
    app.run()
The on_button_pressed method is an event handler. Event handlers are methods called by Textual in response to an event such as a key press, mouse click, etc. Event handlers begin with on_ followed by the name of the event they will handle. Hence on_button_pressed will handle the button pressed event.

See the guide on message handlers for the details on how to write event handlers.

If you run stopwatch04.py now you will be able to toggle between the two states by clicking the first button:

stopwatch04.py
⭘
StopwatchApp
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
╭─╮╭─╮   ╭─╮╭─╮   ╭─╮╭─╮ ╭─╮╭─╮
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
 Start 
│ ││ │ : │ ││ │ : │ ││ │ │ ││ │
 Reset 
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
╰─╯╰─╯   ╰─╯╰─╯   ╰─╯╰─╯•╰─╯╰─╯
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
╭─╮╭─╮   ╭─╮╭─╮   ╭─╮╭─╮ ╭─╮╭─╮
 Stop 
│ ││ │ : │ ││ │ : │ ││ │ │ ││ │
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
╰─╯╰─╯   ╰─╯╰─╯   ╰─╯╰─╯•╰─╯╰─╯
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
╭─╮╭─╮   ╭─╮╭─╮   ╭─╮╭─╮ ╭─╮╭─╮
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
 Start 
│ ││ │ : │ ││ │ : │ ││ │ │ ││ │
 Reset 
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
╰─╯╰─╯   ╰─╯╰─╯   ╰─╯╰─╯•╰─╯╰─╯
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
 d 
Toggle dark mode 
▏
^p
 palette

When the button event handler adds or removes the "started" CSS class, Textual re-applies the CSS and updates the visuals.

Reactive attributes¶
A recurring theme in Textual is that you rarely need to explicitly update a widget's visuals. It is possible: you can call refresh() to display new data. However, Textual prefers to do this automatically via reactive attributes.

Reactive attributes work like any other attribute, such as those you might set in an __init__ method, but allow Textual to detect when you assign to them, in addition to some other superpowers.

To add a reactive attribute, import reactive and create an instance in your class scope.

Let's add reactives to our stopwatch to calculate and display the elapsed time.

stopwatch05.py

from time import monotonic

from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Button, Digits, Footer, Header


class TimeDisplay(Digits):
    """A widget to display elapsed time."""

    start_time = reactive(monotonic)
    time = reactive(0.0)

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.set_interval(1 / 60, self.update_time)

    def update_time(self) -> None:
        """Method to update the time to the current time."""
        self.time = monotonic() - self.start_time

    def watch_time(self, time: float) -> None:
        """Called when the time attribute changes."""
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")


class Stopwatch(HorizontalGroup):
    """A stopwatch widget."""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "start":
            self.add_class("started")
        elif event.button.id == "stop":
            self.remove_class("started")

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        yield TimeDisplay()


class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "stopwatch04.tcss"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield VerticalScroll(Stopwatch(), Stopwatch(), Stopwatch())

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    app = StopwatchApp()
    app.run()
We have added two reactive attributes to the TimeDisplay widget: start_time will contain the time the stopwatch was started (in seconds), and time will contain the time to be displayed in the Stopwatch widget.

Both attributes will be available on self as if you had assigned them in __init__. If you write to either of these attributes the widget will update automatically.

Info

The monotonic function in this example is imported from the standard library time module. It is similar to time.time but won't go backwards if the system clock is changed.

The first argument to reactive may be a default value for the attribute or a callable that returns a default value. We set the default for start_time to the monotonic function which will be called to initialize the attribute with the current time when the TimeDisplay is added to the app. The time attribute has a simple float as the default, so self.time will be initialized to 0.

The on_mount method is an event handler called when the widget is first added to the application (or mounted in Textual terminology). In this method we call set_interval() to create a timer which calls self.update_time sixty times a second. This update_time method calculates the time elapsed since the widget started and assigns it to self.time — which brings us to one of Reactive's super-powers.

If you implement a method that begins with watch_ followed by the name of a reactive attribute, then the method will be called when the attribute is modified. Such methods are known as watch methods.

Because watch_time watches the time attribute, when we update self.time 60 times a second we also implicitly call watch_time which converts the elapsed time to a string and updates the widget with a call to self.update. Because this happens automatically, we don't need to pass in an initial argument to TimeDisplay.

The end result is that the Stopwatch widgets show the time elapsed since the widget was created:

stopwatch05.py
⭘
StopwatchApp
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
╭─╮╭─╮   ╭─╮╭─╮   ╭─╮╶─╮ ╭─╮╶─┐
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
 Start 
│ ││ │ : │ ││ │ : │ │ ─┤ │ │  │
 Reset 
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
╰─╯╰─╯   ╰─╯╰─╯   ╰─╯╶─╯•╰─╯  ╵
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
╭─╮╭─╮   ╭─╮╭─╮   ╭─╮╶─╮ ╭─╮╶─┐
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
 Start 
│ ││ │ : │ ││ │ : │ │ ─┤ │ │  │
 Reset 
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
╰─╯╰─╯   ╰─╯╰─╯   ╰─╯╶─╯•╰─╯  ╵
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
╭─╮╭─╮   ╭─╮╭─╮   ╭─╮╶─╮ ╭─╮╶─┐
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
 Start 
│ ││ │ : │ ││ │ : │ │ ─┤ │ │  │
 Reset 
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
╰─╯╰─╯   ╰─╯╰─╯   ╰─╯╶─╯•╰─╯  ╵
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
 d 
Toggle dark mode 
▏
^p
 palette

We've seen how we can update widgets with a timer, but we still need to wire up the buttons so we can operate stopwatches independently.

Wiring buttons¶
We need to be able to start, stop, and reset each stopwatch independently. We can do this by adding a few more methods to the TimeDisplay class.

stopwatch06.py

from time import monotonic

from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Button, Digits, Footer, Header


class TimeDisplay(Digits):
    """A widget to display elapsed time."""

    start_time = reactive(monotonic)
    time = reactive(0.0)
    total = reactive(0.0)

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.update_timer = self.set_interval(1 / 60, self.update_time, pause=True)

    def update_time(self) -> None:
        """Method to update time to current."""
        self.time = self.total + (monotonic() - self.start_time)

    def watch_time(self, time: float) -> None:
        """Called when the time attribute changes."""
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")

    def start(self) -> None:
        """Method to start (or resume) time updating."""
        self.start_time = monotonic()
        self.update_timer.resume()

    def stop(self) -> None:
        """Method to stop the time display updating."""
        self.update_timer.pause()
        self.total += monotonic() - self.start_time
        self.time = self.total

    def reset(self) -> None:
        """Method to reset the time display to zero."""
        self.total = 0
        self.time = 0


class Stopwatch(HorizontalGroup):
    """A stopwatch widget."""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        time_display = self.query_one(TimeDisplay)
        if button_id == "start":
            time_display.start()
            self.add_class("started")
        elif button_id == "stop":
            time_display.stop()
            self.remove_class("started")
        elif button_id == "reset":
            time_display.reset()

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        yield TimeDisplay()


class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "stopwatch04.tcss"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header()
        yield Footer()
        yield VerticalScroll(Stopwatch(), Stopwatch(), Stopwatch())

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    app = StopwatchApp()
    app.run()
Here's a summary of the changes made to TimeDisplay.

We've added a total reactive attribute to store the total time elapsed between clicking the start and stop buttons.
The call to set_interval has grown a pause=True argument which starts the timer in pause mode (when a timer is paused it won't run until resume() is called). This is because we don't want the time to update until the user hits the start button.
The update_time method now adds total to the current time to account for the time between any previous clicks of the start and stop buttons.
We've stored the result of set_interval which returns a Timer object. We will use this to resume the timer when we start the Stopwatch.
We've added start(), stop(), and reset() methods.
In addition, the on_button_pressed method on Stopwatch has grown some code to manage the time display when the user clicks a button. Let's look at that in detail:


    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        time_display = self.query_one(TimeDisplay)
        if button_id == "start":
            time_display.start()
            self.add_class("started")
        elif button_id == "stop":
            time_display.stop()
            self.remove_class("started")
        elif button_id == "reset":
            time_display.reset()
This code supplies missing features and makes our app useful. We've made the following changes.

The first line retrieves id attribute of the button that was pressed. We can use this to decide what to do in response.
The second line calls query_one to get a reference to the TimeDisplay widget.
We call the method on TimeDisplay that matches the pressed button.
We add the "started" class when the Stopwatch is started (self.add_class("started")), and remove it (self.remove_class("started")) when it is stopped. This will update the Stopwatch visuals via CSS.
If you run stopwatch06.py you will be able to use the stopwatches independently.

stopwatch06.py
⭘
StopwatchApp
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
╭─╮╭─╮   ╭─╮╭─╮   ╶╮ ╭─╮ ╶╮ ╷ ╷
 Stop 
│ ││ │ : │ ││ │ :  │ │ │  │ ╰─┤
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
╰─╯╰─╯   ╰─╯╰─╯   ╶┴╴╰─╯•╶┴╴  ╵
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
╭─╮╭─╮   ╭─╮╭─╮   ╭─╮╭─╴ ╭─╮╭─╮
 Stop 
│ ││ │ : │ ││ │ : │ │├─╮ │ │├─┤
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
╰─╯╰─╯   ╰─╯╰─╯   ╰─╯╰─╯•╰─╯╰─╯
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
╭─╮╭─╮   ╭─╮╭─╮   ╭─╮╭─╮ ╭─╮╭─╮
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
 Start 
│ ││ │ : │ ││ │ : │ ││ │ │ ││ │
 Reset 
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
╰─╯╰─╯   ╰─╯╰─╯   ╰─╯╰─╯•╰─╯╰─╯
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
 d 
Toggle dark mode 
▏
^p
 palette

The only remaining feature of the Stopwatch app left to implement is the ability to add and remove stopwatches.

Dynamic widgets¶
The Stopwatch app creates widgets when it starts via the compose method. We will also need to create new widgets while the app is running, and remove widgets we no longer need. We can do this by calling mount() to add a widget, and remove() to remove a widget.

Let's use these methods to implement adding and removing stopwatches to our app.

stopwatch.py

from time import monotonic

from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Button, Digits, Footer, Header


class TimeDisplay(Digits):
    """A widget to display elapsed time."""

    start_time = reactive(monotonic)
    time = reactive(0.0)
    total = reactive(0.0)

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.update_timer = self.set_interval(1 / 60, self.update_time, pause=True)

    def update_time(self) -> None:
        """Method to update time to current."""
        self.time = self.total + (monotonic() - self.start_time)

    def watch_time(self, time: float) -> None:
        """Called when the time attribute changes."""
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")

    def start(self) -> None:
        """Method to start (or resume) time updating."""
        self.start_time = monotonic()
        self.update_timer.resume()

    def stop(self):
        """Method to stop the time display updating."""
        self.update_timer.pause()
        self.total += monotonic() - self.start_time
        self.time = self.total

    def reset(self):
        """Method to reset the time display to zero."""
        self.total = 0
        self.time = 0


class Stopwatch(HorizontalGroup):
    """A stopwatch widget."""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        time_display = self.query_one(TimeDisplay)
        if button_id == "start":
            time_display.start()
            self.add_class("started")
        elif button_id == "stop":
            time_display.stop()
            self.remove_class("started")
        elif button_id == "reset":
            time_display.reset()

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        yield TimeDisplay()


class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "stopwatch.tcss"

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("a", "add_stopwatch", "Add"),
        ("r", "remove_stopwatch", "Remove"),
    ]

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header()
        yield Footer()
        yield VerticalScroll(Stopwatch(), Stopwatch(), Stopwatch(), id="timers")

    def action_add_stopwatch(self) -> None:
        """An action to add a timer."""
        new_stopwatch = Stopwatch()
        self.query_one("#timers").mount(new_stopwatch)
        new_stopwatch.scroll_visible()

    def action_remove_stopwatch(self) -> None:
        """Called to remove a timer."""
        timers = self.query("Stopwatch")
        if timers:
            timers.last().remove()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    app = StopwatchApp()
    app.run()
Here's a summary of the changes:

The VerticalScroll object in StopWatchApp grew a "timers" ID.
Added action_add_stopwatch to add a new stopwatch.
Added action_remove_stopwatch to remove a stopwatch.
Added keybindings for the actions.
The action_add_stopwatch method creates and mounts a new stopwatch. Note the call to query_one() with a CSS selector of "#timers" which gets the timer's container via its ID. Once mounted, the new Stopwatch will appear in the terminal. That last line in action_add_stopwatch calls scroll_visible() which will scroll the container to make the new Stopwatch visible (if required).

The action_remove_stopwatch function calls query() with a CSS selector of "Stopwatch" which gets all the Stopwatch widgets. If there are stopwatches then the action calls last() to get the last stopwatch, and remove() to remove it.

If you run stopwatch.py now you can add a new stopwatch with the A key and remove a stopwatch with R.

stopwatch.py
⭘
StopwatchApp
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
╭─╮╭─╮   ╭─╮╭─╮   ╭─╮╭─╴ ╭─╮╭─╮
 Stop 
│ ││ │ : │ ││ │ : │ │╰─╮ │ │╰─┤
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
╰─╯╰─╯   ╰─╯╰─╯   ╰─╯╶─╯•╰─╯╶─╯
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
╭─╮╭─╮   ╭─╮╭─╮   ╭─╮╭─╮ ╭─╮╭─╮
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
 Start 
│ ││ │ : │ ││ │ : │ ││ │ │ ││ │
 Reset 
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
╰─╯╰─╯   ╰─╯╰─╯   ╰─╯╰─╯•╰─╯╰─╯
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
╭─╮╭─╮   ╭─╮╭─╮   ╭─╮╭─╮ ╭─╮╭─╮
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
 Start 
│ ││ │ : │ ││ │ : │ ││ │ │ ││ │
 Reset 
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
╰─╯╰─╯   ╰─╯╰─╯   ╰─╯╰─╯•╰─╯╰─╯
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
╭─╮╭─╮   ╭─╮╭─╮   ╭─╮╭─╮ ╭─╮╭─╮
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
 Start 
│ ││ │ : │ ││ │ : │ ││ │ │ ││ │
 Reset 
 d 
Toggle dark mode 
 a 
Add 
 r 
Remove 
▏
^p
 palette

What next?¶
