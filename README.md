# periodic-table-tui

A terminal UI for browsing the periodic table of the elements, built with
[Textual](https://textual.textualize.io/).

Click (or tab to) any element tile to see its name, atomic mass, category,
melting/boiling point, density, electron configuration, electronegativity,
atomic radius, and oxidation states in the side panel, along with a
sparkline of electronegativity across that element's period. Tiles are
color-coded by category, with a legend below the details panel.

## Keys

- `↑`/`↓`/`←`/`→` — move focus between element tiles, following the grid
  (skips the gaps, e.g. jumping straight from period 2 to period 3).
- `/` — focus the search box; filters tiles by name, symbol, or atomic
  number as you type (non-matching tiles dim).
- `esc` — clear the search box.
- `t` — cycle through a handful of built-in color themes.
- `?` — toggle the help panel, listing all available keys and commands.
- `ctrl+p` — open the command palette, which includes "Change theme" for
  the full list of Textual's built-in themes (light and dark).
- `q` — quit.

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
scripts/
    generate_data.py   # regenerates data.py's chemistry fields (dev-only)
tests/
    test_data.py
    test_app.py
```

## Regenerating element data

`data.py`'s core fields (number, symbol, name, mass, category, summary) are
hand-authored. The extra chemistry fields (melting/boiling point, density,
electron configuration, electronegativity, atomic radius, oxidation states)
are generated from the [`mendeleev`](https://mendeleev.readthedocs.io/)
package's data. `mendeleev` is a dev-only dependency — it's not imported by
the app at runtime, only by the generator script:

```sh
uv run python scripts/generate_data.py
# or: pixi run gen-data
```
