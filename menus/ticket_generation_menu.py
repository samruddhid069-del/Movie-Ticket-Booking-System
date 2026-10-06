from rich.console import Console
from rich.panel import Panel
from services.ticket_generation_service import generate_ticket

console = Console()

def ticket_generation_menu(user_id=None):
    while True:
        console.print(Panel.fit("[bold cyan]TICKET GENERATION[/bold cyan]", border_style="cyan"))
        console.print("[bold yellow]1.[/bold yellow] Generate Ticket")
        console.print("[bold yellow]2.[/bold yellow] Back")
        
        choice = console.input("\n[bold green]Enter your choice: [/bold green]").strip()

        if choice == "1":
            if user_id:
                from services.ticket_booking_services import view_booking
                console.print("\n[bold cyan]Your Bookings:[/bold cyan]")
                view_booking(user_id)
                
            booking_id = console.input("\n[bold green]Enter Booking ID: [/bold green]").strip()
            if not booking_id.isdigit():
                console.print("[bold red]Please enter a valid numeric Booking ID.[/bold red]")
                continue
            generate_ticket(int(booking_id), user_id)
        elif choice == "2":
            break
        else:
            console.print("[bold red]Invalid choice. Please select 1 or 2.[/bold red]")