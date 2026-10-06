from datetime import datetime, timedelta
from db import conn, cursor
from utils import get_string, get_yes_no
from services.movie_services import view_movies
from services.theater_services import view_theaters
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def show_all_shows_table():
    cursor.execute("""
        SELECT s.show_id, m.movie_name, t.theater_name, t.location, s.show_date, s.show_time
        FROM shows s
        JOIN movies m ON s.movie_id = m.movie_id
        JOIN theaters t ON s.theater_id = t.theater_id
        ORDER BY s.show_date, s.show_time
    """)
    records = cursor.fetchall()
    if not records:
        console.print("[bold red]No shows found.[/bold red]")
        return False

    table = Table(title="SHOWS", border_style="cyan")
    table.add_column("Show ID", justify="center")
    table.add_column("Movie")
    table.add_column("Theater")
    table.add_column("Location")
    table.add_column("Date")
    table.add_column("Time")

    for row in records:
        table.add_row(str(row[0]), str(row[1]), str(row[2]), str(row[3]).title(), str(row[4]), str(row[5]))
    console.print(table)
    return True

def add_show():
    try:
        console.print(Panel.fit("[bold cyan]ADD SHOW[/bold cyan]"))
        
        console.print("[bold cyan]Existing Shows:[/bold cyan]")
        show_all_shows_table()
        
        console.print("\n[bold cyan]Available Movies:[/bold cyan]")
        if not view_movies(): return
        movie_id_str = console.input("\n[bold green]Movie ID : [/bold green]").strip()
        if not movie_id_str.isdigit():
            console.print("[bold red]Invalid Input! Movie ID must be a number.[/bold red]")
            return
        movie_id = int(movie_id_str)
        
        cursor.execute("SELECT movie_name, duration, release_date FROM movies WHERE movie_id = %s", (movie_id,))
        movie = cursor.fetchone()
        if not movie:
            console.print("[bold red]Movie ID not found.[/bold red]")
            return

        movie_name, duration, release_date = movie[0], movie[1], movie[2]

        console.print("\n[bold cyan]Available Theaters:[/bold cyan]")
        if not view_theaters(): return
        theater_id_str = console.input("\n[bold green]Theater ID : [/bold green]").strip()
        if not theater_id_str.isdigit():
            console.print("[bold red]Invalid Input! Theater ID must be a number.[/bold red]")
            return
        theater_id = int(theater_id_str)

        cursor.execute("SELECT theater_name FROM theaters WHERE theater_id = %s", (theater_id,))
        if not cursor.fetchone():
            console.print("[bold red]Theater ID not found.[/bold red]")
            return

        while True:
            show_date = console.input("[bold green]Show Date (YYYY-MM-DD) : [/bold green]").strip()
            try:
                date_obj = datetime.strptime(show_date, "%Y-%m-%d").date()
                if date_obj < release_date:
                    console.print(f"[bold red]Show date cannot be before the movie's release date ({release_date}).[/bold red]")
                    continue
                if date_obj < datetime.now().date():
                    console.print("[bold red]Show date cannot be in the past.[/bold red]")
                    continue
                break
            except ValueError:
                console.print("[bold red]Invalid date format. Please use YYYY-MM-DD.[/bold red]")
        
        while True:
            show_time = console.input("[bold green]Show Time (HH:MM:SS) : [/bold green]").strip()
            try:
                datetime.strptime(show_time, "%H:%M:%S")
                break
            except ValueError:
                console.print("[bold red]Invalid time format. Please use HH:MM:SS.[/bold red]")

        new_start = datetime.strptime(show_date + " " + show_time, "%Y-%m-%d %H:%M:%S")
        new_end = new_start + timedelta(minutes=duration)

        cursor.execute("""
            SELECT s.show_id, s.show_time, m.movie_name, m.duration
            FROM shows s JOIN movies m ON s.movie_id = m.movie_id
            WHERE s.theater_id = %s AND s.show_date = %s
        """, (theater_id, show_date))

        existing_shows = cursor.fetchall()
        for show in existing_shows:
            existing_time = str(show[1]).split(".")[0]
            existing_start = datetime.strptime(show_date + " " + existing_time, "%Y-%m-%d %H:%M:%S")
            existing_end = existing_start + timedelta(minutes=show[3])
            
            if (new_start < existing_end and new_end > existing_start):
                console.print(Panel(f"[bold red]SHOW TIMING CONFLICT![/bold red]\n\n[yellow]Existing Show ID : {show[0]}\nExisting Movie : {show[2]}[/yellow]", border_style="red"))
                return

        cursor.execute("INSERT INTO shows (movie_id, theater_id, show_date, show_time) VALUES (%s, %s, %s, %s)", (movie_id, theater_id, show_date, show_time))
        conn.commit()
        console.print("[bold green]Show added successfully.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

def view_shows():
    while True:
        console.print(Panel.fit("[bold cyan]VIEW SHOWS[/bold cyan]"))
        console.print("[bold yellow]1.[/bold yellow] All Shows")
        console.print("[bold yellow]2.[/bold yellow] Shows by Date")
        console.print("[bold yellow]3.[/bold yellow] Shows by Theater")
        console.print("[bold yellow]4.[/bold yellow] Back")
        
        choice = console.input("\n[bold green]Enter Choice: [/bold green]").strip()
        
        if choice == "1":
            show_all_shows_table()
        elif choice == "2":
            date_str = console.input("[bold green]Enter Date (YYYY-MM-DD): [/bold green]").strip()
            cursor.execute("""
                SELECT s.show_id, m.movie_name, t.theater_name, s.show_date, s.show_time
                FROM shows s JOIN movies m ON s.movie_id = m.movie_id JOIN theaters t ON s.theater_id = t.theater_id
                WHERE s.show_date = %s ORDER BY s.show_time
            """, (date_str,))
            records = cursor.fetchall()
            if records:
                table = Table(title=f"SHOWS ON {date_str}", border_style="cyan")
                table.add_column("ID", justify="center")
                table.add_column("Movie")
                table.add_column("Theater")
                table.add_column("Time")
                for row in records: table.add_row(str(row[0]), str(row[1]), str(row[2]), str(row[4]))
                console.print(table)
            else:
                console.print("[bold red]No shows found for this date.[/bold red]")
        elif choice == "3":
            if not view_theaters(): continue
            theater_id_str = console.input("[bold green]Enter Theater ID: [/bold green]").strip()
            if not theater_id_str.isdigit():
                console.print("[bold red]Invalid Theater ID.[/bold red]")
                continue
            cursor.execute("""
                SELECT s.show_id, m.movie_name, s.show_date, s.show_time
                FROM shows s JOIN movies m ON s.movie_id = m.movie_id
                WHERE s.theater_id = %s ORDER BY s.show_date, s.show_time
            """, (int(theater_id_str),))
            records = cursor.fetchall()
            if records:
                table = Table(title="SHOWS IN THEATER", border_style="cyan")
                table.add_column("ID", justify="center")
                table.add_column("Movie")
                table.add_column("Date")
                table.add_column("Time")
                for row in records: table.add_row(str(row[0]), str(row[1]), str(row[2]), str(row[3]))
                console.print(table)
            else:
                console.print("[bold red]No shows found for this theater.[/bold red]")
        elif choice == "4":
            break
        else:
            console.print("[bold red]Invalid choice.[/bold red]")

def search_show():
    while True:
        console.print(Panel.fit("[bold cyan]SEARCH SHOW[/bold cyan]"))
        console.print("[bold yellow]1.[/bold yellow] Search by Show ID")
        console.print("[bold yellow]2.[/bold yellow] Search by Movie Name and Theater Name")
        console.print("[bold yellow]3.[/bold yellow] Back")
        choice = console.input("\n[bold green]Enter Choice: [/bold green]").strip()
        
        if choice == "1":
            show_id = console.input("[bold green]Enter Show ID : [/bold green]").strip()
            cursor.execute("""
                SELECT s.show_id, m.movie_name, t.theater_name, s.show_date, s.show_time
                FROM shows s JOIN movies m ON s.movie_id = m.movie_id JOIN theaters t ON s.theater_id = t.theater_id 
                WHERE s.show_id = %s
            """, (show_id,))
            records = cursor.fetchall()
        elif choice == "2":
            movie_name = get_string("Enter Movie Name :")
            theater_name = get_string("Enter Theater Name :")
            cursor.execute("""
                SELECT s.show_id, m.movie_name, t.theater_name, s.show_date, s.show_time
                FROM shows s JOIN movies m ON s.movie_id = m.movie_id JOIN theaters t ON s.theater_id = t.theater_id 
                WHERE m.movie_name LIKE %s AND t.theater_name LIKE %s
            """, ("%" + movie_name + "%", "%" + theater_name + "%"))
            records = cursor.fetchall()
        elif choice == "3":
            break
        else:
            console.print("[bold red]Invalid choice.[/bold red]")
            continue
            
        if records:
            table = Table(title="SEARCH RESULTS", border_style="cyan")
            table.add_column("ID", justify="center")
            table.add_column("Movie")
            table.add_column("Theater")
            table.add_column("Date")
            table.add_column("Time")
            for row in records: table.add_row(str(row[0]), str(row[1]), str(row[2]), str(row[3]), str(row[4]))
            console.print(table)
        else:
            console.print("[bold red]Show not found.[/bold red]")

def update_show():
    try:
        if not show_all_shows_table(): return
        
        show_id_str = console.input("\n[bold green]Enter Show ID to Update: [/bold green]").strip()
        if not show_id_str.isdigit(): return
        show_id = int(show_id_str)
        
        cursor.execute("""
            SELECT s.show_id, m.movie_name, t.theater_name, s.show_date, s.show_time
            FROM shows s JOIN movies m ON s.movie_id = m.movie_id JOIN theaters t ON s.theater_id = t.theater_id 
            WHERE s.show_id = %s
        """, (show_id,))
        row = cursor.fetchone()
        
        if not row:
            console.print("[bold red]Show not found.[/bold red]")
            return

        table = Table(title="SELECTED SHOW", border_style="cyan")
        table.add_column("ID"); table.add_column("Movie"); table.add_column("Theater"); table.add_column("Date"); table.add_column("Time")
        table.add_row(str(row[0]), str(row[1]), str(row[2]), str(row[3]), str(row[4]))
        console.print(table)
        
        if not get_yes_no("Do you want to update this show?"): return

        console.print("\n[bold cyan]Available Movies:[/bold cyan]")
        view_movies()
        movie_id_str = console.input("\n[bold green]New Movie ID : [/bold green]").strip()
        if not movie_id_str.isdigit():
            console.print("[bold red]Invalid Input! Movie ID must be a number.[/bold red]")
            return
        movie_id = int(movie_id_str)

        console.print("\n[bold cyan]Available Theaters:[/bold cyan]")
        view_theaters()
        theater_id_str = console.input("\n[bold green]New Theater ID : [/bold green]").strip()
        if not theater_id_str.isdigit():
            console.print("[bold red]Invalid Input! Theater ID must be a number.[/bold red]")
            return
        theater_id = int(theater_id_str)
        
        while True:
            show_date = console.input("[bold green]New Date (YYYY-MM-DD) : [/bold green]").strip()
            try:
                date_obj = datetime.strptime(show_date, "%Y-%m-%d").date()
                if date_obj < datetime.now().date():
                    console.print("[bold red]Show date cannot be in the past.[/bold red]")
                    continue
                break
            except ValueError:
                console.print("[bold red]Invalid date format.[/bold red]")

        while True:
            show_time = console.input("[bold green]New Time (HH:MM:SS) : [/bold green]").strip()
            try:
                datetime.strptime(show_time, "%H:%M:%S")
                break
            except ValueError:
                console.print("[bold red]Invalid time format.[/bold red]")

        if get_yes_no("Confirm update?"):
            cursor.execute("UPDATE shows SET movie_id = %s, theater_id = %s, show_date = %s, show_time = %s WHERE show_id = %s", 
                           (movie_id, theater_id, show_date, show_time, show_id))
            conn.commit()
            console.print("[bold green]Show updated successfully.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

def delete_show():
    try:
        if not show_all_shows_table(): return
        show_id_str = console.input("\n[bold green]Enter Show ID to delete : [/bold green]").strip()
        if not show_id_str.isdigit():
            console.print("[bold red]Invalid Show ID.[/bold red]")
            return
        show_id = int(show_id_str)
        
        cursor.execute("SELECT * FROM shows WHERE show_id=%s", (show_id,))
        if not cursor.fetchone():
            console.print("[bold red]Show ID not found.[/bold red]")
            return
            
        if get_yes_no("Are you sure you want to delete this show?"):
            try:
                cursor.execute("DELETE FROM shows WHERE show_id = %s", (show_id,))
                conn.commit()
                console.print("[bold green]Show deleted successfully.[/bold green]")
            except Exception as fk_err:
                console.print("[bold red]Cannot delete show: It has associated bookings. Cancel tickets first.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")