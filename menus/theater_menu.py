from rich.console import Console
from rich.panel import Panel
from services.theater_services import add_theater, view_theaters, search_theater, update_theater, delete_theater

console = Console()

def theater_menu():
    while True:
        try:
            console.print(Panel.fit("[bold cyan]THEATER MANAGEMENT[/bold cyan]", border_style="cyan"))
            console.print("[bold yellow]1.[/bold yellow] Add Theater")
            console.print("[bold yellow]2.[/bold yellow] View Theaters")
            console.print("[bold yellow]3.[/bold yellow] Search Theater")
            console.print("[bold yellow]4.[/bold yellow] Update Theater")
            console.print("[bold yellow]5.[/bold yellow] Delete Theater")
            console.print("[bold yellow]6.[/bold yellow] Back")

            choice = console.input("\n[bold green]Enter your choice : [/bold green]").strip()

            if choice == "1": add_theater()
            elif choice == "2": view_theaters()
            elif choice == "3": search_theater()
            elif choice == "4": update_theater()
            elif choice == "5": delete_theater()
            elif choice == "6": break
            else: console.print("\n[bold red]Invalid Choice! Please Try Again.[/bold red]\n")
        except Exception as e:
            console.print(f"[bold red]Error: {e}[/bold red]")