from db import conn, cursor
from utils import get_string, get_yes_no
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def add_theater():
    try:
        console.print(Panel.fit("[bold cyan]ADD THEATER[/bold cyan]"))
        
        while True:
            theater_name = get_string("Enter Theater Name :")
            if theater_name: break
            console.print("[bold red]Theater name cannot be empty.[/bold red]")

        while True:
            location = get_string("Enter Location :")
            if location: break
            console.print("[bold red]Location cannot be empty.[/bold red]")

        cursor.execute("SELECT * FROM theaters WHERE theater_name=%s AND location=%s", (theater_name, location))
        if cursor.fetchone():
            console.print("[bold red]This Theater with the same location already exists![/bold red]")
            return

        cursor.execute("INSERT INTO theaters(theater_name, location) VALUES(%s, %s)", (theater_name, location))
        conn.commit()
        theater_id = cursor.lastrowid
        console.print("\n[bold green]Theater Added Successfully![/bold green]")
        
        console.print("\n[bold cyan]Now, let's configure the seats for this theater.[/bold cyan]")
        
        from services.seat_services import generate_seats_for_theater 
        generate_seats_for_theater(theater_id)

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

def view_theaters():
    try:
        cursor.execute("SELECT * FROM theaters")
        theaters = cursor.fetchall()
        if not theaters:
            console.print("\n[bold red]No Theater Found.[/bold red]\n")
            return False
            
        table = Table(title="THEATER DETAILS", border_style="cyan")
        table.add_column("Theater ID", style="cyan", justify="center")
        table.add_column("Theater Name", style="green")
        table.add_column("Location", style="magenta")
        
        for theater in theaters: 
            table.add_row(str(theater[0]), theater[1], theater[2])
        console.print(table)
        return True
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        return False

def search_theater():
    while True:
        try:
            console.print(Panel.fit("[bold cyan]SEARCH THEATER[/bold cyan]"))
            console.print("[bold yellow]1.[/bold yellow] Search by Theater Name")
            console.print("[bold yellow]2.[/bold yellow] Search by Location")
            console.print("[bold yellow]3.[/bold yellow] Back")
            
            choice = console.input("\n[bold green]Enter your choice : [/bold green]").strip()

            if choice == "1":
                theater_name = get_string("Enter Theater Name :")
                cursor.execute("SELECT * FROM theaters WHERE theater_name LIKE %s", ("%" + theater_name + "%",))
            elif choice == "2":
                location = get_string("Enter Location :")
                cursor.execute("SELECT * FROM theaters WHERE location LIKE %s", ("%" + location + "%",))
            elif choice == "3":
                return
            else:
                console.print("[bold red]Invalid choice! Please enter 1, 2, or 3.[/bold red]")
                continue

            theaters = cursor.fetchall()
            if theaters:
                table = Table(title="SEARCH RESULTS", border_style="cyan")
                table.add_column("Theater ID", style="cyan")
                table.add_column("Theater Name", style="green")
                table.add_column("Location", style="magenta")
                for theater in theaters: 
                    table.add_row(str(theater[0]), theater[1], theater[2])
                console.print(table)
                break
            else:
                console.print("\n[bold red]Theater Not Found![/bold red]\n")
                break
        except Exception as e:
            console.print(f"[bold red]Error: {e}[/bold red]")
            break

