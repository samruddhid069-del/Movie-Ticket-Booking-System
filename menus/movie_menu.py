from rich.console import Console
from rich.panel import Panel
from services.movie_services import add_movie, view_movies, search_movie, update_movie, delete_movie

console = Console()

def menu():
    while True:
        try:
            console.print(Panel.fit("[bold cyan]MOVIE MANAGEMENT SYSTEM[/bold cyan]", border_style="cyan"))
            console.print("[bold yellow]1.[/bold yellow] Add Movie")
            console.print("[bold yellow]2.[/bold yellow] View Movies")
            console.print("[bold yellow]3.[/bold yellow] Search Movie")
            console.print("[bold yellow]4.[/bold yellow] Update Movie")
            console.print("[bold yellow]5.[/bold yellow] Delete Movie")
            console.print("[bold yellow]6.[/bold yellow] Back")

            choice = console.input("\n[bold green]Enter your choice : [/bold green]").strip()

            if choice == "1": add_movie()
            elif choice == "2": view_movies()
            elif choice == "3": search_movie()
            elif choice == "4": update_movie()
            elif choice == "5": delete_movie()
            elif choice == "6":
                break
            else:
                console.print("[bold red]Invalid Choice! Try Again.[/bold red]")
        except Exception as e:
            console.print(f"[bold red]Error: {e}[/bold red]")