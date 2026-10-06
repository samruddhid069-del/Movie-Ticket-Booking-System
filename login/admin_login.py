from db import cursor
from services.otp_service import VerifyOtp
from services.admin_service import update_admin_credentials
from utils import get_yes_no, get_password, get_string
from rich.console import Console
from rich.panel import Panel

console = Console()

def admin_login():
    count = 0
    while True:
        try:
            console.print(Panel.fit("[bold cyan]ADMIN LOGIN[/bold cyan]"))
            username = get_string("Enter username :")
            password = get_password("Enter password :")
            
            cursor.execute("SELECT * FROM admins WHERE admin_username=%s AND admin_password=%s", (username, password))
            row = cursor.fetchone()
            
            if row:
                console.print("\n[bold green]Login successful![/bold green]")
                return True
            else:
                console.print("\n[bold red]Invalid credentials[/bold red]")
                count += 1
                
                if count >= 3:
                    console.print("[bold yellow]You have exceeded the maximum number of attempts.[/bold yellow]")
                    if get_yes_no("Do you want to change credentials using OTP?"):
                        email_limit = 0
                        while email_limit < 3:
                            email = get_string("Enter your registered email:")
                            cursor.execute("SELECT * FROM admins WHERE admin_email=%s", (email,))
                            email_row = cursor.fetchone()
                            
                            if email_row:
                                otp = VerifyOtp()
                                if otp.check_login(email, update_admin_credentials):
                                    console.print("[bold green]Please login with your new credentials.[/bold green]")
                                    count = 0 
                                    break
                                else:
                                    return False
                            else:
                                email_limit += 1
                                console.print("[bold red]Email does not match our records.[/bold red]")
                                if email_limit < 3:
                                    console.print(f"[yellow]{3 - email_limit} attempt(s) remaining![/yellow]")
                                    if not get_yes_no("Want to retry?"):
                                        console.print("[bold cyan]Thank you for using our service.[/bold cyan]")
                                        return False
                                else:
                                    console.print("[bold red]Attempts reached! Try after some time.[/bold red]")
                                    return False
                        if count == 0:
                            continue
                        return False
                    else:
                        console.print("[bold cyan]Thank you for using our service.[/bold cyan]")
                        return False
                else:
                    if get_yes_no("Do you want to try again?"):
                        continue
                    else:
                        console.print("[bold cyan]Thank you for using our service.[/bold cyan]")
                        return False
        except Exception as e:
            console.print(f"[bold red]Error: {e}[/bold red]")
            return False