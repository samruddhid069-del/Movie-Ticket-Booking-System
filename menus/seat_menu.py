from rich.console import Console
from rich.panel import Panel
from services.seat_services import add_seat, view_seats, changes_in_seat, delete_seat

console = Console()

def seat_menu():
    while True:
        try:
            console.print(Panel.fit("[bold cyan]SEAT MANAGEMENT[/bold cyan]", border_style="cyan"))
            console.print("[bold yellow]1.[/bold yellow] Add Seats (Modify / Scratch)")
            console.print("[bold yellow]2.[/bold yellow] View Seat Layout and Availability")
            console.print("[bold yellow]3.[/bold yellow] Changes in Seat (Update Type / Block / Unblock)")
            console.print("[bold yellow]4.[/bold yellow] Delete Seat")
            console.print("[bold yellow]5.[/bold yellow] Back")

            choice = console.input("\n[bold green]Enter your choice: [/bold green]").strip()

            if choice == "1": add_seat()
            elif choice == "2": view_seats()
            elif choice == "3": changes_in_seat()
            elif choice == "4": delete_seat()
            elif choice == "5": break
            else:
                console.print("[bold red]Invalid Choice! Try Again.[/bold red]")
        except Exception as e:
            console.print(f"\n[bold red]Error: {e}[/bold red]")