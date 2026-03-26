from __future__ import annotations

import threading
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

from api.server import app, set_runtime
from dashboard.cli import (
    print_action_result,
    print_banner,
    print_deities,
    print_error,
    print_help,
    print_lore,
    print_mortals,
    prompt_command,
)
from mortals.archetypes import list_archetypes
from simulation import create_runtime, execute_divine_action, run_ticks


def start_server() -> None:
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()


def main() -> None:
    load_dotenv()
    runtime = create_runtime(str(Path(__file__).resolve().parent))
    set_runtime(runtime)
    start_server()

    print_help()
    while True:
        print_banner(runtime.world.get_prop("world_name", "Evershade"), str(runtime.clock))
        try:
            raw = prompt_command(runtime.active_deity_name).strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw:
            continue
        parts = raw.split()
        command = parts[0].lower()
        args = parts[1:]

        try:
            if command == "tick":
                n = int(args[0]) if args else 1
                if n < 0:
                    raise ValueError("Tick count cannot be negative.")
                for line in run_ticks(runtime, n):
                    print_action_result(line)
            elif command == "observe":
                print_mortals(runtime.world.get_all_mortals(alive_only=True))
            elif command == "pantheon":
                print_deities(runtime.pantheon.list_deities())
            elif command == "lore":
                limit = int(args[0]) if args else 30
                print_lore(runtime.events.get_lore(limit))
            elif command == "smite":
                print_action_result(execute_divine_action(runtime, runtime.active_deity_name, "smite", target=args[0]))
            elif command == "bless":
                target = args[0]
                message = " ".join(args[1:]) if len(args) > 1 else ""
                print_action_result(execute_divine_action(runtime, runtime.active_deity_name, "bless", target=target, message=message))
            elif command == "decree":
                print_action_result(execute_divine_action(runtime, runtime.active_deity_name, "decree", message=" ".join(args)))
            elif command == "spawn":
                archetype = args[0].lower()
                if archetype not in list_archetypes():
                    raise ValueError("Unknown archetype.")
                print_action_result(execute_divine_action(runtime, runtime.active_deity_name, "spawn", target=archetype))
            elif command == "curse":
                print_action_result(execute_divine_action(runtime, runtime.active_deity_name, "curse", target=args[0]))
            elif command == "inspire":
                print_action_result(execute_divine_action(runtime, runtime.active_deity_name, "inspire", target=args[0]))
            elif command == "deity":
                name = " ".join(args)
                if runtime.pantheon.get(name) is None:
                    raise ValueError("Unknown deity.")
                runtime.active_deity_name = name
                print_action_result(f"Active deity is now {name}.")
            elif command == "rename":
                new_name = " ".join(args).strip()
                if not new_name:
                    raise ValueError("Rename requires a new world name.")
                runtime.world.set_prop("world_name", new_name)
                print_action_result(f"World renamed to {new_name}.")
            elif command == "help":
                print_help()
            elif command == "quit":
                break
            else:
                print_error("Unknown command. Type 'help' to see options.")
        except IndexError:
            print_error("Missing required argument.")
        except ValueError as exc:
            print_error(str(exc))
        except Exception as exc:
            print_error(f"Unexpected error: {exc}")


if __name__ == "__main__":
    main()
