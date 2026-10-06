from datetime import datetime
from db import conn, cursor
from utils import get_string, get_yes_no
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def add_movie():
    try:
        console.print(Panel.fit("[bold cyan]ADD MOVIE[/bold cyan]"))
        
        while True:
            movie_name = get_string("Movie Name :")
            if movie_name: break
            console.print("[bold red]Movie name cannot be empty. Please enter a valid name.[/bold red]")

        while True:
            language = get_string("Language :")
            if language: break
            console.print("[bold red]Language cannot be empty. Please enter a valid language.[/bold red]")

        cursor.execute("SELECT * FROM movies WHERE movie_name=%s AND language=%s", (movie_name, language))
        if cursor.fetchone():
            console.print("[bold red]This movie with the same language already exists![/bold red]")
            return

        while True:
            genre = get_string("Genre :")
            if genre: break
            console.print("[bold red]Genre cannot be empty. Please enter a valid genre.[/bold red]")

        while True:
            try:
                hours = int(console.input("[bold green]Duration (hours) : [/bold green]").strip())
                minutes = int(console.input("[bold green]Duration (minutes) : [/bold green]").strip())
                duration = (hours * 60) + minutes
                if duration > 0: break
                console.print("[bold red]Duration must be greater than 0.[/bold red]")
            except ValueError:
                console.print("[bold red]Please enter valid numbers for hours and minutes.[/bold red]")

        while True:
            try:
                date_str = console.input("[bold green]Release Date (DD-MM-YYYY): [/bold green]").strip()
                release_date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                if release_date_obj.date() < datetime.now().date():
                    console.print("[bold red]Release date cannot be in the past. Please enter a present or future date.[/bold red]")
                    continue
                release_date = release_date_obj.strftime("%Y-%m-%d")
                break
            except ValueError:
                console.print("[bold red]Invalid date format. Please use DD-MM-YYYY.[/bold red]")

        query = "INSERT INTO movies (movie_name, genre, language, duration, release_date) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (movie_name, genre, language, duration, release_date))
        conn.commit()
        console.print("[bold green]Movie Added Successfully![/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

def view_movies():
    try:
        cursor.execute("SELECT * FROM movies")
        movies = cursor.fetchall()
        if not movies:
            console.print("[bold red]No Movies Found.[/bold red]")
            return False

        table = Table(title="MOVIE LIST", border_style="cyan")
        table.add_column("ID", justify="center", style="cyan")
        table.add_column("Movie Name", style="green")
        table.add_column("Genre", style="yellow")
        table.add_column("Language", style="magenta")
        table.add_column("Duration", style="blue")
        table.add_column("Release Date", style="white")

        for movie in movies:
            hours = movie[4] // 60
            minutes = movie[4] % 60
            duration_str = f"{hours}h {minutes}m"
            table.add_row(str(movie[0]), movie[1], movie[2], movie[3], duration_str, str(movie[5]))
        
        console.print(table)
        return True
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        return False

def search_movie():
    while True:
        try:
            console.print(Panel.fit("[bold cyan]SEARCH MOVIE[/bold cyan]"))
            console.print("[bold yellow]1.[/bold yellow] Search by Movie ID")
            console.print("[bold yellow]2.[/bold yellow] Search by Movie Name")
            console.print("[bold yellow]3.[/bold yellow] Search by Language")
            console.print("[bold yellow]4.[/bold yellow] Search by Genre")
            console.print("[bold yellow]5.[/bold yellow] Back")
            
            choice = console.input("\n[bold green]Enter Choice : [/bold green]").strip()

            if choice == "1":
                movie_id = console.input("[bold green]Enter Movie ID : [/bold green]").strip()
                cursor.execute("SELECT * FROM movies WHERE movie_id=%s", (movie_id,))
                movies = cursor.fetchall()
            elif choice == "2":
                movie_name = get_string("Enter Movie Name :")
                cursor.execute("SELECT * FROM movies WHERE movie_name LIKE %s", ("%" + movie_name + "%",))
                movies = cursor.fetchall()
            elif choice == "3":
                language = get_string("Enter Language :")
                cursor.execute("SELECT * FROM movies WHERE language=%s", (language,))
                movies = cursor.fetchall()
            elif choice == "4":
                genre = get_string("Enter Genre :")
                cursor.execute("SELECT * FROM movies WHERE genre=%s", (genre,))
                movies = cursor.fetchall()
            elif choice == "5":
                return
            else:
                console.print("[bold red]Invalid Choice![/bold red]")
                continue

            if movies:
                table = Table(title="SEARCH RESULTS", border_style="cyan")
                table.add_column("ID", justify="center", style="cyan")
                table.add_column("Movie Name", style="green")
                table.add_column("Genre", style="yellow")
                table.add_column("Language", style="magenta")
                table.add_column("Duration", style="blue")
                table.add_column("Release Date", style="white")

                for movie in movies:
                    hours = movie[4] // 60
                    minutes = movie[4] % 60
                    duration_str = f"{hours}h {minutes}m"
                    table.add_row(str(movie[0]), movie[1], movie[2], movie[3], duration_str, str(movie[5]))
                
                console.print(table)
            else:
                console.print("[bold red]Movie Not Found.[/bold red]")
        except Exception as e:
            console.print(f"[bold red]Error: {e}[/bold red]")

def update_movie():
    try:
        if not view_movies(): return
        
        movie_id = console.input("\n[bold green]Enter Movie ID to update : [/bold green]").strip()
        cursor.execute("SELECT * FROM movies WHERE movie_id=%s", (movie_id,))
        movie = cursor.fetchone()
        
        if not movie:
            console.print("[bold red]Movie Not Found.[/bold red]")
            return

        table = Table(title="SELECTED MOVIE", border_style="cyan")
        table.add_column("ID", style="cyan")
        table.add_column("Movie Name", style="green")
        table.add_column("Language", style="magenta")
        table.add_row(str(movie[0]), movie[1], movie[3])
        console.print(table)

        if not get_yes_no("Do you want to update this movie?"):
            console.print("[bold cyan]Taking you back...[/bold cyan]")
            return

        while True:
            movie_name = get_string("New Movie Name :")
            if movie_name: break
            console.print("[bold red]Movie name cannot be empty.[/bold red]")

        while True:
            language = get_string("New Language :")
            if language: break
            console.print("[bold red]Language cannot be empty.[/bold red]")

        cursor.execute("SELECT * FROM movies WHERE movie_name=%s AND language=%s AND movie_id!=%s", (movie_name, language, movie_id))
        if cursor.fetchone():
            console.print("[bold red]Another movie with the same name and language already exists![/bold red]")
            return

        while True:
            genre = get_string("New Genre :")
            if genre: break
            console.print("[bold red]Genre cannot be empty.[/bold red]")

        while True:
            try:
                hours = int(console.input("[bold green]New Duration (hours) : [/bold green]").strip())
                minutes = int(console.input("[bold green]New Duration (minutes) : [/bold green]").strip())
                duration = (hours * 60) + minutes
                if duration > 0: break
                console.print("[bold red]Duration must be greater than 0.[/bold red]")
            except ValueError:
                console.print("[bold red]Please enter valid numbers.[/bold red]")

        while True:
            try:
                date_str = console.input("[bold green]New Release Date (DD-MM-YYYY): [/bold green]").strip()
                release_date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                if release_date_obj.date() < datetime.now().date():
                    console.print("[bold red]Release date cannot be in the past.[/bold red]")
                    continue
                release_date = release_date_obj.strftime("%Y-%m-%d")
                break
            except ValueError:
                console.print("[bold red]Invalid date format. Please use DD-MM-YYYY.[/bold red]")

        if get_yes_no("Confirm update with these details?"):
            cursor.execute("UPDATE movies SET movie_name=%s, genre=%s, language=%s, duration=%s, release_date=%s WHERE movie_id=%s", (movie_name, genre, language, duration, release_date, movie_id))
            conn.commit()
            console.print("[bold green]Movie Updated Successfully![/bold green]")
        else:
            console.print("[bold cyan]Update cancelled.[/bold cyan]")

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

def delete_movie():
    try:
        if not view_movies(): return
        
        movie_id = console.input("\n[bold green]Enter Movie ID to delete : [/bold green]").strip()
        cursor.execute("SELECT * FROM movies WHERE movie_id=%s", (movie_id,))
        movie = cursor.fetchone()
        
        if not movie:
            console.print("[bold red]Movie Not Found.[/bold red]")
            return

        table = Table(title="SELECTED MOVIE TO DELETE", border_style="red")
        table.add_column("ID", style="cyan")
        table.add_column("Movie Name", style="green")
        table.add_row(str(movie[0]), movie[1])
        console.print(table)

        if get_yes_no("Are you sure you want to delete this movie?"):
            cursor.execute("DELETE FROM movies WHERE movie_id=%s", (movie_id,))
            conn.commit()
            console.print("[bold green]Movie Deleted Successfully![/bold green]")
        else:
            console.print("[bold cyan]Deletion cancelled. Taking you back...[/bold cyan]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")