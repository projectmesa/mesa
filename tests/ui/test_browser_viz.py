"""Browser-based tests for Mesa's visualization components.

These tests validate that visualization components render and function correctly
in a real browser environment. These are slower than the browser-less tests
and are intended to be run less frequently.
"""

import pytest
from playwright.sync_api import Page


def test_schelling_model_browser(solara_test, page_session: Page):
    """Test that the Schelling model visualizes correctly in a browser."""
    from mesa.examples.basic.schelling.app import page as app_page

    app_page()

    step_button = page_session.locator("button:has-text('Step')")
    step_button.wait_for()

    step_button.click()

    page_session.locator("text=Happy agents:").wait_for()

    # Wait for visualization container instead of specific svg
    visualization_container = page_session.locator(
        '[data-testid="visualization-container"]'
    )
    if visualization_container.count() == 0:  # Fallback if data-testid is not present
        visualization_container = page_session.locator(".visualization-container")
    if visualization_container.count() == 0:  # Further fallback
        visualization_container = page_session.locator(
            "div:has(> svg), div:has(> canvas)"
        )
    visualization_container.wait_for()

    agent_density_slider = page_session.locator("input[type='range']:nth-of-type(1)")
    agent_density_slider.wait_for()

    assert_solara_snapshot = pytest.importorskip("pytest_ipywidgets.solara_snapshots")
    assert_solara_snapshot(page_session.screenshot())


def test_conway_model_browser(solara_test, page_session: Page):
    """Test that the Conway model visualizes correctly in a browser."""
    from mesa.examples.basic.conways_game_of_life.app import page as app_page

    app_page()

    step_button = page_session.locator("button:has-text('Step')")
    step_button.wait_for()

    # Wait for visualization container instead of specific svg
    visualization_container = page_session.locator(
        '[data-testid="visualization-container"]'
    )
    if visualization_container.count() == 0:  # Fallback if data-testid is not present
        visualization_container = page_session.locator(".visualization-container")
    if visualization_container.count() == 0:  # Further fallback
        visualization_container = page_session.locator(
            "div:has(> svg), div:has(> canvas)"
        )
    visualization_container.wait_for()

    before_step = visualization_container.screenshot()
    step_button.click()
    page_session.wait_for_timeout(500)
    after_step = visualization_container.screenshot()

    assert before_step != after_step


def test_boltzmann_model_charts_browser(solara_test, page_session: Page):
    """Test that the Boltzmann model charts render correctly in a browser."""
    from mesa.examples.basic.boltzmann_wealth_model.app import page as app_page

    app_page()

    # Wait for visualization container instead of specific svg
    visualization_container = page_session.locator(
        '[data-testid="visualization-container"]'
    )
    if visualization_container.count() == 0:  # Fallback if data-testid is not present
        visualization_container = page_session.locator(".visualization-container")
    if visualization_container.count() == 0:  # Further fallback
        visualization_container = page_session.locator(
            "div:has(> svg), div:has(> canvas)"
        )
    visualization_container.wait_for()

    play_button = page_session.locator("button:has-text('Play')")
    play_button.wait_for()
    play_button.click()

    page_session.wait_for_timeout(1000)

    pause_button = page_session.locator("button:has-text('Pause')")
    pause_button.wait_for()
    pause_button.click()

    # We still need to check chart paths, but we'll make sure charts are present first
    chart_container = page_session.locator("div:has(> svg path)")
    chart_container.wait_for()
    chart_paths = page_session.locator("svg path")
    assert chart_paths.count() > 0


def test_model_params_update_browser(solara_test, page_session: Page):
    """Test that updating model parameters works correctly."""
    from mesa.examples.basic.schelling.app import page as app_page

    app_page()

    reset_button = page_session.locator("button:has-text('Reset')")
    reset_button.wait_for()

    slider = page_session.locator("input[role='slider']").nth(2)
    slider.wait_for()

    slider.evaluate(
        "slider => { slider.value = slider.max; slider.dispatchEvent(new Event('change')); }"
    )

    reset_button.click()

    # Wait for visualization container instead of specific svg
    visualization_container = page_session.locator(
        '[data-testid="visualization-container"]'
    )
    if visualization_container.count() == 0:  # Fallback if data-testid is not present
        visualization_container = page_session.locator(".visualization-container")
    if visualization_container.count() == 0:  # Further fallback
        visualization_container = page_session.locator(
            "div:has(> svg), div:has(> canvas)"
        )
    visualization_container.wait_for()

    page_session.wait_for_timeout(500)
    assert visualization_container.is_visible()


@pytest.mark.skip(reason="Only run manually to generate reference screenshots")
def test_generate_reference_screenshots(solara_test, page_session: Page):
    """Generate reference screenshots for all example models."""
    from mesa.examples.basic.schelling.app import page as schelling_page

    schelling_page()
    page_session.wait_for_timeout(1000)
    page_session.screenshot(path="schelling_reference.png")

    from mesa.examples.basic.conways_game_of_life.app import page as conway_page

    conway_page()
    page_session.wait_for_timeout(1000)
    page_session.screenshot(path="conway_reference.png")

    from mesa.examples.basic.boltzmann_wealth_model.app import page as boltzmann_page

    boltzmann_page()
    page_session.wait_for_timeout(1000)
    page_session.screenshot(path="boltzmann_reference.png")

    from mesa.examples.basic.virus_on_network.app import page as virus_page

    virus_page()
    page_session.wait_for_timeout(1000)
    page_session.screenshot(path="virus_reference.png")
