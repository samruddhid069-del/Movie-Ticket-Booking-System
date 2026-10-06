from rich.console import Console
from rich.panel import Panel
from services.payment_services import view_payments, generate_receipt

console = Console()

def payment_menu(user_id=None):
    while True:
        console.print(Panel.fit("[bold cyan]PAYMENT MANAGEMENT[/bold cyan]", border_style="cyan"))
        console.print("[bold yellow]1.[/bold yellow] View Payment History")
        console.print("[bold yellow]2.[/bold yellow] Generate Receipt")
        console.print("[bold yellow]3.[/bold yellow] Back")

        choice = console.input("\n[bold green]Enter your choice: [/bold green]").strip()

        if choice == "1":
            view_payments(user_id)
        elif choice == "2":
            generate_receipt(user_id)
        elif choice == "3":
            break
        else:
            console.print("[bold red]Invalid choice. Please select 1, 2, or 3.[/bold red]")