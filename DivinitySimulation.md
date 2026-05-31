# Divinity Sim — Architecture & Design Reference

> This document describes the architecture of the built system.
> For setup and usage instructions see [README.md](./README.md).

---

## Overview

Divinity Sim is a multi-agent god-game. Mortal villagers are LLM-powered agents with persistent memory and needs. Developers act as deities through a React browser dashboard or a Rich CLI, spending divine energy to influence the simulation.

**Stack:**

| Layer | Technology |
|---|---|
| Backend API | Python 3.12 · FastAPI · uvicorn |
| Persistence | SQLite (single file `data/world.db`) |
| LLM | Anthropic API — `claude-haiku-4-5-20251001` |
| Frontend | React 18 · TypeScript · Vite 5 |
| Real-time | Server-Sent Events (SSE) via `/api/stream` |
| Tests | pytest · pytest-playwright · httpx · system Chrome |

---

## Hard Constraints

| Constraint | Requirement |
|---|---|
| RAM | Runs comfortably under 1 GB total |
| Disk | Code + venv + npm + DB under 500 MB |
| CPU | No local model inference — Anthropic API only |
| Python | 3.10+ minimum, 3.12+ recommended |
| DB | SQLite only — no Postgres, Redis, or Docker |
| LLM | `claude-haiku-4-5-20251001` as default — fast and cheap for tight loops |
| Active mortals | Capped at 10 by default (`SIM_MAX_MORTALS` env var) |

---

## Project Layout

```
divinity-verse-sim/
├── main.py                  # CLI entry point + API server (interactive)
├── start_server.py          # API-only server (headless / tests)
├── simulation.py            # SimulationRuntime, tick loop, divine action dispatcher
├── requirements.txt         # Runtime deps
├── requirements-dev.txt     # Dev/test deps (pytest, playwright, httpx)
├── pytest.ini
│
├── world/
│   ├── clock.py             # SimClock
│   ├── state.py             # WorldState (SQLite)
│   └── events.py            # EventBus (SQLite + callbacks)
│
├── mortals/
│   ├── agent.py             # Mortal class + cognition loop
│   ├── memory.py            # MemoryStream (SQLite)
│   └── archetypes.py        # 8 archetype templates
│
├── deities/
│   ├── deity.py             # Deity dataclass
│   └── pantheon.py          # Pantheon registry
│
├── divine/
│   └── actions.py           # smite, bless, decree, spawn, curse, inspire
│
├── api/
│   ├── server.py            # FastAPI app
│   └── sse.py               # asyncio.Queue → SSE stream
│
├── dashboard/
│   ├── cli.py               # Rich CLI helpers
│   ├── frontend/            # React + Vite source (npm project)
│   └── static/              # Built frontend (gitignored; npm run build)
│
├── tests/
│   ├── conftest.py
│   ├── test_api.py          # 29 API integration tests
│   ├── test_e2e.py          # 20 E2E layout tests
│   └── test_buttons.py      # 21 button interaction tests
│
├── contributors/            # Contributor deity JSON files
└── data/                    # Auto-created (gitignored)
    └── world.db
```

---

## Module Specs

### `world/clock.py` — SimClock

```python
SimClock(tick=0)
  .day         # tick // 24
  .hour        # tick % 24
  .time_of_day # "morning" | "afternoon" | "evening" | "night"
  .advance(n)  # tick += n
  .__str__()   # "Day 3, Hour 14:00 (afternoon)"
```

### `world/state.py` — WorldState

SQLite-backed. Tables: `mortals`, `world_props`.

```
mortals: name (PK), archetype, traits (JSON), location,
         needs (JSON: hunger/rest/purpose 0-100), alive (int), tick_born

world_props: key, value
  Defaults: world_name="Evershade", population_limit="10",
            current_era="Age of Embers", current_tick="0"
```

Key methods: `add_mortal`, `get_mortal`, `get_all_mortals(alive_only=True)`, `update_mortal`, `kill_mortal`, `get_prop`, `set_prop`

### `world/events.py` — EventBus

Persists `WorldEvent` objects to SQLite and fires subscriber callbacks synchronously.

```python
WorldEvent(
  tick, source_type, source_name, event_type,
  description, target_name=None, metadata={}, timestamp
)
# event_type: "action" | "divine_act" | "birth" | "death" | "decree"
# source_type: "mortal" | "deity" | "world"
```

Methods: `emit(event)`, `subscribe(callback)`, `get_recent(limit=20)`, `get_lore(limit=50)`, `get_latest_tick()`

---

### `mortals/archetypes.py`

8 archetypes — each has `traits` (list of 3), `location`, `description`:

| Archetype | Traits | Location |
|---|---|---|
| farmer | hardworking, superstitious, patient | wheat fields |
| merchant | shrewd, sociable, greedy | market square |
| scholar | curious, bookish, skeptical | library |
| guard | loyal, suspicious, disciplined | city gate |
| wanderer | restless, perceptive, unlucky | road outside town |
| priest | devout, manipulative, comforting | temple |
| blacksmith | strong, pragmatic, stubborn | forge |
| thief | cunning, cowardly, opportunistic | shadows near the market |