def update_theater():
    try:
        if not view_theaters(): return
        
        theater_id_str = console.input("\n[bold green]Enter Theater ID to Update : [/bold green]").strip()
        if not theater_id_str.isdigit():
            console.print("[bold red]Invalid Theater ID.[/bold red]")
            return
        theater_id = int(theater_id_str)
        
        cursor.execute("SELECT * FROM theaters WHERE theater_id=%s", (theater_id,))
        theater = cursor.fetchone()
        if not theater:
            console.print("\n[bold red]Theater Not Found![/bold red]\n")
            return

        table = Table(title="SELECTED THEATER", border_style="cyan")
        table.add_column("ID", style="cyan")
        table.add_column("Theater Name", style="green")
        table.add_column("Location", style="magenta")
        table.add_row(str(theater[0]), theater[1], theater[2])
        console.print(table)

        if not get_yes_no("Do you want to update this theater?"):
            console.print("[bold cyan]Taking you back...[/bold cyan]")
            return

        while True:
            new_name = get_string("Enter New Theater Name :")
            if new_name: break
            console.print("[bold red]Theater name cannot be empty.[/bold red]")

        while True:
            new_location = get_string("Enter New Location :")
            if new_location: break
            console.print("[bold red]Location cannot be empty.[/bold red]")

        cursor.execute("SELECT * FROM theaters WHERE theater_name=%s AND location=%s AND theater_id!=%s", (new_name, new_location, theater_id))
        if cursor.fetchone():
            console.print("[bold red]Another theater with this name and location already exists![/bold red]")
            return

        if get_yes_no("Confirm update with these details?"):
            cursor.execute("UPDATE theaters SET theater_name=%s, location=%s WHERE theater_id=%s", (new_name, new_location, theater_id))
            conn.commit()
            console.print("\n[bold green]Theater Updated Successfully![/bold green]\n")
        else:
            console.print("[bold cyan]Update cancelled.[/bold cyan]")

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

def delete_theater():
    try:
        if not view_theaters(): return
        
        theater_id_str = console.input("\n[bold green]Enter Theater ID to Delete : [/bold green]").strip()
        if not theater_id_str.isdigit():
            console.print("[bold red]Invalid Theater ID.[/bold red]")
            return
        theater_id = int(theater_id_str)
        
        cursor.execute("SELECT * FROM theaters WHERE theater_id=%s", (theater_id,))
        theater = cursor.fetchone()
        
        if not theater:
            console.print("\n[bold red]Theater Not Found![/bold red]\n")
            return

        table = Table(title="SELECTED THEATER", border_style="red")
        table.add_column("ID", style="cyan")
        table.add_column("Theater Name", style="green")
        table.add_column("Location", style="magenta")
        table.add_row(str(theater[0]), theater[1], theater[2])
        console.print(table)

        if get_yes_no("Are you sure you want to delete this theater?"):
            # Check for CURRENT or UPCOMING shows
            cursor.execute("""
                SELECT s.show_id, m.movie_name, s.show_date, s.show_time 
                FROM shows s 
                JOIN movies m ON s.movie_id = m.movie_id 
                WHERE s.theater_id=%s 
                AND (s.show_date > CURDATE() OR (s.show_date = CURDATE() AND s.show_time > CURTIME()))
            """, (theater_id,))
            upcoming_shows = cursor.fetchall()
            
            if upcoming_shows:
                console.print("\n[bold red]Cannot delete theater: It has current or upcoming scheduled shows.[/bold red]\n")
                table_shows = Table(title="UPCOMING SHOWS", border_style="red")
                table_shows.add_column("Show ID", style="cyan")
                table_shows.add_column("Movie", style="green")
                table_shows.add_column("Date", style="blue")
                table_shows.add_column("Time", style="yellow")
                for s in upcoming_shows:
                    table_shows.add_row(str(s[0]), s[1], str(s[2]), str(s[3]))
                console.print(table_shows)
            else:
                try:
                    # Cascade delete past data to clear foreign key constraints safely
                    cursor.execute("DELETE p FROM payments p JOIN bookings b ON p.booking_id = b.booking_id JOIN shows s ON b.show_id = s.show_id WHERE s.theater_id = %s", (theater_id,))
                    cursor.execute("DELETE b FROM bookings b JOIN shows s ON b.show_id = s.show_id WHERE s.theater_id = %s", (theater_id,))
                    cursor.execute("DELETE FROM shows WHERE theater_id=%s", (theater_id,))
                    cursor.execute("DELETE FROM seats WHERE theater_id=%s", (theater_id,))
                    cursor.execute("DELETE FROM theaters WHERE theater_id=%s", (theater_id,))
                    conn.commit()
                    console.print("\n[bold green]Theater and its past historical records Deleted Successfully![/bold green]\n")
                except Exception as e:
                    conn.rollback()
                    console.print(f"\n[bold red]Error deleting theater records: {e}[/bold red]\n")
        else:
            console.print("[bold cyan]Deletion cancelled. Taking you back...[/bold cyan]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")