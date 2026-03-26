# Divinity Sim

## What This Is
Divinity Sim is a lightweight god-game I came up after conversation withmy team mates about aspirations it life. 
it features where mortal villagers act as LLM-driven agents with memory, needs, creed, paying taxes and personalities. Developers step in as deities
 through a CLI or browser dashboard. The whole world persists in SQLite and avoids local model inference to stay resource-friendly.

## Requirements
- Python 3.10+
- Around 200MB disk for project files and a virtual environment
- 8GB RAM is fine because there are no local AI models

## Setup
1. Clone the repository.
2. Create a virtual environment with `python -m venv .venv`
3. Activate it and run `pip install -r requirements.txt`
4. Copy `.env.example` to `.env`
5. Add your Anthropic API key
6. Start the app with `python main.py`

The web dashboard is served at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Screenshots
### Dashboard View 1
![Dashboard screenshot 1](./screenshot-1.png)

### Dashboard View 2
![Dashboard screenshot 2](./screenshot-2.png)

### Dashboard View 3
![Dashboard screenshot 3](./screenshot-3.png)

### Dashboard View 4
![Dashboard screenshot 4](./screenshot-4.png)

## Commands
| Command | Description |
|---|---|
| `tick [n]` | Advance the simulation by `n` ticks |
| `observe` | Show all living mortals |
| `pantheon` | Show all loaded deities |
| `lore [n]` | Show the recent chronicle |
| `smite <name>` | Kill a mortal |
| `bless <name> [gift]` | Improve rest and purpose |
| `decree <message>` | Broadcast a divine decree |
| `spawn <archetype>` | Create a new mortal |
| `curse <name>` | Drain a mortal's needs |
| `inspire <name>` | Greatly improve purpose |
| `deity <name>` | Switch the active deity |
| `rename <new_world_name>` | Rename the world |
| `help` | Show command help |
| `quit` | Exit cleanly |

## How Mortals Work
Each mortal has an archetype, traits, a location, and three needs: hunger, rest, and purpose. Their memory stream is stored in SQLite and surfaced by a recency-plus-importance score when preparing prompts. On each tick, the mortal receives world context, recent events, and memory highlights before producing a short in-character action.

## How Deities Work
Each deity has a domain and a finite pool of divine energy that regenerates every tick. Divine actions consume energy and can affect individual mortals or the whole world. Contributor deities are simple JSON files in `contributors/` and are loaded automatically on startup.

## Contributing As A Deity
Fork the project, add a new JSON file in `contributors/`, and open a pull request.

Example:

```json
{
  "name": "YouveryOwnBeloeved name",
  "title": "The Unnamed",
  "domain": "chaos",
  "divine_energy": 100,
  "max_energy": 100,
  "color": "red"
}
```

## Extension Roadmap
- web dashboard expansion
- mortal-to-mortal dialogue
- prayer system
- lore export
- faction rivalries
