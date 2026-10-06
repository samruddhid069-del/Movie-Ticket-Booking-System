import mysql.connector
from db import conn, cursor
from utils import get_string, get_yes_no
from services.theater_services import view_theaters
from services.show_services import show_all_shows_table
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def generate_seats_for_theater(theater_id):
    try:
        total_rows = int(console.input("[bold green]Enter Total Number of Rows (e.g., 10): [/bold green]").strip())
        cols = int(console.input("[bold green]Enter Seats per Row (e.g., 12): [/bold green]").strip())

        console.print("\n[bold cyan]--- Seat Categorization ---[/bold cyan]")
        prem_rows = int(console.input("[bold green]Number of Premium Rows : [/bold green]").strip())
        gold_rows = int(console.input("[bold green]Number of Gold Rows : [/bold green]").strip())
        silv_rows = int(console.input("[bold green]Number of Silver Rows : [/bold green]").strip())

        if prem_rows + gold_rows + silv_rows != total_rows:
            console.print("[bold red]Error: Row counts do not equal total rows![/bold red]")
            return

        prem_price = float(console.input("[bold green]Price for Premium Seats : ₹[/bold green]").strip())
        gold_price = float(console.input("[bold green]Price for Gold Seats : ₹[/bold green]").strip())
        silv_price = float(console.input("[bold green]Price for Silver Seats : ₹[/bold green]").strip())

        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        seat_data = []

        for r in range(total_rows):
            row_letter = alphabet[r % 26] * (r // 26 + 1)
            
            if r < prem_rows:
                stype, sprice = "Premium", prem_price
            elif r < prem_rows + gold_rows:
                stype, sprice = "Gold", gold_price
            else:
                stype, sprice = "Silver", silv_price

            for c in range(1, cols + 1):
                seat_num = f"{row_letter}{c}"
                seat_data.append((theater_id, seat_num, stype, sprice))

        cursor.executemany("""
            INSERT IGNORE INTO seats (theater_id, seat_number, seat_type, seat_price)
            VALUES (%s, %s, %s, %s)
        """, seat_data)
        conn.commit()
        console.print(f"\n[bold green]✅ {len(seat_data)} Seats Generated Successfully![/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error generating seats: {e}[/bold red]")

def add_seat():
    try:
        console.print(Panel.fit("[bold cyan]ADD SEATS (MODIFY / SCRATCH)[/bold cyan]"))
        if not view_theaters(): return
        
        theater_id_str = console.input("\n[bold green]Enter Theater ID: [/bold green]").strip()
        if not theater_id_str.isdigit(): return
        theater_id = int(theater_id_str)

        cursor.execute("SELECT theater_name, location FROM theaters WHERE theater_id = %s", (theater_id,))
        theater = cursor.fetchone()
        if not theater:
            console.print("[bold red]Theater not found![/bold red]")
            return

        console.print(f"\n[bold yellow]Selected Theater: {theater[0]} | Location: {theater[1]}[/bold yellow]")
        if not get_yes_no("Are you sure you want to add/modify seats in this theater?"):
            return

        console.print("\n[bold cyan]1. Add from Scratch (Deletes existing unbooked seats)[/bold cyan]")
        console.print("[bold cyan]2. Back[/bold cyan]")
        choice = console.input("[bold green]Enter choice: [/bold green]").strip()

        if choice == "1":
            cursor.execute("""
                DELETE FROM seats WHERE theater_id = %s 
                AND seat_id NOT IN (SELECT seat_id FROM bookings)
            """, (theater_id,))
            conn.commit()
            console.print("[bold yellow]Previous unbooked seats cleared. Generating new layout...[/bold yellow]")
            generate_seats_for_theater(theater_id)
        else:
            return

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

def view_seats():
    try:
        console.print(Panel.fit("[bold cyan]VIEW SEAT LAYOUT AND AVAILABILITY[/bold cyan]"))
        if not show_all_shows_table(): return
        
        show_id_str = console.input("\n[bold green]Enter Show ID : [/bold green]").strip()
        if not show_id_str.isdigit(): return
        show_id = int(show_id_str)

        cursor.execute("""
            SELECT t.theater_id, t.theater_name, t.location, m.movie_name 
            FROM shows s JOIN theaters t ON s.theater_id = t.theater_id 
            JOIN movies m ON s.movie_id = m.movie_id WHERE s.show_id = %s
        """, (show_id,))
        show_data = cursor.fetchone()
        if not show_data:
            console.print("[bold red]Show not found![/bold red]")
            return

        theater_id, theater_name, location, movie_name = show_data
        console.print(f"\n[bold yellow]Movie: {movie_name} | Theater: {theater_name} ({location})[/bold yellow]")
        
        cursor.execute("""
            SELECT s.seat_id, s.seat_number, s.seat_type, s.seat_price, s.is_blocked,
                   CASE WHEN b.seat_id IS NULL THEN 'Available' ELSE 'Booked' END AS status
            FROM seats s
            LEFT JOIN bookings b ON s.seat_id = b.seat_id AND b.show_id = %s AND (b.status = 'Booked' OR b.status IS NULL)
            WHERE s.theater_id = %s ORDER BY s.seat_id
        """, (show_id, theater_id))
        
        seats = cursor.fetchall()
        if not seats:
            console.print("\n[bold red]No seats found for this theater.[/bold red]")
            return

        console.print("\n[bold white]" + "SCREEN".center(60) + "[/bold white]")
        console.print("[dim]" + "-"*60 + "[/dim]")
        
        for i in range(0, len(seats), 10):
            row = seats[i:i + 10]
            for seat in row:
                stype = seat[2].lower()
                is_blocked = seat[4]
                status = seat[5]

                if is_blocked:
                    console.print(f"[white on bright_black] {seat[1]:^4} [/white on bright_black]", end=" ")
                elif status == "Booked":
                    console.print(f"[white on red] {seat[1]:^4} [/white on red]", end=" ")
                else:
                    if stype == "premium":
                        console.print(f"[white on magenta] {seat[1]:^4} [/white on magenta]", end=" ")
                    elif stype == "gold":
                        console.print(f"[black on yellow] {seat[1]:^4} [/black on yellow]", end=" ")
                    else:
                        console.print(f"[black on white] {seat[1]:^4} [/black on white]", end=" ")
            console.print()

        console.print("\n[magenta]■ Premium[/magenta]   [yellow]■ Gold[/yellow]   [white]■ Silver[/white]   [red]■ Booked[/red]   [bright_black]■ Blocked[/bright_black]\n")

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

def changes_in_seat():
    while True:
        console.print(Panel.fit("[bold cyan]CHANGES IN SEAT[/bold cyan]"))
        console.print("[bold yellow]1.[/bold yellow] Update Row Seat Type & Price")
        console.print("[bold yellow]2.[/bold yellow] Block a Seat")
        console.print("[bold yellow]3.[/bold yellow] Unblock a Seat")
        console.print("[bold yellow]4.[/bold yellow] Back")
        
        choice = console.input("\n[bold green]Enter choice: [/bold green]").strip()
        
        if choice == "1":
            if not view_theaters(): continue
            theater_id_str = console.input("[bold green]Enter Theater ID: [/bold green]").strip()
            if not theater_id_str.isdigit():
                console.print("[bold red]Invalid Theater ID! Must be a number.[/bold red]")
                continue
            theater_id = int(theater_id_str)
            
            row_letter = get_string("Enter Row Letter (e.g., A, B):").upper()
            if not row_letter.isalpha():
                console.print("[bold red]Invalid Row Letter! Must be alphabetic.[/bold red]")
                continue
                
            new_type = get_string("Enter New Seat Type (Premium/Gold/Silver):").title()
            
            try:
                new_price = float(console.input("[bold green]Enter New Price: ₹[/bold green]").strip())
            except ValueError:
                console.print("[bold red]Invalid Price! Must be a number.[/bold red]")
                continue
            
            if get_yes_no(f"Update all seats in Row {row_letter} to {new_type} (₹{new_price})?"):
                cursor.execute("""
                    UPDATE seats SET seat_type = %s, seat_price = %s 
                    WHERE theater_id = %s AND seat_number LIKE %s
                """, (new_type, new_price, theater_id, f"{row_letter}%"))
                conn.commit()
                console.print(f"[bold green]Row {row_letter} updated successfully![/bold green]")
                
        elif choice == "2" or choice == "3":
            if not view_theaters(): continue
            theater_id_str = console.input("[bold green]Enter Theater ID: [/bold green]").strip()
            if not theater_id_str.isdigit():
                console.print("[bold red]Invalid Theater ID! Must be a number.[/bold red]")
                continue
            theater_id = int(theater_id_str)
            
            seat_num = get_string("Enter Seat Number (e.g., A1):").upper()
            
            is_blocked = True if choice == "2" else False
            action = "Block" if choice == "2" else "Unblock"
            
            cursor.execute("SELECT seat_id FROM seats WHERE theater_id = %s AND seat_number = %s", (theater_id, seat_num))
            if not cursor.fetchone():
                console.print("[bold red]Seat not found![/bold red]")
                continue
                
            if get_yes_no(f"Are you sure you want to {action} seat {seat_num}?"):
                cursor.execute("UPDATE seats SET is_blocked = %s WHERE theater_id = %s AND seat_number = %s", (is_blocked, theater_id, seat_num))
                conn.commit()
                console.print(f"[bold green]Seat {seat_num} {action}ed successfully![/bold green]")
        
        elif choice == "4":
            break
        else:
            console.print("[bold red]Invalid choice.[/bold red]")

def delete_seat():
    try:
        console.print(Panel.fit("[bold cyan]DELETE SEAT[/bold cyan]"))
        if not view_theaters(): return
        theater_id = console.input("[bold green]Enter Theater ID: [/bold green]").strip()
        
        cursor.execute("SELECT seat_id, seat_number, seat_type, seat_price FROM seats WHERE theater_id = %s", (theater_id,))
        seats = cursor.fetchall()
        if not seats:
            console.print("[bold red]No seats found for this theater.[/bold red]")
            return
            
        table = Table(title="SEATS", border_style="cyan")
        table.add_column("Seat ID"); table.add_column("Seat No."); table.add_column("Type"); table.add_column("Price")
        for s in seats: table.add_row(str(s[0]), s[1], s[2], str(s[3]))
        console.print(table)
        
        seat_id = console.input("\n[bold green]Enter Seat ID to delete: [/bold green]").strip()
        cursor.execute("SELECT * FROM seats WHERE seat_id = %s", (seat_id,))
        seat_row = cursor.fetchone()
        
        if not seat_row:
            console.print("[bold red]Seat ID not found.[/bold red]")
            return
            
        cursor.execute("SELECT * FROM bookings WHERE seat_id = %s", (seat_id,))
        if cursor.fetchone():
            console.print("[bold red]You cannot delete this seat as it is already booked.[/bold red]")
            return

        table_del = Table(title="SEAT TO DELETE", border_style="red")
        table_del.add_column("Seat ID"); table_del.add_column("Seat No."); table_del.add_column("Type")
        table_del.add_row(str(seat_row[0]), seat_row[2], seat_row[3])
        console.print(table_del)

        if get_yes_no("Are you sure you want to delete this seat?"):
            cursor.execute("DELETE FROM seats WHERE seat_id = %s", (seat_id,))
            conn.commit()
            console.print("[bold green]Seat Deleted Successfully![/bold green]")
        else:
            console.print("[bold cyan]Deletion cancelled.[/bold cyan]")

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")