### `mortals/memory.py` — MemoryStream

SQLite table `memories`: `mortal_name, tick, description, importance (1-10), tags (JSON)`.

Retrieval score: `importance + 1.0 / (1 + age * 0.1)` — higher surfaces first.

Methods: `add`, `retrieve(current_tick, limit=10)`, `to_context_string(current_tick, limit=8)`, `count()`, `recent(limit=20)`

### `mortals/agent.py` — Mortal

```python
Mortal(name, archetype, db_path, tick_born=0)
  .needs          # {"hunger": 80, "rest": 80, "purpose": 80}
  .think_and_act(current_tick, world_context, recent_events) -> str
  .receive_divine_act(act_type, description, tick, importance=8)
  .update_needs(delta)   # clamp 0-100
  .to_dict()
```

`think_and_act` builds a prompt from identity + needs + memories + recent events, calls Anthropic API (`max_tokens=150`), stores result as memory (importance 3), returns action string. Falls back to `"{name} stands still, lost in thought."` on API failure.

---

### `deities/deity.py` — Deity

```python
@dataclass
Deity(name, title, domain, divine_energy=100, max_energy=100, color="white")
  VALID_DOMAINS = {"knowledge", "chaos", "harvest", "war", "fate"}
  .can_act(cost)         # bool
  .spend_energy(cost)    # raises ValueError if insufficient
  .restore_energy(5)     # clamped to max_energy
  .log_intervention(tick, action_type, target, description)
```

### `deities/pantheon.py` — Pantheon

Loads all `contributors/*.json` at startup. Skips files where `name == "YourNameHere"`. Falls back to creating `"Average Diety The Corn"` (domain=knowledge) if no contributor files exist.

Methods: `load_all()`, `get(name)`, `add(deity)`, `list_deities()`, `tick_restore()` (+5 energy to all)

---

### `divine/actions.py`

All action functions share the signature:
```python
def action(deity, target_or_message, world_state, event_bus, tick, **kwargs) -> str
```

| Action | Cost | Effect |
|---|---|---|
| `bless` | 15 | purpose +30, rest +20; mortal receives divine memory (importance 8) |
| `inspire` | 10 | purpose +50; mortal receives divine memory (importance 9) |
| `decree` | 10 | Emits decree event; message stored as `target_or_message` |
| `smite` | 20 | `world_state.kill_mortal(name)`; emits death event |
| `curse` | 20 | All needs −40 (floor 0); mortal receives curse memory |
| `spawn` | 25 | Generates unique name, creates `Mortal`, adds to world; emits birth event |

Name generation uses `NAME_PARTS` (first + last syllables), retries 50 times for uniqueness, falls back to `Nameless{N}`.

---

### `api/server.py` — FastAPI

**Startup (lifespan):** If `runtime` is not pre-set (e.g. when running via uvicorn directly), `create_runtime()` is called automatically.

**CORS origins:** `localhost`, `127.0.0.1`, `:5173`, `:5174`, `:8000`

**Endpoints:**

| Method | Path | Body / Notes |
|---|---|---|
| `GET` | `/api/world` | Returns world_name, current_era, clock, tick, **stability** (avg all needs), **faith** (energy %), mortal_count |
| `GET` | `/api/mortals` | All living mortals |
| `GET` | `/api/mortals/{name}/memories` | Last 20 memories; 404 if not found |
| `GET` | `/api/deities` | All deities |
| `GET` | `/api/lore` | Last 50 events |
| `GET` | `/api/stream` | SSE — `text/event-stream` |
| `POST` | `/api/tick` | `{"n": int (ge=0)}` → `{"tick": N, "actions": [...]}` |
| `POST` | `/api/action` | `{"deity", "action", "target", "message"}` → `{"result": "..."}` or 400 |

Static files: `dashboard/static/` mounted at `/` with HTML fallback (serves the built React app).

### `api/sse.py`

Module-level `asyncio.Queue` (`event_queue`). `push_event(data)` puts items; `sse_stream()` is an async generator yielding `data: {json}\n\n`.

SSE event shapes pushed by the tick loop:
```json
{"type": "action", "tick": 5, "mortal": "Aldric", "text": "Aldric heads to the mill."}
{"type": "tick",   "tick": 5}
{"type": "divine_act", "tick": 5, "mortal": "Aldric", "text": "...", "action": "bless"}
```

---

### `dashboard/frontend/` — React + Vite

**Build:** `npm run build` outputs to `dashboard/static/` (served by FastAPI at `:8000`).  
**Dev:** `npm run dev` runs at `:5173`, proxying `/api` to `:8000`.

Key source files:

