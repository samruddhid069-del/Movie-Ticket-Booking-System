from rich.console import Console
from rich.panel import Panel
from services.ticket_cancellation_service import view_tickets, search_ticket, cancel_ticket, view_cancelled_tickets

console = Console()

def ticket_menu(user_id=None):
    while True:
        try:
            console.print(Panel.fit("[bold cyan]🎟️ TICKET MANAGEMENT[/bold cyan]", border_style="cyan"))
            console.print("[bold yellow]1.[/bold yellow] View Active Tickets")
            console.print("[bold yellow]2.[/bold yellow] Search Ticket")
            console.print("[bold yellow]3.[/bold yellow] Cancel Ticket")
            console.print("[bold yellow]4.[/bold yellow] View Cancelled Tickets")
            console.print("[bold yellow]5.[/bold yellow] Back")
            
            choice = console.input("\n[bold green]Enter Choice : [/bold green]").strip()

            if choice == "1": view_tickets(user_id)
            elif choice == "2": search_ticket(user_id)
            elif choice == "3": cancel_ticket(user_id)
            elif choice == "4": view_cancelled_tickets(user_id)
            elif choice == "5": break
            else:
                console.print("[bold red]❌ Invalid Choice! Please enter a number from 1 to 5.[/bold red]")
        except Exception as e:
            console.print(f"[bold red]❌ Unexpected Error: {e}[/bold red]")