"""Shared fixtures for all test modules."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.server import app, set_runtime
from simulation import create_runtime


# ---------------------------------------------------------------------------
# API / unit test fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def tmp_dir():
    # ignore_cleanup_errors=True avoids WinError 32 when SQLite still holds
    # the DB file open during teardown on Windows.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
        yield Path(d)


@pytest.fixture(scope="session")
def runtime(tmp_dir):
    rt = create_runtime(str(tmp_dir))
    set_runtime(rt)
    return rt


@pytest.fixture(scope="session")
def client(runtime):
    """FastAPI TestClient with the sim runtime pre-loaded."""
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


@pytest.fixture()
def first_mortal(client):
    """Return the name of the first living mortal, skipping tests if none exist."""
    r = client.get("/api/mortals")
    mortals = r.json()
    if not mortals:
        pytest.skip("No living mortals — seed failed or population is 0")
    return mortals[0]["name"]


@pytest.fixture()
def active_deity_name(client):
    """Return the name of the first available deity."""
    r = client.get("/api/deities")
    deities = r.json()
    assert deities, "No deities loaded — check contributors/ folder"
    return deities[0]["name"]


# ---------------------------------------------------------------------------
# Playwright / E2E fixtures
# Use installed system Chrome to avoid downloading Chromium (disk space)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Use installed system Chrome via Playwright's channel mechanism.
    This avoids needing to download Playwright's bundled Chromium.
    """
    return {**browser_type_launch_args, "channel": "chrome"}


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1440, "height": 900},
    }
