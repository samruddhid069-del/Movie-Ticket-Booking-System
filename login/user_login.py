from db import cursor
from services.otp_service import VerifyOtp
from services.user_services import update_user_credentials
from utils import get_yes_no, get_password, get_string
from rich.console import Console
from rich.panel import Panel

console = Console()

def user_login():
    count = 0
    while True:
        try:
            console.print(Panel.fit("[bold cyan]USER LOGIN[/bold cyan]"))
            username = get_string("Enter username :")
            password = get_password("Enter password :")
            
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            row = cursor.fetchone()
            if row is not None:
                console.print("[bold green]Login successful[/bold green]")
                return row[0] 
            else:
                console.print("[bold red]Invalid credentials[/bold red]")
                count += 1
                if count >= 3:
                    console.print("[bold yellow]You have exceeded the maximum number of attempts. Please try again later.[/bold yellow]")
                    if get_yes_no("Do you want to change credentials?"):
                        limit = 0
                        while limit < 3:
                            email = get_string("Enter your registered email:")
                            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
                            email_row = cursor.fetchone()
                            
                            if email_row is None:
                                limit += 1
                                console.print("[bold red]Email does not match our records.[/bold red]")
                                if limit < 3:    
                                    console.print(f"[yellow]{3-limit} attempt(s) remaining![/yellow]")                          
                                    if not get_yes_no("Want to retry again?"):                              
                                        console.print("[bold cyan]Thank you for using our service.[/bold cyan]")
                                        return None  
                                else:
                                    console.print("[bold red]Attempts Reached! Try after some time.[/bold red]")
                                    return None
                            else:
                                otp = VerifyOtp()
                                if otp.check_login(email, update_user_credentials, email):
                                    console.print("[bold green]Please login with your new credentials.[/bold green]")
                                    count = 0
                                    break
                                else:
                                    return None
                        if count == 0:
                            continue
                        return None
                    else:
                        console.print("[bold cyan]Thank you for using our service.[/bold cyan]")
                        return None
                else:
                    if get_yes_no("Do you want to try again?"):
                        continue
                    else:
                        console.print("[bold cyan]Thank you for using our service.[/bold cyan]")
                        return None
        except Exception as e:
            console.print(f"[bold red]Error: {e}[/bold red]")
            return None