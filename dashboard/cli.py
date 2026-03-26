from __future__ import annotations

from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

console = Console()


def print_banner(world_name: str, clock_str: str) -> None:
    console.print(
        Rule(
            "[bold yellow]<3 Divinity Sim <3[/bold yellow]",
            style="bold purple",
            characters="=",
        )
    )
    console.print(
        Panel.fit(
            Align.center(
                f"[bold yellow]DIVINITY SIM[/bold yellow]\n"
                f"[bold white on rgb(65,40,10)]  {world_name}  [/bold white on rgb(65,40,10)]\n"
                f"[italic bright_black]{clock_str}[/italic bright_black]"
            ),
            border_style="bright_yellow",
            box=box.DOUBLE,
            padding=(1, 5),
            title="[bold purple]Temple Of The CLI[/bold purple]",
            subtitle="[bold yellow]Sacred Console <3[/bold yellow]",
        )
    )
    console.print(Rule(style="bold purple", characters="="))


def print_mortals(mortals: list[dict]) -> None:
    table = Table(title="Mortals")
    for column in ["Name", "Archetype", "Location", "Hunger", "Rest", "Purpose"]:
        table.add_column(column)
    for mortal in mortals:
        table.add_row(
            mortal["name"],
            mortal["archetype"],
            mortal["location"],
            str(mortal["needs"]["hunger"]),
            str(mortal["needs"]["rest"]),
            str(mortal["needs"]["purpose"]),
        )
    console.print(table)


def print_deities(deities) -> None:
    table = Table(title="Pantheon")
    for column in ["Name", "Title", "Domain", "Energy"]:
        table.add_column(column)
    for deity in deities:
        table.add_row(deity.name, deity.title, deity.domain, str(deity.divine_energy))
    console.print(table)


def print_lore(lore_str: str) -> None:
    console.print(Panel(lore_str or "No lore has been written yet.", title="Chronicle"))


def print_action_result(result: str) -> None:
    console.print(f"[bold green]{result}[/bold green]")


def print_error(msg: str) -> None:
    console.print(f"[bold red]{msg}[/bold red]")


def print_help() -> None:
    commands = """tick [n]
observe
pantheon
lore [n]
smite <name>
bless <name> [gift]
decree <message>
spawn <archetype>
curse <name>
inspire <name>
deity <name>
rename <new_world_name>
help
quit"""
    console.print(Panel(commands, title="Commands"))


def prompt_command(deity_name: str) -> str:
    return console.input(f"[bold cyan]{deity_name}[/bold cyan][white] > [/white]")
