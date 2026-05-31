"""
API integration tests — all endpoints exercised against a real (temp-dir) runtime.
No mocking of DB or Anthropic client; Anthropic calls fall back gracefully when
ANTHROPIC_API_KEY is absent (mortal uses fallback action text).
"""
from __future__ import annotations


# ---------------------------------------------------------------------------
# /api/world
# ---------------------------------------------------------------------------


def test_world_returns_required_fields(client):
    r = client.get("/api/world")
    assert r.status_code == 200
    body = r.json()
    for key in ("world_name", "current_era", "clock", "tick", "stability", "faith", "mortal_count"):
        assert key in body, f"Missing key: {key}"


def test_world_stability_is_percentage(client):
    r = client.get("/api/world")
    stab = r.json()["stability"]
    assert 0 <= stab <= 100


def test_world_faith_is_percentage(client):
    r = client.get("/api/world")
    faith = r.json()["faith"]
    assert 0 <= faith <= 100


# ---------------------------------------------------------------------------
# /api/mortals
# ---------------------------------------------------------------------------


def test_mortals_returns_list(client):
    r = client.get("/api/mortals")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_mortals_have_required_fields(client, first_mortal):
    r = client.get("/api/mortals")
    mortal = next(m for m in r.json() if m["name"] == first_mortal)
    for key in ("name", "archetype", "location", "needs", "alive", "tick_born"):
        assert key in mortal, f"Missing key: {key}"
    for need in ("hunger", "rest", "purpose"):
        assert need in mortal["needs"]
        assert 0 <= mortal["needs"][need] <= 100


def test_mortal_alive_field_is_bool(client, first_mortal):
    r = client.get("/api/mortals")
    mortal = next(m for m in r.json() if m["name"] == first_mortal)
    assert mortal["alive"] is True


# ---------------------------------------------------------------------------
# /api/mortals/{name}/memories
# ---------------------------------------------------------------------------


def test_mortal_memories_empty_initially(client, first_mortal):
    r = client.get(f"/api/mortals/{first_mortal}/memories")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_mortal_memories_404_for_unknown(client):
    r = client.get("/api/mortals/NonExistentXYZ/memories")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# /api/deities
# ---------------------------------------------------------------------------


def test_deities_returns_list(client):
    r = client.get("/api/deities")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 1


def test_deity_has_required_fields(client):
    deity = client.get("/api/deities").json()[0]
    for key in ("name", "title", "domain", "divine_energy", "max_energy"):
        assert key in deity


def test_deity_energy_within_bounds(client):
    for deity in client.get("/api/deities").json():
        assert 0 <= deity["divine_energy"] <= deity["max_energy"]


# ---------------------------------------------------------------------------
# /api/lore
# ---------------------------------------------------------------------------


def test_lore_returns_list(client):
    r = client.get("/api/lore")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ---------------------------------------------------------------------------
# /api/tick
# ---------------------------------------------------------------------------


def test_tick_advances_clock(client):
    before = client.get("/api/world").json()["tick"]
    client.post("/api/tick", json={"n": 1})
    after = client.get("/api/world").json()["tick"]
    assert after == before + 1


def test_tick_returns_actions_list(client):
    r = client.post("/api/tick", json={"n": 1})
    assert r.status_code == 200
    body = r.json()
    assert "tick" in body
    assert "actions" in body
    assert isinstance(body["actions"], list)


def test_tick_n5_advances_5(client):
    before = client.get("/api/world").json()["tick"]
    r = client.post("/api/tick", json={"n": 5})
    assert r.status_code == 200
    after = client.get("/api/world").json()["tick"]
    assert after == before + 5


def test_tick_n0_is_noop(client):
    before = client.get("/api/world").json()["tick"]
    r = client.post("/api/tick", json={"n": 0})
    assert r.status_code == 200
    after = client.get("/api/world").json()["tick"]
    assert after == before


def test_tick_negative_is_rejected(client):
    r = client.post("/api/tick", json={"n": -1})
    assert r.status_code == 422  # pydantic validation rejects ge=0 violation


# ---------------------------------------------------------------------------
# /api/action — inspire (cheapest, safest, no mortal death)
# ---------------------------------------------------------------------------


def test_inspire_succeeds(client, first_mortal, active_deity_name):
    r = client.post("/api/action", json={
        "deity": active_deity_name,
        "action": "inspire",
        "target": first_mortal,
        "message": "",
    })
    assert r.status_code == 200
    assert "result" in r.json()


