"""A terminal UI for browsing the periodic table of the elements."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical, VerticalScroll
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Footer, Header, Input, Sparkline, Static

from periodic_table_tui.data import CATEGORY_COLORS, ELEMENTS, Element

GRID_COLUMNS = 18
GRID_ROWS = 10

ROOM_TEMPERATURE_LABEL = "at room temp"

# A handful of Textual's built-in themes, cycled one at a time with "t".
# The full set (light and dark) is also reachable via the command palette
# (ctrl+p -> "Change theme").
THEME_CYCLE = [
    "textual-dark",
    "nord",
    "gruvbox",
    "dracula",
    "tokyo-night",
    "catppuccin-mocha",
    "textual-light",
    "solarized-light",
]

_ELEMENTS_BY_POS: dict[tuple[int, int], Element] = {(e.period, e.group): e for e in ELEMENTS}
_GRID_DIRECTIONS: dict[str, tuple[int, int]] = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}
_ELEMENTS_BY_PERIOD: dict[int, list[Element]] = {}
for _element in ELEMENTS:
    _ELEMENTS_BY_PERIOD.setdefault(_element.period, []).append(_element)
for _period_elements in _ELEMENTS_BY_PERIOD.values():
    _period_elements.sort(key=lambda e: e.group)


def _category_class(category: str) -> str:
    return "cat-" + category.replace(" ", "-")


def _format_optional(value: float | None, unit: str = "", precision: int = 2) -> str:
    if value is None:
        return "unknown"
    return f"{value:.{precision}f}{unit}"


class ElementTile(Static, can_focus=True):
    """A single clickable/focusable cell representing one element."""

    class Selected(Message):
        def __init__(self, element: Element) -> None:
            self.element = element
            super().__init__()

    def __init__(self, element: Element) -> None:
        text = f"{element.number}\n[b]{element.symbol}[/b]\n{element.mass:.1f}"
        super().__init__(text, classes=f"tile {_category_class(element.category)}")
        self.element = element

    def on_click(self) -> None:
        self.post_message(self.Selected(self.element))
        self.focus()

    def on_focus(self) -> None:
        self.post_message(self.Selected(self.element))

    def matches(self, query: str) -> bool:
        if not query:
            return True
        query = query.strip().lower()
        return (
            query in self.element.name.lower()
            or query in self.element.symbol.lower()
            or query == str(self.element.number)
        )


class Blank(Static):
    """An empty, non-interactive spacer cell used to preserve grid alignment."""


class ElementGrid(ScrollableContainer):
    """Scrollable wrapper around the tile grid.

    ScrollableContainer's default up/down/left/right bindings scroll the
    viewport; that shadows arrow-key tile navigation for any focused tile
    inside it, since the container is closer in the DOM than the App. These
    overrides redirect arrow keys to the App's tile-navigation action instead
    (mouse-wheel/scrollbar scrolling is unaffected).
    """

    BINDINGS = [
        Binding("up", "app.move_focus('up')", "Navigate", show=False),
        Binding("down", "app.move_focus('down')", "Navigate", show=False),
        Binding("left", "app.move_focus('left')", "Navigate", show=False),
        Binding("right", "app.move_focus('right')", "Navigate", show=False),
    ]


class Legend(Static):
    """Static color-key for element categories."""

    def compose(self) -> ComposeResult:
        yield Static("Categories", classes="legend-title")
        for category in CATEGORY_COLORS:
            yield Static(f" {category} ", classes=f"legend-item {_category_class(category)}")


class DetailPanel(Vertical):
    """Shows information about the currently selected element, plus a trend chart."""

    element: reactive[Element | None] = reactive(None)

    def compose(self) -> ComposeResult:
        yield Static(id="detail-text")
        yield Static(id="detail-trend-label")
        yield Sparkline([], id="detail-trend")

    def watch_element(self, element: Element | None) -> None:
        text = self.query_one("#detail-text", Static)
        trend_label = self.query_one("#detail-trend-label", Static)
        sparkline = self.query_one(Sparkline)

        if element is None:
            text.update("[dim]Select an element to see details.[/dim]")
            trend_label.update("")
            sparkline.data = []
            return

        melting = _format_optional(element.melting_point, " K")
        boiling = _format_optional(element.boiling_point, " K")
        density = _format_optional(element.density, " g/cm³", precision=4)
        electronegativity = _format_optional(element.electronegativity, precision=2)
        atomic_radius = _format_optional(element.atomic_radius, " pm", precision=0)
        oxidation_states = element.oxidation_states or "unknown"

        text.update(
            f"[b]{element.name}[/b] ({element.symbol})\n\n"
            f"Atomic number: {element.number}\n"
            f"Atomic mass:   {element.mass}\n"
            f"Category:      {element.category}\n"
            f"Phase {ROOM_TEMPERATURE_LABEL}: {element.phase}\n\n"
            f"Melting point: {melting}\n"
            f"Boiling point: {boiling}\n"
            f"Density:       {density}\n\n"
            f"Electron config: {element.electron_configuration}\n"
            f"Electronegativity: {electronegativity}\n"
            f"Atomic radius: {atomic_radius}\n"
            f"Oxidation states: {oxidation_states}\n\n"
            f"{element.summary}"
        )

        period_values = [
            e.electronegativity
            for e in _ELEMENTS_BY_PERIOD.get(element.period, [])
            if e.electronegativity is not None
        ]
        if period_values:
            trend_label.update(f"Electronegativity across period {element.period}")
            sparkline.data = period_values
        else:
            trend_label.update("")
            sparkline.data = []


class PeriodicTableApp(App[None]):
    """Textual application that renders an interactive periodic table."""

    TITLE = "Periodic Table"
    CSS = """
    Screen {
        layout: vertical;
    }

    #search {
        margin: 0 1;
    }

    #body {
        height: 1fr;
    }

    #grid {
        layout: grid;
        grid-size: 18 10;
        grid-gutter: 0 1;
        width: 145;
        height: 52;
        padding: 1;
    }

    .tile {
        width: 7;
        height: 5;
        content-align: center middle;
        text-align: center;
        color: black;
        border: round black 50%;
        transition: background 150ms, opacity 150ms;
    }

    .tile:hover {
        border: round white;
    }

    .tile:focus {
        background: $accent;
        text-style: bold reverse;
        border: round $accent;
    }

    .tile.dim {
        opacity: 35%;
    }

    Blank {
        width: 7;
        height: 5;
    }

    #sidebar {
        width: 40;
        border-left: solid $accent;
        padding: 1 2;
    }

    #detail {
        height: auto;
        margin-bottom: 1;
    }

    #detail-text {
        margin-bottom: 1;
    }

    #detail-trend-label {
        color: $text-muted;
        margin-bottom: 1;
    }

    .legend-title {
        text-style: bold;
        margin-bottom: 1;
    }

    .legend-item {
        color: black;
        padding: 0 1;
        margin-bottom: 1;
    }
    """
    for _category, _color in CATEGORY_COLORS.items():
        CSS += f"\n.{_category_class(_category)} {{ background: {_color}; }}\n"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("slash", "focus_search", "Search"),
        ("escape", "clear_search", "Clear search"),
        ("t", "cycle_theme", "Theme"),
        ("question_mark", "toggle_help", "Help"),
    ]

    def on_mount(self) -> None:
        self._tile_by_number = {tile.element.number: tile for tile in self.query(ElementTile)}

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Search by name, symbol, or atomic number…", id="search")
        with Horizontal(id="body"):
            with ElementGrid(), Container(id="grid"):
                for row in range(1, GRID_ROWS + 1):
                    for col in range(1, GRID_COLUMNS + 1):
                        element = _ELEMENTS_BY_POS.get((row, col))
                        if element is None:
                            yield Blank()
                        else:
                            yield ElementTile(element)
            with VerticalScroll(id="sidebar"):
                yield DetailPanel(id="detail")
                yield Legend()
        yield Footer()

    def on_element_tile_selected(self, message: ElementTile.Selected) -> None:
        self.query_one(DetailPanel).element = message.element

    def on_input_changed(self, message: Input.Changed) -> None:
        if message.input.id != "search":
            return
        query = message.value
        first_match: ElementTile | None = None
        for tile in self.query(ElementTile):
            matches = tile.matches(query)
            tile.set_class(not matches, "dim")
            if matches and query and first_match is None:
                first_match = tile
        if first_match is not None:
            first_match.scroll_visible()

    def action_focus_search(self) -> None:
        self.query_one("#search", Input).focus()

    def action_clear_search(self) -> None:
        search = self.query_one("#search", Input)
        if search.value:
            search.value = ""
        for tile in self.query(ElementTile):
            tile.set_class(False, "dim")
        if search.has_focus:
            search.blur()

    def action_cycle_theme(self) -> None:
        try:
            index = THEME_CYCLE.index(self.theme)
        except ValueError:
            index = -1
        self.theme = THEME_CYCLE[(index + 1) % len(THEME_CYCLE)]

    def action_move_focus(self, direction: str) -> None:
        focused = self.focused
        if not isinstance(focused, ElementTile):
            return
        d_period, d_group = _GRID_DIRECTIONS[direction]
        period, group = focused.element.period, focused.element.group
        while True:
            period += d_period
            group += d_group
            if not (1 <= period <= GRID_ROWS and 1 <= group <= GRID_COLUMNS):
                return
            element = _ELEMENTS_BY_POS.get((period, group))
            if element is not None:
                self._tile_by_number[element.number].focus()
                return

    def action_toggle_help(self) -> None:
        if self.screen.query("HelpPanel"):
            self.action_hide_help_panel()
        else:
            self.action_show_help_panel()


def main() -> None:
    PeriodicTableApp().run()


if __name__ == "__main__":
    main()
