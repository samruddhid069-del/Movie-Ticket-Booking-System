from db import conn, cursor
from utils import get_string, get_yes_no
from services.payment_services import process_multiple_payments
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime, timedelta

console = Console()

def display_visual_seat_layout(show_id, theater_id):
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
        return False

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
    return True

def book_ticket(user_id):
    try:
        console.print(Panel.fit("[bold cyan]🎟️ BOOK TICKET[/bold cyan]"))
        
        location = get_string("Enter Location (e.g., Pune, Mumbai) :")
        movie_name = get_string("Enter Movie Name :")
        
        today = datetime.now().date()
        next_week = today + timedelta(days=7)

        # STRICTLY fetch only shows that have NOT yet started
        cursor.execute("""
            SELECT s.show_id, t.theater_id, t.theater_name, t.location, s.show_date, s.show_time
            FROM shows s 
            JOIN theaters t ON s.theater_id = t.theater_id
            JOIN movies m ON s.movie_id = m.movie_id
            WHERE t.location LIKE %s AND m.movie_name LIKE %s 
            AND (s.show_date > CURDATE() OR (s.show_date = CURDATE() AND s.show_time > CURTIME()))
            ORDER BY s.show_date, s.show_time
        """, ("%" + location + "%", "%" + movie_name + "%"))
        
        shows = cursor.fetchall()
        
        if not shows:
            console.print(f"[bold yellow]No upcoming shows available for '{movie_name}' in '{location}' at this time.[/bold yellow]")
            return

        table = Table(title=f"UPCOMING SHOWS FOR {movie_name.upper()} IN {location.upper()}", border_style="cyan")
        table.add_column("Show ID", style="cyan")
        table.add_column("Theater", style="green")
        table.add_column("Date", style="blue")
        table.add_column("Time", style="cyan")
        table.add_column("Status", style="yellow")

        available_shows = []
        for show in shows:
            show_date = show[4]
            if show_date > next_week:
                status = "Coming Soon"
            else:
                status = "Available"
                available_shows.append(show)
            table.add_row(str(show[0]), show[2], str(show[4]), str(show[5]), status)
        
        console.print(table)
        
        if not available_shows:
            console.print("[bold yellow]Tickets for these shows are not open for booking yet (Available 7 days prior).[/bold yellow]")
            return

        show_id_str = console.input("\n[bold green]Enter Show ID to book : [/bold green]").strip()
        if not show_id_str.isdigit():
            console.print("[bold red]Show ID must be a number.[/bold red]")
            return
        show_id = int(show_id_str)

        selected_show = next((show for show in available_shows if show[0] == show_id), None)
        if selected_show is None:
            console.print("[bold red]Invalid Show ID or Show is not currently open for booking.[/bold red]")
            return

        theater_id = selected_show[1]
        
        if not display_visual_seat_layout(show_id, theater_id):
            return

        seat_input = get_string("Enter Seat Numbers to book (comma-separated, e.g., A1,A2) :").upper()
        if not seat_input:
            console.print("[bold red]Please enter at least one Seat Number.[/bold red]")
            return

        seat_numbers = list(dict.fromkeys([seat.strip() for seat in seat_input.split(",")]))
        
        selected_seats = []
        total_amount = 0

        for seat_num in seat_numbers:
            cursor.execute("""
                SELECT s.seat_id, s.seat_price, s.is_blocked, b.booking_id
                FROM seats s
                LEFT JOIN bookings b ON s.seat_id = b.seat_id AND b.show_id = %s AND (b.status = 'Booked' OR b.status IS NULL)
                WHERE s.theater_id = %s AND s.seat_number = %s
            """, (show_id, theater_id, seat_num))
            
            seat_data = cursor.fetchone()
            if not seat_data:
                console.print(f"[bold red]Seat {seat_num} is invalid for this theater.[/bold red]")
                return
                
            seat_id, price, is_blocked, booking_id = seat_data
            
            if is_blocked:
                console.print(f"[bold red]Seat {seat_num} is currently blocked/damaged.[/bold red]")
                return
            if booking_id:
                console.print(f"[bold red]Seat {seat_num} is already booked.[/bold red]")
                return
                
            selected_seats.append((seat_id, float(price)))
            total_amount += float(price)

        console.print(f"\n[bold cyan]Number of Seats : {len(selected_seats)}[/bold cyan]")
        console.print(f"[bold cyan]Total Amount : ₹{total_amount:.2f}[/bold cyan]")

        if not get_yes_no("Confirm Booking & Proceed to Payment?"):
            console.print("\n[bold yellow]Booking Cancelled.[/bold yellow]\n")
            return

        booking_data = []
        try:
            for seat_id, price in selected_seats:
                cursor.execute("SELECT booking_id FROM bookings WHERE show_id = %s AND seat_id = %s AND (status = 'Booked' OR status IS NULL) FOR UPDATE", (show_id, seat_id))
                if cursor.fetchone():
                    raise Exception(f"Seat ID {seat_id} was just booked by another user.")

                cursor.execute("""
                    INSERT INTO bookings(user_id, show_id, seat_id, total_amount)
                    VALUES(%s, %s, %s, %s)
                """, (user_id, show_id, seat_id, price))
                booking_data.append((cursor.lastrowid, price))
            conn.commit()
            
            console.print("\n[bold yellow]Redirecting to Payment Gateway...[/bold yellow]")
            success = process_multiple_payments(booking_data, total_amount, user_id)
            
            if not success:
                # If payment fails/cancels, release the booked seats
                for b_id, _ in booking_data:
                    cursor.execute("DELETE FROM bookings WHERE booking_id = %s", (b_id,))
                conn.commit()
                console.print("[bold yellow]Tickets have been released due to payment failure or cancellation.[/bold yellow]")
            
        except Exception as e:
            conn.rollback()
            console.print(f"[bold red]Booking Error: {e}[/bold red]")

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

