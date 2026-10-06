from rich.console import Console
from rich.panel import Panel
from services.show_services import add_show, view_shows, search_show, update_show, delete_show

console = Console()

def show_menu():
    while True:
        try:
            console.print(Panel.fit("[bold cyan]SHOW MANAGEMENT[/bold cyan]", border_style="cyan"))
            console.print("[bold yellow]1.[/bold yellow] Add Show")
            console.print("[bold yellow]2.[/bold yellow] View Shows")
            console.print("[bold yellow]3.[/bold yellow] Search Show")
            console.print("[bold yellow]4.[/bold yellow] Update Show")
            console.print("[bold yellow]5.[/bold yellow] Delete Show")
            console.print("[bold yellow]6.[/bold yellow] Back")
            
            choice = console.input("\n[bold green]Enter Choice : [/bold green]").strip()

            if choice == "1": add_show()
            elif choice == "2": view_shows()
            elif choice == "3": search_show()
            elif choice == "4": update_show()
            elif choice == "5": delete_show()
            elif choice == "6": break
            else:
                console.print("[bold red]Invalid Choice! Please enter a number from 1 to 6.[/bold red]")
        except Exception as e:
            console.print(f"[bold red]Error: {e}[/bold red]")