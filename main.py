from login.admin_login import admin_login
from menus.user_menu import menu as user_menu
from menus.admin_menu import admin_menu
from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    while True:
        console.print(Panel.fit("[bold cyan]🍿 MOVIE TICKET BOOKING SYSTEM 🍿[/bold cyan]", border_style="cyan"))
        console.print("[bold yellow]1.[/bold yellow] Admin Panel")
        console.print("[bold yellow]2.[/bold yellow] User Panel")
        console.print("[bold yellow]3.[/bold yellow] Exit")
        
        choice = console.input("\n[bold green]Enter your choice: [/bold green]").strip()
        
        if choice == "1":
            if admin_login():
                admin_menu()
        elif choice == "2":
            user_menu()
        elif choice == "3":
            console.print("\n[bold green]Thank you for using the system. Goodbye![/bold green]\n")
            break
        else:
            console.print("\n[bold red]❌ Invalid choice. Please try again.[/bold red]")

if __name__ == "__main__":
    main()