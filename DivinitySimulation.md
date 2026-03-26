# Divinity Sim — Full Build Instructions for Claude Code / Codex

> Hand this file to Claude Code or Codex as your primary prompt.
> It contains everything needed to build the complete application from scratch.

---

## Your Mission

Build **Divinity Sim** — a multi-agent simulation with a web UI where:
- **Mortals** are LLM-powered AI agents with persistent memory, personalities, needs, and daily routines
- **Deities** are developers (users and contributors) who intervene in the world via a browser dashboard or CLI
- The world runs on a tick-based clock, persists all state in SQLite, and costs minimal compute/disk
- A **FastAPI backend** exposes the simulation as a REST + SSE API
- A **single-file vanilla JS frontend** (no Node, no npm, no build step) connects to that API in the browser

This must run comfortably on a **traditional laptop with 8GB RAM and limited disk space**.
There are **no local AI models**. All cognition is handled via the Anthropic API (claude-haiku).

---

## Hard Constraints — Non-Negotiable

| Constraint | Requirement |
|---|---|
| RAM | Must run in under 1GB RAM total |
| Disk | Entire project (code + DB + venv) must stay under 500MB |
| CPU | No model inference locally — Anthropic API only |
| Python | 3.10+ only |
| Dependencies | Minimize packages — no heavy ML/AI frameworks (no torch, tensorflow, transformers, langchain) |
| DB | SQLite only — no Postgres, Redis, Docker, or external services |
| UI | FastAPI backend + single HTML file frontend — no Electron, no npm, no build tools |
| LLM Model | `claude-haiku-4-5-20251001` as default — fast and cheap for simulation loops |
| Active Mortals | Cap at 10 active mortals by default to control API costs |

---

## Project Structure to Build

```
divinity-sim/
├── main.py                    # Entry point — starts FastAPI server + sim loop together
├── requirements.txt           # Lean dependency list
├── .env.example               # API key + config template
├── .gitignore
├── README.md                  # User-facing setup guide
│
├── world/
│   ├── __init__.py
│   ├── clock.py               # Simulation time (ticks → hours → days)
│   ├── state.py               # SQLite world state engine
│   └── events.py              # Event bus — all actions log here
│
├── mortals/
│   ├── __init__.py
│   ├── agent.py               # Mortal class + LLM cognition loop
│   ├── memory.py              # Memory stream with recency+importance scoring
│   └── archetypes.py          # Starter personality templates
│
├── deities/
│   ├── __init__.py
│   ├── deity.py               # Deity dataclass
│   └── pantheon.py            # Registry — loads from contributors/
│
├── divine/
│   ├── __init__.py
│   └── actions.py             # smite, bless, decree, spawn, curse, inspire
│
├── api/
│   ├── __init__.py
│   ├── server.py              # FastAPI app — all REST endpoints
│   └── sse.py                 # Server-Sent Events stream for live tick output
│
├── dashboard/
│   ├── __init__.py
│   ├── cli.py                 # Rich-powered interactive CLI (kept for headless use)
│   └── static/
│       └── index.html         # Single-file frontend — all HTML, CSS, JS in one file
│
├── contributors/
│   └── example_deity.json     # Template for contributor deities
│
└── data/                      # Auto-created at runtime (gitignored)
    └── world.db               # SQLite — all world state + memory + lore
```

---

## Dependency List — Keep It Lean

```
# requirements.txt
anthropic>=0.25.0
python-dotenv>=1.0.0
rich>=13.7.0
click>=8.1.7
fastapi>=0.110.0
uvicorn>=0.29.0
```

**Nothing else.** Do not add langchain, pydantic (unless already a subdependency), numpy, pandas, or any ML library. FastAPI pulls in pydantic automatically — that's fine.

---

## Module Specs

