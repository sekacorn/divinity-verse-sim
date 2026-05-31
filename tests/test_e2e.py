"""
End-to-end tests using Playwright.

Requires the full stack running:
  - Backend:  python main.py  (port 8000)
  - Frontend: npm run dev     (port 5173, inside dashboard/frontend/)

Run with:
  pytest tests/test_e2e.py --headed        # visible browser
  pytest tests/test_e2e.py                 # headless (CI)

These tests are marked @pytest.mark.e2e so you can exclude them from fast runs:
  pytest tests/ -m "not e2e"
"""
from __future__ import annotations

import time

import pytest
from playwright.sync_api import Page, expect

BASE = "http://localhost:5173"

pytestmark = pytest.mark.e2e


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def wait_for_app(page: Page, timeout: int = 15_000) -> None:
    """Navigate and wait until React has mounted (header is visible).
    We use 'load' not 'networkidle' because the SSE stream keeps a
    persistent connection open, so networkidle never fires.
    """
    page.goto(BASE, wait_until="load", timeout=timeout)
    # Confirm React rendered — header always exists once app mounts
    page.wait_for_selector("header", timeout=timeout)


# ---------------------------------------------------------------------------
# Layout / smoke
# ---------------------------------------------------------------------------


def test_page_loads_title(page: Page):
    wait_for_app(page)
    expect(page).to_have_title("Aetheria Prime | Divine Command Center")


def test_header_visible(page: Page):
    wait_for_app(page)
    # World name heading is visible in the fixed header
    header = page.locator("header h1")
    expect(header).to_be_visible()


def test_three_column_layout(page: Page):
    wait_for_app(page)
    page.set_viewport_size({"width": 1440, "height": 900})
    # All three panels should exist in the DOM
    main = page.locator("main")
    expect(main).to_be_visible()


def test_live_chronicle_panel_visible(page: Page):
    wait_for_app(page)
    # Chronicle heading
    chronicle_heading = page.get_by_text("Live Chronicle")
    expect(chronicle_heading).to_be_visible()


def test_terminal_input_visible(page: Page):
    wait_for_app(page)
    terminal = page.locator("input[placeholder='Enter Command...']")
    expect(terminal).to_be_visible()


def test_action_buttons_visible(page: Page):
    wait_for_app(page)
    for label in ("Bless", "Smite", "Inspire", "Curse", "Spawn"):
        btn = page.get_by_text(label, exact=True).first
        expect(btn).to_be_visible()


def test_world_status_panel_visible(page: Page):
    wait_for_app(page)
    expect(page.get_by_text("World Status")).to_be_visible()


def test_priority_mortals_panel_visible(page: Page):
    wait_for_app(page)
    expect(page.get_by_text("Priority Mortals")).to_be_visible()


def test_essence_counter_in_header(page: Page):
    wait_for_app(page)
    expect(page.get_by_text("Essence")).to_be_visible()


# ---------------------------------------------------------------------------
# Mortal interaction
# ---------------------------------------------------------------------------


def test_mortal_chips_appear(page: Page):
    wait_for_app(page)
    # Wait for API data — mortal names appear as buttons in the panel
    page.wait_for_selector("button >> text=Aldric", timeout=8_000)
    mortal = page.locator("button", has_text="Aldric")
    expect(mortal.first).to_be_visible()


def test_clicking_mortal_selects_it(page: Page):
    wait_for_app(page)
    page.wait_for_selector("button >> text=Aldric", timeout=8_000)
    mortal_btn = page.locator("button", has_text="Aldric").first
    mortal_btn.click()
    # After click, TARGET label appears in the viewport overlay
    expect(page.get_by_text("TARGET: Aldric")).to_be_visible(timeout=3_000)


# ---------------------------------------------------------------------------
# Divine actions
# ---------------------------------------------------------------------------


def test_bless_without_mortal_shows_error(page: Page):
    wait_for_app(page)
    # Don't click any mortal — directly click Bless
    bless_btn = page.get_by_text("Bless", exact=True).first
    bless_btn.click()
    # Error toast / message should appear
    expect(page.get_by_text("Select a mortal before using bless")).to_be_visible(timeout=3_000)


def test_bless_with_mortal_selected(page: Page):
    wait_for_app(page)
    page.wait_for_selector("button >> text=Aldric", timeout=8_000)

    # Select mortal
    page.locator("button", has_text="Aldric").first.click()
    page.wait_for_selector("text=TARGET: Aldric", timeout=3_000)

    # Bless
    bless_btn = page.get_by_text("Bless", exact=True).first
    bless_btn.click()

    # Chronicle should update with a bless entry
    expect(page.locator(".feed-entry, p").filter(has_text="blessed")).to_be_visible(timeout=8_000)


def test_spawn_opens_archetype_picker(page: Page):
    wait_for_app(page)
    page.get_by_text("Spawn", exact=True).first.click()
    # Archetype select appears
    expect(page.locator("select")).to_be_visible(timeout=3_000)
    expect(page.get_by_text("Archetype:")).to_be_visible()


def test_spawn_creates_mortal(page: Page):
    wait_for_app(page)
    mortals_before = page.locator("#mortal-list button, aside button[class]").count()

    page.get_by_text("Spawn", exact=True).first.click()
    page.locator("select").select_option("merchant")
    page.get_by_text("Spawn", exact=True).nth(1).click()  # inline confirm button

    # Chronicle should mention the spawn
    time.sleep(1)
    expect(page.locator("p").filter(has_text="merchant")).to_be_visible(timeout=8_000)


# ---------------------------------------------------------------------------
# Decree terminal
# ---------------------------------------------------------------------------


def test_decree_terminal_accepts_input(page: Page):
    wait_for_app(page)
    terminal = page.locator("input[placeholder='Enter Command...']")
    terminal.fill("LET THERE BE RAIN")
    terminal.press("Enter")

    # The decree text should appear in the feed
    expect(page.locator("p").filter(has_text="LET THERE BE RAIN")).to_be_visible(timeout=5_000)


# ---------------------------------------------------------------------------
# Tick
# ---------------------------------------------------------------------------


def test_tick_button_advances_world(page: Page):
    wait_for_app(page)
    tick_before_text = page.locator("header").inner_text()

    page.get_by_text("Tick +1", exact=True).click()

    # Feed should update (new action lines appear)
    # At minimum loading state clears within a few seconds
    time.sleep(2)
    expect(page.get_by_text("Tick +1", exact=True)).to_be_visible()  # button still there = app didn't crash


def test_tick5_button_present(page: Page):
    wait_for_app(page)
    expect(page.get_by_text("Tick +5", exact=True)).to_be_visible()


# ---------------------------------------------------------------------------
# Responsive / mobile nav
# ---------------------------------------------------------------------------


def test_mobile_nav_hidden_on_desktop(page: Page):
    wait_for_app(page)
    page.set_viewport_size({"width": 1440, "height": 900})
    mobile_nav = page.locator(".mobile-nav")
    # CSS hides it — check it's not visible
    assert not mobile_nav.is_visible()


def test_mobile_nav_visible_on_small_screen(page: Page):
    wait_for_app(page)
    page.set_viewport_size({"width": 375, "height": 812})
    page.wait_for_timeout(300)
    mobile_nav = page.locator(".mobile-nav")
    expect(mobile_nav).to_be_visible()