def view_booking(user_id):
    try:
        # Get Upcoming Bookings (Shows strictly in the future)
        cursor.execute("""
            SELECT b.booking_id, m.movie_name, t.theater_name, t.location, s.show_date, s.show_time, se.seat_number, se.seat_type, b.booking_date, b.total_amount
            FROM bookings b JOIN shows s ON b.show_id = s.show_id
            JOIN movies m ON s.movie_id = m.movie_id JOIN theaters t ON s.theater_id = t.theater_id
            JOIN seats se ON b.seat_id = se.seat_id 
            WHERE b.user_id = %s AND (b.status = 'Booked' OR b.status IS NULL) 
            AND (s.show_date > CURDATE() OR (s.show_date = CURDATE() AND s.show_time > CURTIME()))
            ORDER BY s.show_date, s.show_time ASC
        """, (user_id,))
        upcoming = cursor.fetchall()
        
        # Get Past/Completed Bookings
        cursor.execute("""
            SELECT b.booking_id, m.movie_name, t.theater_name, t.location, s.show_date, s.show_time, se.seat_number, se.seat_type, b.booking_date, b.total_amount
            FROM bookings b JOIN shows s ON b.show_id = s.show_id
            JOIN movies m ON s.movie_id = m.movie_id JOIN theaters t ON s.theater_id = t.theater_id
            JOIN seats se ON b.seat_id = se.seat_id 
            WHERE b.user_id = %s AND (b.status = 'Booked' OR b.status IS NULL) 
            AND (s.show_date < CURDATE() OR (s.show_date = CURDATE() AND s.show_time <= CURTIME()))
            ORDER BY s.show_date DESC, s.show_time DESC
        """, (user_id,))
        past = cursor.fetchall()
        
        def render_table(title, records, color):
            if not records:
                console.print(f"\n[bold yellow]No {title.lower()} found.[/bold yellow]")
                return
            table = Table(title=title, border_style=color)
            table.add_column("Booking ID", style="cyan")
            table.add_column("Movie", style="green")
            table.add_column("Theater", style="yellow")
            table.add_column("Date", style="blue")
            table.add_column("Time", style="cyan")
            table.add_column("Seat", style="green")
            table.add_column("Amount", style="magenta")
            
            for row in records:
                table.add_row(str(row[0]), row[1], row[2], str(row[4]), str(row[5]), row[6], f"₹{row[9]}")
            console.print(table)

        render_table("UPCOMING BOOKINGS", upcoming, "cyan")
        render_table("PAST / COMPLETED BOOKINGS", past, "bright_black")

    except Exception as e:
        console.print(f"[bold red]Error viewing bookings: {e}[/bold red]")