from db import conn, cursor
from utils import get_password, get_yes_no
from rich.console import Console
from rich.panel import Panel

console = Console()

def update_admin_credentials():
    """Updates password only, keeping it consistent with the user password update rule."""
    while True:
        try:
            console.print(Panel.fit("[bold cyan]UPDATE ADMIN PASSWORD[/bold cyan]"))
            
            cursor.execute("SELECT admin_id FROM admins LIMIT 1")
            row = cursor.fetchone()
            if not row:
                console.print("[bold red]Admin account not found![/bold red]")
                return False

            newpass = get_password("Enter new password :")
            confirm_pass = get_password("Re-enter new password :")
            
            if newpass == confirm_pass:
                if get_yes_no("Are you sure you want to update the admin password?"):
                    cursor.execute("UPDATE admins SET admin_password=%s WHERE admin_id=%s", (newpass, row[0]))
                    conn.commit()
                    console.print("[bold green]✅ Admin password updated successfully![/bold green]")
                    return True
                else:
                    console.print("[bold cyan]Update cancelled.[/bold cyan]")
                    return False
            else:
                console.print("[bold red]❌ Passwords do not match![/bold red]")
                if not get_yes_no("Want to try again?"):
                    return False
        except Exception as e:
            console.print(f"[bold red]Error: {e}[/bold red]")
            return False