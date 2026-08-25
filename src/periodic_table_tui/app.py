"""A terminal UI for browsing the periodic table of the elements."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer, VerticalScroll
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Footer, Header, Static

from periodic_table_tui.data import CATEGORY_COLORS, ELEMENTS, Element

GRID_COLUMNS = 18
GRID_ROWS = 10

_ELEMENTS_BY_POS: dict[tuple[int, int], Element] = {(e.period, e.group): e for e in ELEMENTS}


def _category_class(category: str) -> str:
    return "cat-" + category.replace(" ", "-")


class ElementTile(Static, can_focus=True):
    """A single clickable/focusable cell representing one element."""

    class Selected(Message):
        def __init__(self, element: Element) -> None:
            self.element = element
            super().__init__()

    def __init__(self, element: Element) -> None:
        text = f"{element.number}\n[b]{element.symbol}[/b]"
        super().__init__(text, classes=f"tile {_category_class(element.category)}")
        self.element = element

    def on_click(self) -> None:
        self.post_message(self.Selected(self.element))
        self.focus()

    def on_focus(self) -> None:
        self.post_message(self.Selected(self.element))


class Blank(Static):
    """An empty, non-interactive spacer cell used to preserve grid alignment."""


class Legend(Static):
    """Static color-key for element categories."""

    def compose(self) -> ComposeResult:
        yield Static("Categories", classes="legend-title")
        for category in CATEGORY_COLORS:
            yield Static(f" {category} ", classes=f"legend-item {_category_class(category)}")


class DetailPanel(Static):
    """Shows information about the currently selected element."""

    element: reactive[Element | None] = reactive(None)

    def watch_element(self, element: Element | None) -> None:
        if element is None:
            self.update("[dim]Select an element to see details.[/dim]")
            return
        self.update(
            f"[b]{element.name}[/b] ({element.symbol})\n\n"
            f"Atomic number: {element.number}\n"
            f"Atomic mass:   {element.mass}\n"
            f"Category:      {element.category}\n\n"
            f"{element.summary}"
        )


class PeriodicTableApp(App[None]):
    """Textual application that renders an interactive periodic table."""

    TITLE = "Periodic Table"
    CSS = """
    Screen {
        layout: vertical;
    }

    #body {
        height: 1fr;
    }

    #grid {
        layout: grid;
        grid-size: 18 10;
        grid-gutter: 0 1;
        width: 109;
        height: 32;
        padding: 1;
    }

    .tile {
        width: 5;
        height: 3;
        content-align: center middle;
        text-align: center;
        color: black;
    }

    .tile:focus {
        background: $accent;
        text-style: bold reverse;
    }

    Blank {
        width: 5;
        height: 3;
    }

    #sidebar {
        width: 36;
        border-left: solid $accent;
        padding: 1 2;
    }

    #detail {
        height: auto;
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
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="body"):
            with ScrollableContainer(), Container(id="grid"):
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


def main() -> None:
    PeriodicTableApp().run()


if __name__ == "__main__":
    main()
