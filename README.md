# periodic-table-tui

A terminal UI for browsing the periodic table of the elements, built with
[Textual](https://textual.textualize.io/).

Click (or tab to) any element tile to see its name, atomic mass, category,
and a short summary in the side panel. Tiles are color-coded by category,
with a legend below the details panel.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) or [pixi](https://pixi.sh/) for environment management
- [ruff](https://docs.astral.sh/ruff/) for linting/formatting

## Running it

With `uv`:

```sh
uv run periodic-table-tui
```

With `pixi`:

```sh
pixi run run
```

## Development

```sh
# uv
uv sync --group dev
uv run ruff check .
uv run ruff format .
uv run pytest

# pixi
pixi install -e dev
pixi run -e dev lint
pixi run -e dev format
pixi run -e dev test
```

## Project layout

```
src/periodic_table_tui/
    data.py    # element data (all 118 elements)
    app.py     # Textual app: grid of tiles + detail panel
tests/
    test_data.py
```
