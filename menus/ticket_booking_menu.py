from rich.console import Console
from rich.panel import Panel
from db import cursor
from utils import get_password
from services.ticket_booking_services import book_ticket, view_booking
from services.seat_services import view_seats

console = Console()

def verify_user(user_id):
    attempts = 0
    while attempts < 3:
        pwd = get_password("Enter your password to access ticket booking :")
        cursor.execute("SELECT password FROM users WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        if row and row[0] == pwd:
            return True
        else:
            console.print("[bold red]❌ Incorrect password![/bold red]")
            attempts += 1
            if attempts < 3:
                console.print(f"[yellow]{3 - attempts} attempt(s) remaining.[/yellow]")
    
    console.print("[bold red]❌ Maximum attempts reached. Access denied.[/bold red]")
    return False

def ticket_booking_menu(user_id):
    if not verify_user(user_id):
        return

    while True:
        try:
            console.print(Panel.fit("[bold cyan]TICKET BOOKING MENU[/bold cyan]", border_style="cyan"))
            console.print("[bold yellow]1.[/bold yellow] Book Ticket")
            console.print("[bold yellow]2.[/bold yellow] Check Seat Availability")
            console.print("[bold yellow]3.[/bold yellow] View Booking")
            console.print("[bold yellow]4.[/bold yellow] Back")

            choice = console.input("\n[bold green]Enter your choice : [/bold green]").strip()

            if choice == "1": 
                book_ticket(user_id)
            elif choice == "2": 
                view_seats()
            elif choice == "3": 
                view_booking(user_id)
            elif choice == "4": 
                break
            else:
                console.print("[bold red]Invalid Choice! Please select 1-4.[/bold red]")
        except Exception as e:
            console.print(f"[bold red]Menu Error: {e}[/bold red]")