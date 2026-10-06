import mysql.connector
from db import conn, cursor
from utils import get_string, get_password, get_yes_no
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def ask_mandatory(label, lower=True):
    """Keeps asking until the user types something."""
    while True:
        value = console.input(f"[bold green]{label} : [/bold green]").strip()
        if value:
            return value.lower() if lower else value
        console.print(f"[bold red]⚠ {label} is mandatory. Please fill this information.[/bold red]")


def ask_mandatory_password(label):
    while True:
        value = get_password(f"{label} :")
        if value:
            return value
        console.print(f"[bold red]⚠ {label} is mandatory. Please fill this information.[/bold red]")


def register_user():
    try:
        console.print(Panel.fit("[bold cyan]USER REGISTRATION[/bold cyan]"))
        console.print("[bold yellow]All fields are mandatory.[/bold yellow]")

        full_name = ask_mandatory("Full Name")

        while True:
            email = ask_mandatory("Email")
            if "@" in email and "." in email.split("@")[-1]:
                break
            console.print("[bold red]❌ Enter a valid email (example: name@gmail.com).[/bold red]")

        while True:
            mobile = ask_mandatory("Mobile", lower=False)
            if mobile.isdigit() and len(mobile) == 10:
                break
            console.print("[bold red]❌ Mobile must be exactly 10 digits.[/bold red]")

        username = ask_mandatory("Username")

        while True:
            password = ask_mandatory_password("Password")
            confirm_password = ask_mandatory_password("Confirm Password")
            if password == confirm_password:
                break
            console.print("[bold red]❌ Passwords do not match. Please try again.[/bold red]")

        cursor.execute(
            "INSERT INTO users (full_name, email, mobile, username, password) VALUES (%s, %s, %s, %s, %s)",
            (full_name, email, mobile, username, password),
        )
        conn.commit()
        console.print(Panel(f"[bold green]✅ Registration Successful![/bold green]\n[bold yellow]Your User ID is : {cursor.lastrowid}[/bold yellow]"))
    except mysql.connector.IntegrityError:
        conn.rollback()
        console.print("[bold red]❌ Registration Failed! Email, Mobile or Username already exists.[/bold red]")
    except Exception as e:
        conn.rollback()
        console.print(f"[bold red]Error: {e}[/bold red]")


def view_profile(user_id):
    try:
        cursor.execute("SELECT user_id, full_name, email, mobile, username FROM users WHERE user_id = %s", (user_id,))
        user_record = cursor.fetchone()
        if not user_record:
            console.print("[bold red]❌ User Not Found.[/bold red]")
            return

        table = Table(title="USER PROFILE", border_style="cyan")
        table.add_column("Field", style="cyan")
        table.add_column("Details", style="green")

        table.add_row("User ID", str(user_record[0]))
        table.add_row("Full Name", user_record[1].title())
        table.add_row("Email", user_record[2])
        table.add_row("Mobile", user_record[3])
        table.add_row("Username", user_record[4])

        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")


def update_profile(user_id):
    try:
        console.print(Panel.fit("[bold cyan]UPDATE PROFILE[/bold cyan]"))
        cursor.execute("SELECT full_name, email, mobile, username FROM users WHERE user_id = %s", (user_id,))
        current_data = cursor.fetchone()

        if not current_data:
            console.print("[bold red]❌ User Not Found.[/bold red]")
            return

        full_name, email, mobile, username = current_data

        console.print("[bold yellow]Leave blank and press Enter to keep current value.[/bold yellow]")

        new_name = console.input(f"[bold green]New Full Name ({full_name.title()}): [/bold green]").strip().lower()
        full_name = new_name if new_name else full_name

        while True:
            new_email = console.input(f"[bold green]New Email ({email}): [/bold green]").strip().lower()
            if new_email:
                confirm_email = console.input("[bold green]Re-enter New Email to confirm: [/bold green]").strip().lower()
                if new_email == confirm_email:
                    email = new_email
                    break
                else:
                    console.print("[bold red]❌ Emails do not match! Try again.[/bold red]")
            else:
                break

        new_mobile = console.input(f"[bold green]New Mobile ({mobile}): [/bold green]").strip()
        mobile = new_mobile if new_mobile else mobile

        new_username = console.input(f"[bold green]New Username ({username}): [/bold green]").strip().lower()
        username = new_username if new_username else username

        if get_yes_no("Are you sure you want to update your profile with these details?"):
            cursor.execute("UPDATE users SET full_name = %s, email = %s, mobile = %s, username = %s WHERE user_id = %s",
                           (full_name, email, mobile, username, user_id))
            conn.commit()
            console.print("[bold green]✅ Profile Updated Successfully![/bold green]")
        else:
            console.print("[bold cyan]Update cancelled.[/bold cyan]")

    except mysql.connector.IntegrityError:
        conn.rollback()
        console.print("[bold red]❌ Update Failed! Email, Mobile or Username already exists.[/bold red]")
    except Exception as e:
        conn.rollback()
        console.print(f"[bold red]Error: {e}[/bold red]")


def update_user_credentials(email):
    """Updates password only as requested."""
    while True:
        try:
            console.print(Panel.fit("[bold cyan]UPDATE PASSWORD[/bold cyan]"))

            newpass = get_password("Enter New Password :")
            confirm_pass = get_password("Re-Enter New Password :")

            if newpass == confirm_pass:
                if get_yes_no("Are you sure you want to update your password?"):
                    cursor.execute("UPDATE users SET password=%s WHERE email=%s", (newpass, email))
                    conn.commit()
                    console.print("[bold green]✅ Password updated successfully![/bold green]")
                    return True
                else:
                    console.print("[bold cyan]Update cancelled.[/bold cyan]")
                    return False
            else:
                console.print("[bold red]❌ Passwords do not match![/bold red]")
                if not get_yes_no("Want to try again?"):
                    return False
        except Exception as e:
            console.print(f"[bold red]❌ Error: {e}[/bold red]")
            return False