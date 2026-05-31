"""
Button interaction tests — verifies every clickable button in the UI
actually does something observable (state change, UI feedback, feed update).

Runs against the live stack on the shared database, so each test that
clicks an action button first restores energy via ticking.
"""
from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

BASE = "http://localhost:5173"
ARCHETYPES = ["farmer", "merchant", "scholar", "guard", "wanderer", "priest", "blacksmith", "thief"]


# ── Helpers ───────────────────────────────────────────────────────────────────

def load(page: Page, timeout: int = 15_000) -> None:
    """Navigate and wait for React to mount."""
    page.goto(BASE, wait_until="load", timeout=timeout)
    page.wait_for_selector("header", timeout=timeout)
    page.wait_for_selector("button", timeout=timeout)


def select_first_mortal(page: Page) -> str:
    """Click the first mortal chip and return its name."""
    page.wait_for_selector("aside button", timeout=8_000)
    chips = page.locator("aside").first.locator("button")
    first = chips.first
    name = first.inner_text().split("\n")[0].strip()
    first.click()
    page.wait_for_selector(f"text=TARGET: {name}", timeout=5_000)
    return name


def latest_feed_text(page: Page) -> str:
    return page.locator("aside").last.inner_text()


def restore_energy(page: Page, need: int = 30) -> None:
    """Tick until essence in the header is >= need (max 30 ticks of +5)."""
    for _ in range(30):
        header = page.locator("header").inner_text()
        try:
            raw = header.strip().split()[-1].replace(",", "")
            energy = int("".join(c for c in raw if c.isdigit()))
        except (ValueError, IndexError):
            energy = 0
        if energy >= need:
            return
        page.get_by_text("Tick +5", exact=True).click()
        page.wait_for_timeout(1_500)


def ensure_spawn_room(page: Page) -> None:
    """If the population is at the cap, smite one mortal to make room."""
    import requests
    world = requests.get("http://localhost:8000/api/world", timeout=5).json()
    mortals = requests.get("http://localhost:8000/api/mortals", timeout=5).json()
    deities = requests.get("http://localhost:8000/api/deities", timeout=5).json()
    pop_limit = 10  # default SIM_MAX_MORTALS

    if len(mortals) < pop_limit:
        return  # room available

    if not mortals or not deities:
        return

    # Smite the first mortal via the API directly (bypass UI energy check)
    deity_name = deities[0]["name"]
    target = mortals[0]["name"]
    requests.post("http://localhost:8000/api/action", json={
        "deity": deity_name, "action": "smite",
        "target": target, "message": "",
    }, timeout=5)
    page.wait_for_timeout(1_000)
    page.reload(wait_until="load")
    page.wait_for_selector("header", timeout=8_000)


# ── Mortal chip ───────────────────────────────────────────────────────────────

def test_mortal_chip_click_selects_target(page: Page):
    load(page)
    name = select_first_mortal(page)
    expect(page.get_by_text(f"TARGET: {name}")).to_be_visible()


def test_clicking_different_mortal_changes_target(page: Page):
    load(page)
    page.wait_for_selector("aside button", timeout=8_000)
    chips = page.locator("aside").first.locator("button")
    if chips.count() < 2:
        pytest.skip("Need at least 2 mortals")
    chips.nth(0).click()
    first_name = chips.nth(0).inner_text().split("\n")[0].strip()
    page.wait_for_selector(f"text=TARGET: {first_name}", timeout=3_000)
    chips.nth(1).click()
    second_name = chips.nth(1).inner_text().split("\n")[0].strip()
    expect(page.get_by_text(f"TARGET: {second_name}")).to_be_visible(timeout=3_000)


# ── Bless ─────────────────────────────────────────────────────────────────────

def test_bless_without_target_shows_error(page: Page):
    load(page)
    restore_energy(page, need=15)
    page.get_by_text("Bless", exact=True).first.click()
    expect(page.get_by_text("Select a mortal before using bless")).to_be_visible(timeout=3_000)


