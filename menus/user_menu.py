from rich.console import Console
from rich.panel import Panel
from db import cursor
from login.user_login import user_login
from services.user_services import register_user, view_profile, update_profile, update_user_credentials
from menus.ticket_booking_menu import ticket_booking_menu
from menus.payment_menu import payment_menu
from menus.ticket_generation_menu import ticket_generation_menu
from menus.ticket_cancellation_menu import ticket_menu

console = Console()

def user_dashboard(user_id):
    while True:
        try:
            console.print(Panel.fit("[bold cyan]USER DASHBOARD[/bold cyan]", border_style="cyan"))
            console.print("[bold yellow]1.[/bold yellow] View Profile")
            console.print("[bold yellow]2.[/bold yellow] Update Profile")
            console.print("[bold yellow]3.[/bold yellow] Update Password")
            console.print("[bold yellow]4.[/bold yellow] Ticket Booking")
            console.print("[bold yellow]5.[/bold yellow] Payment Management")
            console.print("[bold yellow]6.[/bold yellow] Ticket Generation")
            console.print("[bold yellow]7.[/bold yellow] Ticket Cancellation")
            console.print("[bold yellow]8.[/bold yellow] Back")

            choice = console.input("\n[bold green]Enter your choice : [/bold green]").strip()

            if choice == "1": 
                view_profile(user_id)
            elif choice == "2": 
                update_profile(user_id)
            elif choice == "3": 
                cursor.execute("SELECT email FROM users WHERE user_id = %s", (user_id,))
                row = cursor.fetchone()
                if row:
                    update_user_credentials(row[0])
            elif choice == "4": 
                ticket_booking_menu(user_id)
            elif choice == "5": 
                payment_menu(user_id)
            elif choice == "6": 
                ticket_generation_menu(user_id)
            elif choice == "7": 
                ticket_menu(user_id)
            elif choice == "8":
                console.print("\n[bold green]Logged out successfully![/bold green]")
                break
            else:
                console.print("\n[bold red]Invalid Choice! Try Again.[/bold red]")
        except Exception as e:
            console.print(f"\n[bold red]Error: {e}[/bold red]")

def menu():
    while True:
        try:
            console.print(Panel.fit("[bold cyan]USER MANAGEMENT SYSTEM[/bold cyan]", border_style="cyan"))
            console.print("[bold yellow]1.[/bold yellow] Register")
            console.print("[bold yellow]2.[/bold yellow] Login")
            console.print("[bold yellow]3.[/bold yellow] Back")

            choice = console.input("\n[bold green]Enter your choice : [/bold green]").strip()

            if choice == "1":
                register_user()
            elif choice == "2":
                user_id = user_login()
                if user_id is not None:
                    user_dashboard(user_id)
            elif choice == "3":
                break
            else:
                console.print("\n[bold red]Invalid Choice! Try Again.[/bold red]")
        except Exception as e:
            console.print(f"\n[bold red]Error: {e}[/bold red]")