import pytest

from periodic_table_tui.app import DetailPanel, ElementTile, PeriodicTableApp


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
