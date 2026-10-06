import sys
import getpass
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from fpdf import FPDF
from rich.console import Console

console = Console()
load_dotenv()

EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def get_yes_no(prompt_msg):
    attempts = 0
    while attempts < 3:
        choice = console.input(f"[bold yellow]{prompt_msg} (y/n): [/bold yellow]").strip().lower()
        if choice == 'y':
            return True
        elif choice == 'n':
            return False
        else:
            console.print("[bold red]❌ Invalid input! Please enter 'y' or 'n'.[/bold red]")
            attempts += 1
    
    console.print("\n[bold red]❌ Too many invalid attempts. Exiting system for security...[/bold red]")
    sys.exit(0)


def get_password(prompt_msg):
    return console.input(f"[bold green]{prompt_msg} [/bold green]")

def get_required(prompt_msg):
    while True:
        value = console.input(f"[bold green]{prompt_msg} [/bold green]").strip().lower()
        if value:
            return value
        console.print("[bold red]❌ This field cannot be empty. Please try again.[/bold red]")

def get_required_password(prompt_msg):
    while True:
        value = get_password(prompt_msg)
        if value:
            return value
        console.print("[bold red]❌ Password cannot be empty. Please try again.[/bold red]")

def get_string(prompt_msg):
    return console.input(f"[bold green]{prompt_msg} [/bold green]").strip().lower()

def send_pdf_email(receiver_email, subject, content_text, filename="document.pdf"):
    """Generates a PDF from text and sends it to the user's email."""
    if not EMAIL or not EMAIL_PASSWORD:
        console.print("[bold red]Email credentials missing in .env file! Cannot send PDF.[/bold red]")
        return False
        
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Replace Rupee symbol with 'Rs.' to prevent FPDF character encoding issues
        content_text = content_text.replace('₹', 'Rs.')
        
        for line in content_text.split('\n'):
            safe_line = line.encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(200, 10, txt=safe_line, ln=True)
            
        pdf.output(filename)

        msg = EmailMessage()
        msg["From"] = EMAIL
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.set_content("Please find your requested document attached below.")

        with open(filename, 'rb') as f:
            pdf_data = f.read()
            
        msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename=filename)

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        os.remove(filename)
        return True
    except Exception as e:
        console.print(f"[bold red]Failed to send email: {e}[/bold red]")
        return False