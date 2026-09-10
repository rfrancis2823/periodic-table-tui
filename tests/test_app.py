import pytest
from textual.widgets import Input

from periodic_table_tui.app import THEME_CYCLE, DetailPanel, ElementTile, PeriodicTableApp


@pytest.mark.asyncio
async def test_app_boots_and_shows_grid():
    app = PeriodicTableApp()
    async with app.run_test():
        tiles = app.query(ElementTile)
        assert len(tiles) == 118


@pytest.mark.asyncio
async def test_clicking_a_tile_updates_detail_panel():
    app = PeriodicTableApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        hydrogen_tile = next(t for t in app.query(ElementTile) if t.element.symbol == "H")
        await pilot.click(hydrogen_tile)
        await pilot.pause()
        detail = app.query_one(DetailPanel)
        assert detail.element is not None
        assert detail.element.symbol == "H"


@pytest.mark.asyncio
async def test_search_dims_non_matching_tiles():
    app = PeriodicTableApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        search = app.query_one("#search", Input)
        search.focus()
        await pilot.pause()
        await pilot.press(*"hydrogen")
        await pilot.pause()

        tiles = {t.element.symbol: t for t in app.query(ElementTile)}
        assert "dim" not in tiles["H"].classes
        assert "dim" in tiles["He"].classes


@pytest.mark.asyncio
async def test_cycle_theme_action_changes_theme():
    app = PeriodicTableApp()
    async with app.run_test():
        starting_theme = app.theme
        app.action_cycle_theme()
        assert app.theme != starting_theme
        assert app.theme in THEME_CYCLE


@pytest.mark.asyncio
async def test_arrow_keys_move_focus_between_tiles():
    app = PeriodicTableApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        # Lithium (period 2, group 1) has neighbors on all four sides.
        lithium_tile = next(t for t in app.query(ElementTile) if t.element.symbol == "Li")
        lithium_tile.focus()
        await pilot.pause()

        await pilot.press("right")
        await pilot.pause()
        assert app.focused.element.symbol == "Be"

        await pilot.press("down")
        await pilot.pause()
        assert app.focused.element.symbol == "Mg"

        await pilot.press("left")
        await pilot.pause()
        assert app.focused.element.symbol == "Na"

        await pilot.press("left")
        await pilot.pause()
        # Group 0 doesn't exist; focus stays put at the edge of the grid.
        assert app.focused.element.symbol == "Na"


@pytest.mark.asyncio
async def test_toggle_help_shows_and_hides_help_panel():
    app = PeriodicTableApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert not app.screen.query("HelpPanel")

        app.action_toggle_help()
        await pilot.pause()
        assert app.screen.query("HelpPanel")

        app.action_toggle_help()
        await pilot.pause()
        assert not app.screen.query("HelpPanel")
