from rich.console import Console
from rich.panel import Panel
from menus.movie_menu import menu as movie_menu
from menus.theater_menu import theater_menu
from menus.show_menu import show_menu
from menus.seat_menu import seat_menu
from menus.ticket_cancellation_menu import ticket_menu
from menus.payment_menu import payment_menu
from menus.ticket_booking_menu import ticket_booking_menu

console = Console()

def admin_menu():
    while True:
        try:
            console.print(Panel.fit("[bold cyan]ADMIN DASHBOARD[/bold cyan]", border_style="cyan"))
            console.print("[bold yellow]1.[/bold yellow] Movie Management")
            console.print("[bold yellow]2.[/bold yellow] Theater Management")
            console.print("[bold yellow]3.[/bold yellow] Show Management")
            console.print("[bold yellow]4.[/bold yellow] Seat Management")
            console.print("[bold yellow]5.[/bold yellow] Ticket Booking")
            console.print("[bold yellow]6.[/bold yellow] Payment Management")
            console.print("[bold yellow]7.[/bold yellow] Ticket Management")
            console.print("[bold yellow]8.[/bold yellow] Back")

            choice = console.input("\n[bold green]Enter your choice : [/bold green]").strip()

            if choice == "1":
                movie_menu()
            elif choice == "2":
                theater_menu()
            elif choice == "3":
                show_menu()
            elif choice == "4":
                seat_menu()
            elif choice == "5":
                user_id_str = console.input("[bold green]Enter the User ID to book a ticket for : [/bold green]").strip()
                if user_id_str.isdigit():
                    ticket_booking_menu(int(user_id_str))
                else:
                    console.print("[bold red]Invalid User ID! It must be a valid number.[/bold red]")
            elif choice == "6":
                payment_menu()
            elif choice == "7":
                ticket_menu()
            elif choice == "8":
                console.print("\n[bold green]Logged out successfully![/bold green]")
                break
            else:
                console.print("[bold red]Invalid Choice! Try Again.[/bold red]")
                
        except Exception as e:
            console.print(f"[bold red]Error: {e}[/bold red]")