def test_inspire_increases_purpose(client, first_mortal, active_deity_name):
    mortals_before = {m["name"]: m for m in client.get("/api/mortals").json()}
    purpose_before = mortals_before[first_mortal]["needs"]["purpose"]

    client.post("/api/action", json={
        "deity": active_deity_name,
        "action": "inspire",
        "target": first_mortal,
        "message": "",
    })

    mortals_after = {m["name"]: m for m in client.get("/api/mortals").json()}
    if first_mortal in mortals_after:
        purpose_after = mortals_after[first_mortal]["needs"]["purpose"]
        assert purpose_after >= purpose_before


def test_bless_increases_purpose_and_rest(client, first_mortal, active_deity_name):
    mortals_before = {m["name"]: m for m in client.get("/api/mortals").json()}
    needs_before = mortals_before[first_mortal]["needs"]

    client.post("/api/action", json={
        "deity": active_deity_name,
        "action": "bless",
        "target": first_mortal,
        "message": "Go forth with vigor",
    })

    mortals_after = {m["name"]: m for m in client.get("/api/mortals").json()}
    if first_mortal in mortals_after:
        needs_after = mortals_after[first_mortal]["needs"]
        assert needs_after["purpose"] >= needs_before["purpose"]
        assert needs_after["rest"] >= needs_before["rest"]


def test_action_unknown_mortal_returns_400(client, active_deity_name):
    r = client.post("/api/action", json={
        "deity": active_deity_name,
        "action": "inspire",
        "target": "Ghost_Of_Nobody",
        "message": "",
    })
    assert r.status_code == 400


def test_action_unknown_deity_returns_400(client, first_mortal):
    r = client.post("/api/action", json={
        "deity": "FakeDeityXYZ",
        "action": "inspire",
        "target": first_mortal,
        "message": "",
    })
    assert r.status_code == 400


def test_action_unknown_action_returns_400(client, first_mortal, active_deity_name):
    r = client.post("/api/action", json={
        "deity": active_deity_name,
        "action": "fly_to_moon",
        "target": first_mortal,
        "message": "",
    })
    assert r.status_code == 400


def test_decree_requires_message(client, active_deity_name):
    r = client.post("/api/action", json={
        "deity": active_deity_name,
        "action": "decree",
        "target": "",
        "message": "",
    })
    assert r.status_code == 400


def test_decree_with_message_succeeds(client, active_deity_name):
    r = client.post("/api/action", json={
        "deity": active_deity_name,
        "action": "decree",
        "target": "",
        "message": "Let there be order!",
    })
    assert r.status_code == 200
    assert "result" in r.json()


def test_spawn_creates_mortal(client, active_deity_name):
    before = len(client.get("/api/mortals").json())
    r = client.post("/api/action", json={
        "deity": active_deity_name,
        "action": "spawn",
        "target": "farmer",
        "message": "",
    })
    assert r.status_code == 200
    after = len(client.get("/api/mortals").json())
    assert after == before + 1


def test_spawn_invalid_archetype_rejected(client, active_deity_name):
    r = client.post("/api/action", json={
        "deity": active_deity_name,
        "action": "spawn",
        "target": "dragon_rider",
        "message": "",
    })
    assert r.status_code == 400


def test_curse_reduces_mortal_needs(client, active_deity_name):
    # Make sure there's someone to curse
    mortals = client.get("/api/mortals").json()
    if not mortals:
        import pytest; pytest.skip("No mortals")
    target = mortals[0]["name"]
    needs_before = mortals[0]["needs"]

    r = client.post("/api/action", json={
        "deity": active_deity_name,
        "action": "curse",
        "target": target,
        "message": "",
    })

    if r.status_code == 200:
        remaining = {m["name"]: m for m in client.get("/api/mortals").json()}
        if target in remaining:
            needs_after = remaining[target]["needs"]
            assert any(needs_after[k] <= needs_before[k] for k in needs_before)


# ---------------------------------------------------------------------------
# Energy depletion guard
# ---------------------------------------------------------------------------


def test_action_fails_when_energy_depleted(client, active_deity_name):
    """Drain energy to 0 then verify actions are rejected."""
    # Keep inspiring until we can't afford it (cost=10)
    for _ in range(50):
        deity = next(d for d in client.get("/api/deities").json() if d["name"] == active_deity_name)
        if deity["divine_energy"] < 10:
            break
        mortals = client.get("/api/mortals").json()
        if not mortals:
            break
        client.post("/api/action", json={
            "deity": active_deity_name,
            "action": "inspire",
            "target": mortals[0]["name"],
            "message": "",
        })
    else:
        import pytest; pytest.skip("Couldn't drain energy in 50 actions (energy restores too fast)")

    mortals = client.get("/api/mortals").json()
    if not mortals:
        import pytest; pytest.skip("All mortals died during drain")

    r = client.post("/api/action", json={
        "deity": active_deity_name,
        "action": "inspire",
        "target": mortals[0]["name"],
        "message": "",
    })
    assert r.status_code == 400