def test_bless_with_target_updates_feed(page: Page):
    load(page)
    restore_energy(page, need=15)
    select_first_mortal(page)
    before = latest_feed_text(page)
    page.get_by_text("Bless", exact=True).first.click()
    page.wait_for_timeout(3_000)
    after = latest_feed_text(page)
    assert after != before
    assert "blessed" in after.lower(), f"Expected 'blessed' in feed, got: {after[-300:]}"


# ── Smite ─────────────────────────────────────────────────────────────────────

def test_smite_without_target_shows_error(page: Page):
    load(page)
    restore_energy(page, need=20)
    page.get_by_text("Smite", exact=True).first.click()
    expect(page.get_by_text("Select a mortal before using smite")).to_be_visible(timeout=3_000)


def test_smite_with_target_updates_feed(page: Page):
    load(page)
    restore_energy(page, need=45)   # 25 spawn + 20 smite
    # Spawn a fresh mortal to smite so we don't deplete the population
    page.get_by_text("Spawn", exact=True).first.click()
    page.wait_for_selector("select", timeout=3_000)
    page.locator("select").select_option("wanderer")
    page.get_by_text("Spawn", exact=True).nth(1).click()
    page.wait_for_timeout(2_000)

    select_first_mortal(page)
    before = latest_feed_text(page)
    page.get_by_text("Smite", exact=True).first.click()
    page.wait_for_timeout(3_000)
    after = latest_feed_text(page)
    assert after != before
    smite_words = ("smite", "struck down", "perished")
    assert any(w in after.lower() for w in smite_words), \
        f"Expected smite event in feed, got: {after[-300:]}"


# ── Inspire ───────────────────────────────────────────────────────────────────

def test_inspire_without_target_shows_error(page: Page):
    load(page)
    restore_energy(page, need=10)
    page.get_by_text("Inspire", exact=True).first.click()
    expect(page.get_by_text("Select a mortal before using inspire")).to_be_visible(timeout=3_000)


def test_inspire_with_target_updates_feed(page: Page):
    load(page)
    restore_energy(page, need=10)
    select_first_mortal(page)
    before = latest_feed_text(page)
    page.get_by_text("Inspire", exact=True).first.click()
    page.wait_for_timeout(3_000)
    after = latest_feed_text(page)
    assert after != before
    assert "inspire" in after.lower(), f"Expected 'inspire' in feed, got: {after[-300:]}"


# ── Curse ─────────────────────────────────────────────────────────────────────

def test_curse_without_target_shows_error(page: Page):
    load(page)
    restore_energy(page, need=20)
    page.get_by_text("Curse", exact=True).first.click()
    expect(page.get_by_text("Select a mortal before using curse")).to_be_visible(timeout=3_000)


def test_curse_with_target_updates_feed(page: Page):
    load(page)
    restore_energy(page, need=20)
    select_first_mortal(page)
    before = latest_feed_text(page)
    page.get_by_text("Curse", exact=True).first.click()
    page.wait_for_timeout(3_000)
    after = latest_feed_text(page)
    assert after != before
    assert "curse" in after.lower() or "cursed" in after.lower(), \
        f"Expected 'curse' in feed, got: {after[-300:]}"


# ── Spawn ─────────────────────────────────────────────────────────────────────

def test_spawn_opens_archetype_picker(page: Page):
    load(page)
    restore_energy(page, need=25)
    page.get_by_text("Spawn", exact=True).first.click()
    expect(page.locator("select")).to_be_visible(timeout=3_000)
    expect(page.get_by_text("Archetype:")).to_be_visible()


def test_spawn_close_button_hides_picker(page: Page):
    load(page)
    restore_energy(page, need=25)
    page.get_by_text("Spawn", exact=True).first.click()
    page.wait_for_selector("select", timeout=3_000)
    page.locator("button", has_text="×").click()
    page.wait_for_timeout(500)
    assert not page.locator("select").is_visible(), "Picker should be hidden after ×"