| File | Responsibility |
|---|---|
| `src/api.ts` | Typed `fetch` wrappers + `ACTION_COSTS` constant |
| `src/useSimulation.ts` | React hook — world/mortal/deity state, SSE subscription, `doTick`, `divineAction` |
| `src/App.tsx` | 3-column grid shell, error toast |
| `src/components/Header.tsx` | Fixed bar — world name (Playfair Display), essence counter |
| `src/components/MortalsPanel.tsx` | World Status bars + mortal chips with purpose spark-lines |
| `src/components/ActionGrid.tsx` | Viewport image, 5 action buttons (Bless/Smite/Inspire/Curse/Spawn), Tick +1/+5 |
| `src/components/ChroniclePanel.tsx` | SSE feed, Divine Decree terminal input, deity energy bar |

**SSE handling:** `useSimulation.ts` uses `EventSource('/api/stream')`. On `type === "tick"` it refreshes all state; other types are appended to the feed as `FeedEntry` objects.

**Design system:** Glassmorphism dark theme from the Stitch design.
- Background: `#0A0C10` (Void Obsidian)
- Primary (Order): `#a7e0ff` (Cyan)
- Secondary (Chaos): `#ffb4aa` (Crimson)
- Tertiary (Energy): `#ffd44f` (Amber)
- Fonts: Playfair Display (lore) · JetBrains Mono (stats/terminal) · Inter (UI labels)

---

## Simulation Loop (per tick)

```
clock.advance(1)
world_props["current_tick"] = clock.tick
pantheon.tick_restore()           # +5 energy to all deities

for each living mortal:
    action = mortal.think_and_act(tick, world_context, recent_events)
    mortal.update_needs({hunger: -3, rest: -2, purpose: -1})
    world.update_mortal(name, needs=mortal.needs)
    events.emit(WorldEvent(type="action", ...))
    push_event({type:"action", tick, mortal, text})   # → SSE

push_event({type:"tick", tick})                        # → SSE
sleep(SIM_TICK_DELAY)
```

Mortal objects are instantiated lazily each tick from DB records and discarded after — no persistent in-memory mortal list.

---

## Memory Scoring

```python
score = importance + 1.0 / (1 + (current_tick - memory_tick) * 0.1)
```

Higher importance + lower age = surfaces first. Default mortal action memories: importance 3. Divine act memories: importance 8. Inspire: importance 9.

---

## Divine Action Flow

```
POST /api/action {"deity": "...", "action": "smite", "target": "Aldric"}
  → require_runtime()
  → execute_divine_action(rt, deity_name, action_name, target, message)
      → validate action name in ACTION_COSTS
      → deity = pantheon.get(deity_name)   # 400 if not found
      → check deity.can_act(cost)          # 400 if insufficient energy
      → check population cap for spawn     # 400 if at limit
      → action_fn(deity, target, world, events, tick, message=message)
      → deity.spend_energy(cost)
      → push_event to SSE
  → return {"result": "..."}
```

---

## Testing

**`tests/conftest.py`**
- `tmp_dir` — session-scoped temp directory (SQLite lives here; `ignore_cleanup_errors=True` for Windows)
- `runtime` — session-scoped `SimulationRuntime` backed by temp DB
- `client` — `fastapi.testclient.TestClient` with runtime pre-loaded
- `browser_type_launch_args` — overrides Playwright to use `channel="chrome"` (system Chrome, no download)
- `browser_context_args` — sets default viewport to 1440×900

**Test files:**

| File | Tests | Scope |
|---|---|---|
| `test_api.py` | 29 | All REST endpoints, error cases, energy depletion |
| `test_e2e.py` | 20 | Page load, layout, mortal selection, actions, decree, responsive nav |
| `test_buttons.py` | 21 | Every button: error state, success state, feed update |

Run API tests without any server: `pytest tests/test_api.py -v -m "not e2e"`  
Run everything via orchestrator: `.\test.ps1`

---

## Resource Budget

| Resource | Target |
|---|---|
| SQLite DB | < 50 MB per normal play session |
| API calls per tick | 1 per living mortal (max 10 = 10 haiku calls) |
| Tokens per mortal | max_tokens=150 per cognition call |
| Memory queries | SQLite ORDER BY with arithmetic score — no vector store |
| In-memory mortal objects | Instantiated per-tick, not held across ticks |

---

## What's Implemented

- [x] `python main.py` starts without error (with or without API key)
- [x] 4 starter mortals seeded (Aldric/farmer, Mira/merchant, Oswin/scholar, Brin/guard)
- [x] `tick` runs the mortal cognition loop and returns action strings
- [x] `smite`, `bless`, `decree`, `spawn`, `curse`, `inspire` all work with energy enforcement
- [x] Mortal memories persist across ticks and influence future cognition
- [x] `lore` returns a readable text chronicle
- [x] Contributor JSON files in `contributors/` load as playable deities
- [x] Project fits under 500 MB on disk including venv and npm deps
- [x] Graceful fallback on API timeout or bad input — never crashes
- [x] React + Vite dashboard at `localhost:5173` with live SSE chronicle
- [x] All 6 divine actions available in the browser UI
- [x] 70 automated tests (29 API · 20 E2E · 21 button)
- [x] PowerShell scripts for setup, run, build, stop, test

---

*Built for Collin @ Cornmeister LLC. For fun. No mortals were harmed in the making of this simulation.*