### `world/clock.py`
- `SimClock` class
- `tick` integer counter (starts at 0)
- Properties: `day` (tick // 24), `hour` (tick % 24), `time_of_day` ("morning" / "afternoon" / "evening" / "night")
- `advance(n=1)` method
- `__str__` returns `"Day 3, Hour 14:00 (afternoon)"`

---

### `world/events.py`
- `WorldEvent` dataclass: `tick`, `source_type` ("mortal"/"deity"/"world"), `source_name`, `event_type` ("action"/"divine_act"/"birth"/"death"/"decree"), `description`, `target_name` (optional), `metadata` (dict), `timestamp`
- `EventBus` class backed by SQLite
  - `emit(event)` — persist to DB, fire all subscriber callbacks
  - `subscribe(callback)` — register listener
  - `get_recent(limit=20)` — return list of recent WorldEvents
  - `get_lore(limit=50)` — return recent events formatted as plain text chronicle

---

### `world/state.py`
- `WorldState` class backed by SQLite
- Tables: `mortals`, `world_props`
- Mortals table fields: `name` (PK), `archetype`, `traits` (JSON), `location`, `needs` (JSON: hunger/rest/purpose 0-100), `alive` (int), `tick_born`
- World props: key-value store seeded with `world_name`, `population_limit` (10), `current_era`
- Methods: `add_mortal`, `get_mortal`, `get_all_mortals(alive_only=True)`, `update_mortal`, `kill_mortal`, `get_prop`, `set_prop`

---

### `mortals/archetypes.py`
Define at minimum these 8 archetypes as a dict. Each has `traits` (list of 3), `location` (starting place string), `description`:

- `farmer` — hardworking, superstitious, patient — wheat fields
- `merchant` — shrewd, sociable, greedy — market square
- `scholar` — curious, bookish, skeptical — library
- `guard` — loyal, suspicious, disciplined — city gate
- `wanderer` — restless, perceptive, unlucky — road outside town
- `priest` — devout, manipulative, comforting — temple
- `blacksmith` — strong, pragmatic, stubborn — forge
- `thief` — cunning, cowardly, opportunistic — shadows near the market

Functions: `get_archetype(name)`, `random_archetype()`, `list_archetypes()`

---

### `mortals/memory.py`
- `Memory` dataclass: `tick`, `description`, `importance` (1–10), `tags` (list)
- `MemoryStream` class backed by SQLite table `memories` (mortal_name, tick, description, importance, tags JSON)
- `add(tick, description, importance=5, tags=[])`
- `retrieve(current_tick, limit=10)` — rank by: `importance + (1.0 / (1 + (current_tick - tick) * 0.1))` — higher = surfaces first
- `to_context_string(current_tick, limit=8)` — format as bullet list for prompt injection
- `count()` — total memories for this mortal

---

### `mortals/agent.py`
- `Mortal` class
- Constructor: `name`, `archetype`, `db_path`, `tick_born=0`
- Loads archetype data, initializes `MemoryStream`, initializes `anthropic.Anthropic` client
- `think_and_act(current_tick, world_context, recent_events) -> str`
  - Builds a prompt that includes: name, archetype, traits, location, needs, memories, recent world events, current time
  - Calls Anthropic API with `max_tokens=150`
  - Stores the resulting action as a memory with `importance=3`
  - Returns the action string
  - Prompt must tell the model: stay in character, 1–2 sentences, no fourth-wall breaking, no AI references
- `receive_divine_act(act_type, description, tick, importance=8)` — stores high-importance divine memory
- `update_needs(delta: dict)` — adjust needs dict, clamp 0–100
- `to_dict()` — serializable representation

---

### `deities/deity.py`
- `Deity` dataclass: `name`, `title`, `domain`, `divine_energy=100`, `max_energy=100`, `color="white"`, `interventions=[]`
- Valid domains: `knowledge`, `chaos`, `harvest`, `war`, `fate`
- `can_act(cost)`, `spend_energy(cost)`, `restore_energy(amount=5)` (clamp to max)
- `log_intervention(tick, action_type, target, description)`

---

### `deities/pantheon.py`
- `Pantheon` class
- `load_all()` — scan `contributors/*.json`, instantiate `Deity` for each
- `get(name)`, `add(deity)`, `list_deities()`
- `tick_restore()` — call `deity.restore_energy(5)` on all deities each tick

---

### `divine/actions.py`
Implement these 6 divine actions as callable functions registered in a `DIVINE_ACTIONS` dict:

| Action | Cost | Effect |
|---|---|---|
| `smite` | 20 | Kill a mortal (set alive=0), emit death event |
| `bless` | 15 | Boost mortal's purpose+30, rest+20; emit divine_act event |
| `decree` | 10 | Emit decree event visible to all; mortals will see it in lore |
| `spawn` | 25 | Create new mortal of given archetype with generated name; emit birth event |
| `curse` | 20 | Drain mortal's needs by 40 each; emit divine_act event |
| `inspire` | 10 | Boost mortal's purpose+50; inject a high-importance memory about receiving inspiration |

Each action function signature: `(deity, target_or_message, world_state, event_bus, tick, **kwargs) -> str` (returns outcome message)

`get_action(name)`, `list_actions()` helper functions.

---

### `dashboard/cli.py`
Use the `rich` library throughout. Implement:

- `print_banner(world_name, clock_str)` — yellow panel header
- `print_mortals(mortals)` — Rich table: Name, Archetype, Location, Hunger, Rest, Purpose
- `print_deities(deities)` — Rich table: Name, Title, Domain, Energy
- `print_lore(lore_str)` — Rich panel with chronicle text
- `print_action_result(result)` — bold green
- `print_error(msg)` — bold red
- `print_help()` — Rich panel listing all commands
- `prompt_command(deity_name)` — colored prompt using `console.input`

---

### `api/server.py`
FastAPI application. Mount it and run with uvicorn. All endpoints return JSON.

**App setup:**
- `app = FastAPI(title="Divinity Sim")`
- Mount `dashboard/static/` as a `StaticFiles` directory at `/`
- Include CORS middleware allowing `localhost` origins (for dev)
- Store shared simulation state (world, clock, events, pantheon, active_mortals) as module-level singletons initialized at startup via a `lifespan` context manager

**Endpoints:**

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/world` | Returns world name, current era, clock string, tick number |
| `GET` | `/api/mortals` | Returns list of all living mortals with name, archetype, location, needs |
| `GET` | `/api/mortals/{name}/memories` | Returns last 20 memories for a named mortal |
| `GET` | `/api/deities` | Returns list of all deities with name, title, domain, energy |
| `GET` | `/api/lore` | Returns last 50 events as a list of `{tick, source_name, description}` objects |
| `POST` | `/api/tick` | Body: `{"n": 1}` — advance simulation by n ticks, run mortal cognition loop, return list of action strings that happened |
| `POST` | `/api/action` | Body: `{"deity": "Collin", "action": "smite", "target": "Aldric", "message": ""}` — execute a divine action, return result string |
| `GET` | `/api/stream` | SSE endpoint — streams live tick events as they happen (see `api/sse.py`) |

**Tick endpoint behavior:** Same mortal loop as the CLI — for each living mortal call `think_and_act`, decay needs, persist to DB, emit event. Return `{"tick": N, "actions": [...]}`.

**Action endpoint behavior:** Look up deity by name, check energy, call the appropriate action function, return `{"result": "..."}`. If deity not found or insufficient energy, return a 400 with a clear error message.

---

### `api/sse.py`
Server-Sent Events for streaming live sim output to the browser.

- Maintain a module-level `asyncio.Queue` called `event_queue`
- `push_event(data: dict)` — puts an item onto the queue (called from the tick loop)
- `sse_stream()` — async generator that yields `data: {json}\n\n` formatted SSE messages from the queue
- The `/api/stream` endpoint in `server.py` uses `StreamingResponse` with `media_type="text/event-stream"` and calls `sse_stream()`
- Events pushed should include: `{type: "action", mortal: "...", text: "..."}` and `{type: "tick", tick: N}`

---

### `dashboard/static/index.html`
**Single file. All HTML, CSS, and JavaScript in one file. No external JS frameworks. No npm. No build step.**

Use only:
- Vanilla JS (ES6+)
- CSS custom properties for theming
- The browser's native `EventSource` API for SSE
- `fetch()` for REST calls

**Visual theme:** Dark fantasy. Dark background (`#0d0d14`), gold/amber accents (`#c9a84c`), muted purple (`#6b4fa0`) for deity elements, desaturated red for danger actions. Monospace font for the lore feed. Clean card layout.

**Layout — three columns:**

```
┌─────────────────────────────────────────────────────┐
│  ⚡ DIVINITY SIM        [World Name]   Day 3 · Noon  │  ← Header bar
├──────────────┬──────────────────────┬────────────────┤
│              │                      │                │
│  MORTALS     │   LIVE FEED          │  DEITY PANEL   │
│              │   (SSE stream)       │                │
│  card per    │   scrolling log      │  Active deity  │
│  mortal —    │   of mortal actions  │  energy bar    │
│  name,       │   and divine events  │                │
│  archetype,  │                      │  Action        │
│  needs bars  │                      │  buttons       │
│              │                      │                │
│              │                      │  PANTHEON      │
│              │                      │  list          │
└──────────────┴──────────────────────┴────────────────┘
│  [Tick +1]  [Tick +5]  [Observe]  [Lore]             │  ← Footer controls
└─────────────────────────────────────────────────────┘
```

**Mortal cards (left column):**
- Name + archetype badge
- Location in italic
- Three small labeled progress bars: Hunger / Rest / Purpose (colored by value — green > 60, yellow > 30, red <= 30)
- Click a mortal card to select it as the current divine action target (highlight the card)

**Live feed (center column):**
- Scrolling div that appends new lines as SSE events arrive
- Mortal actions in white, divine acts in gold, deaths in red, births in green, decrees in purple
- Auto-scrolls to bottom on new events
- `[Tick N]` prefix on each line

**Deity panel (right column):**
- Active deity name + title + domain badge
- Animated energy bar (depletes and regenerates visually)
- Action buttons: Smite, Bless, Curse, Inspire, Decree, Spawn
  - Each button shows its energy cost
  - Smite and Curse are styled danger red
  - Bless and Inspire are styled green
  - Decree is styled purple
  - Spawn opens a small inline dropdown to pick archetype
  - Bless and Decree open a small inline text input for gift/message
  - Clicking an action button fires `POST /api/action` with the selected mortal as target (or prompts if none selected)
- Below action buttons: Pantheon list — all deities with name, domain, energy; click to switch active deity

**Footer controls:**
- `[Tick +1]` and `[Tick +5]` buttons — call `POST /api/tick`
- `[Observe]` — refreshes the mortal list
- `[Lore]` — opens a modal overlay showing the full chronicle from `GET /api/lore`

**Lore modal:**
- Overlay with blurred backdrop
- Scrollable list of all lore events, newest at top
- Click anywhere outside to close

**Polling:** On page load, fetch `/api/world`, `/api/mortals`, `/api/deities`. Connect to `/api/stream` via `EventSource`. Re-fetch mortals after every tick response to update need bars.

**Error handling:** If a fetch fails, show a small red toast notification in the top-right corner that disappears after 3 seconds.

---

### `main.py` (updated for frontend)
The main loop. Responsibilities:

1. Load `.env` (dotenv)
2. Initialize `WorldState`, `SimClock`, `EventBus`, `Pantheon`
3. Load pantheon from `contributors/`. If empty, create default deity `Collin, The Architect, domain=knowledge`
4. Seed world with 4 starter mortals if DB is empty: Aldric (farmer), Mira (merchant), Oswin (scholar), Brin (guard)
5. Enter interactive CLI loop:
   - Print banner each iteration
   - Read command from `prompt_command`
   - Dispatch to handlers

**Commands to implement:**

| Command | Description |
|---|---|
| `tick [n]` | Advance clock by n ticks (default 1). Each tick: restore deity energy, run mortal cognition loop, print each mortal's action |
| `observe` | Print mortal table |
| `pantheon` | Print deity table |
| `lore [n]` | Print last n events as chronicle (default 30) |
| `smite <name>` | Execute smite action as active deity |
| `bless <name> [gift]` | Execute bless action |
| `decree <message>` | Execute decree action |
| `spawn <archetype>` | Execute spawn action |
| `curse <name>` | Execute curse action |
| `inspire <name>` | Execute inspire action |
| `deity <name>` | Switch active deity |
| `rename <new_world_name>` | Update world name in world_props |
| `help` | Print help panel |
| `quit` | Exit cleanly |

**Mortal tick loop:** For each living mortal, call `think_and_act`, decay needs by hunger-3/rest-2/purpose-1, persist updated needs to DB, emit action event, print to console.

**Error handling:** Wrap Anthropic API calls in try/except. If API fails, mortal produces a fallback action like `"{name} stands still, lost in thought."` — never crash the sim.

**Population cap:** If `get_all_mortals()` returns >= `SIM_MAX_MORTALS` (from env, default 10), block `spawn` and print an error message.

---

### `contributors/example_deity.json`

```json
{
  "name": "YourNameHere",
  "title": "The Unnamed",
  "domain": "chaos",
  "divine_energy": 100,
  "max_energy": 100,
  "color": "red"
}
```

Include a comment block above it in the README explaining how contributors fork + add their deity JSON + PR.

---

### `.env.example`

```
ANTHROPIC_API_KEY=your_key_here
SIM_MODEL=claude-haiku-4-5-20251001
SIM_MAX_MORTALS=10
SIM_TICK_DELAY=0
```

---

### `README.md` — Include These Sections

1. **What This Is** — 3 sentence summary of the god-game concept
2. **Requirements** — Python 3.10+, ~200MB disk, 8GB RAM fine (no local models)
3. **Setup** — clone, venv, pip install, cp .env.example, add API key, python main.py
4. **Commands** — table of all CLI commands
5. **How Mortals Work** — memory stream, cognition loop, needs
6. **How Deities Work** — energy system, domains, contributor JSON format
7. **Contributing as a Deity** — fork, add JSON, PR
8. **Extension Roadmap** — web dashboard, mortal-to-mortal dialogue, prayer system, lore export, faction rivalries

---

## Resource Budget Guidelines

- **DB size:** The SQLite DB should stay under 50MB for a normal play session. Memory entries are small strings — this is achievable easily.
- **API calls per tick:** 1 call per living mortal. At 10 mortals = 10 haiku calls per tick. Keep `max_tokens=150` per mortal.
- **In-memory:** Lazy-load `Mortal` agent objects only when they take a tick action. Do not hold all mortal objects in memory simultaneously if population grows.
- **No caching libraries, no in-memory vector stores.** SQLite ORDER BY with arithmetic scoring is sufficient for memory retrieval at this scale.

---

## What Done Looks Like

The simulation is complete when:

- [ ] `python main.py` starts without error (with a valid API key)
- [ ] 4 starter mortals are seeded and visible in `observe`
- [ ] `tick` runs the mortal cognition loop and prints each mortal's action
- [ ] `smite`, `bless`, `decree`, `spawn`, `curse`, `inspire` all work with energy cost enforcement
- [ ] Mortal memories persist across ticks and influence future behavior
- [ ] `lore` returns a readable text chronicle of past events
- [ ] A contributor JSON file in `contributors/` is loaded as a playable deity
- [ ] The entire project fits in under 500MB on disk including the venv
- [ ] No crashes on API timeout or bad input — graceful error handling throughout

---

*Built for Collin @ Cornmeister LLC. For fun. No mortals were harmed in the making of this simulation.*