def test_spawn_dropdown_contains_all_archetypes(page: Page):
    """Verify every archetype is present in the dropdown — without actually spawning all."""
    load(page)
    restore_energy(page, need=25)
    page.get_by_text("Spawn", exact=True).first.click()
    page.wait_for_selector("select", timeout=3_000)
    options = page.locator("select option").all_inner_texts()
    for arch in ARCHETYPES:
        assert arch in options, f"Archetype '{arch}' missing from dropdown. Got: {options}"
    # Close without spawning
    page.locator("button", has_text="×").click()


def test_spawn_farmer_creates_mortal(page: Page):
    load(page)
    ensure_spawn_room(page)
    restore_energy(page, need=25)
    before = latest_feed_text(page)
    page.get_by_text("Spawn", exact=True).first.click()
    page.wait_for_selector("select", timeout=3_000)
    page.locator("select").select_option("farmer")
    page.get_by_text("Spawn", exact=True).nth(1).click()
    page.wait_for_timeout(2_000)
    after = latest_feed_text(page)
    assert after != before
    assert "farmer" in after.lower(), f"Expected 'farmer' in feed, got: {after[-300:]}"


def test_spawn_merchant_creates_mortal(page: Page):
    load(page)
    ensure_spawn_room(page)
    restore_energy(page, need=25)
    before = latest_feed_text(page)
    page.get_by_text("Spawn", exact=True).first.click()
    page.wait_for_selector("select", timeout=3_000)
    page.locator("select").select_option("merchant")
    page.get_by_text("Spawn", exact=True).nth(1).click()
    page.wait_for_timeout(2_000)
    after = latest_feed_text(page)
    assert after != before
    assert "merchant" in after.lower(), f"Expected 'merchant' in feed, got: {after[-300:]}"


# ── Tick buttons ──────────────────────────────────────────────────────────────

def test_tick1_updates_feed(page: Page):
    load(page)
    before = latest_feed_text(page)
    page.get_by_text("Tick +1", exact=True).click()
    page.wait_for_timeout(4_000)
    after = latest_feed_text(page)
    assert after != before, "Feed did not update after Tick +1"


def test_tick5_updates_feed(page: Page):
    load(page)
    before = latest_feed_text(page)
    page.get_by_text("Tick +5", exact=True).click()
    page.wait_for_timeout(6_000)
    after = latest_feed_text(page)
    assert after != before, "Feed did not update after Tick +5"


def test_tick1_button_shows_loading_state(page: Page):
    load(page)
    page.get_by_text("Tick +1", exact=True).click()
    # During load both tick buttons become "..." (disabled)
    expect(page.get_by_role("button", name="...", exact=True).first).to_be_visible(timeout=3_000)


# ── Decree terminal ───────────────────────────────────────────────────────────

def test_decree_enter_key_submits(page: Page):
    load(page)
    restore_energy(page, need=10)
    terminal = page.locator("input[placeholder='Enter Command...']")
    terminal.fill("ALL SHALL KNEEL")
    terminal.press("Enter")
    page.wait_for_timeout(2_000)
    assert "ALL SHALL KNEEL" in latest_feed_text(page)


def test_decree_empty_does_not_update_feed(page: Page):
    load(page)
    before = latest_feed_text(page)
    terminal = page.locator("input[placeholder='Enter Command...']")
    terminal.fill("")
    terminal.press("Enter")
    page.wait_for_timeout(1_000)
    assert latest_feed_text(page) == before


# ── Error toast dismiss ───────────────────────────────────────────────────────

def test_error_toast_dismiss_button(page: Page):
    load(page)
    restore_energy(page, need=15)
    page.get_by_text("Bless", exact=True).first.click()
    page.wait_for_selector("text=Select a mortal before using bless", timeout=3_000)
    page.locator("button", has_text="×").click()
    page.wait_for_timeout(500)
    assert not page.get_by_text("Select a mortal before using bless").is_visible()
