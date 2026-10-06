import os
from dotenv import load_dotenv
import time
import random as r
import smtplib
from email.message import EmailMessage
from utils import get_yes_no
from rich.console import Console

console = Console()

load_dotenv()
EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

class VerifyOtp:
    def __init__(self):
        self.__otp = None
        self.__attempts = 0
    
    def check_attempts(self, receiver, update_function, *args):
        if self.__attempts < 3:
            return self.check_login(receiver, update_function, *args)
        return False

    def check_login(self, receiver, update_function, *args):
        self.__otp = r.randint(1000, 9999)
        msg = EmailMessage()
        msg["From"] = EMAIL
        msg["To"] = receiver
        msg["Subject"] = "Update your credentials - MOVIE TICKET BOOKING SYSTEM"
        msg.set_content(f"Your OTP is : {self.__otp}")
        
        server = None
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
            self.sendtime = time.time()
        except Exception as e:
            console.print(f"[bold red]Failed to send email: {e}[/bold red]")
            return False
        finally:
            if server is not None:
                server.quit()
                
        try:    
            console.print(f"[bold green]✅ An OTP has been sent to your email ({receiver}).[/bold green]")
            userotp_str = console.input("[bold yellow]Enter your OTP to validate : [/bold yellow]").strip()
            
            if not userotp_str.isdigit():
                console.print("[bold red]❌ OTP must be a number.[/bold red]")
                userotp = 0 
            else:
                userotp = int(userotp_str)
                
            self.currenttime = time.time()
            if self.currenttime - self.sendtime > 300:
                console.print("[bold red]❌ OTP Expired (Valid for 5 minutes).[/bold red]")
                if get_yes_no("Resend OTP?"):
                    return self.check_login(receiver, update_function, *args)
                else:
                    console.print("[bold cyan]Thank you for using our service.[/bold cyan]")
                    return False
                    
            if self.__otp == userotp:
                console.print("[bold green]✅ OTP Matched![/bold green]")
                return update_function(*args)
            else:
                console.print("[bold red]❌ OTP Not Matched.[/bold red]")
                self.__attempts += 1
                console.print(f"[bold yellow]{3 - self.__attempts} attempt(s) left![/bold yellow]")
                
                if self.__attempts == 3:
                    console.print("[bold red]❌ Maximum attempts reached! Try after some time.[/bold red]")
                    return False
                    
                if get_yes_no("Resend OTP?"):
                    return self.check_attempts(receiver, update_function, *args)
                else:
                    console.print("[bold cyan]Thank you for using our service.[/bold cyan]")
                    return False
        except Exception as e:
            console.print(f"[bold red]Error: {e}[/bold red]")
            return False