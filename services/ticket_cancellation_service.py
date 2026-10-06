from db import conn, cursor
from utils import get_string, get_yes_no
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime, timedelta

console = Console()

def get_filtered_tickets(status, user_id=None, active_only=False):
    base_query = f"""
        SELECT b.booking_id, b.user_id, m.movie_name, t.theater_name, t.location, 
               s.show_date, s.show_time, se.seat_number, b.total_amount
        FROM bookings b
        JOIN shows s ON b.show_id = s.show_id
        JOIN movies m ON s.movie_id = m.movie_id
        JOIN theaters t ON s.theater_id = t.theater_id
        JOIN seats se ON b.seat_id = se.seat_id
        WHERE (b.status = '{status}' OR ('{status}' = 'Booked' AND b.status IS NULL))
    """
    
    if user_id:
        base_query += f" AND b.user_id = {user_id}"
        
    if active_only:
        base_query += " AND (s.show_date > CURDATE() OR (s.show_date = CURDATE() AND s.show_time > CURTIME()))"
        
    console.print("\n[bold cyan]Filter by:[/bold cyan]")
    console.print("[bold yellow]1.[/bold yellow] All Tickets")
    console.print("[bold yellow]2.[/bold yellow] By Movie Name")
    console.print("[bold yellow]3.[/bold yellow] By Theater / Location")
    console.print("[bold yellow]4.[/bold yellow] By Show Time (Date)")
    if not user_id:
        console.print("[bold yellow]5.[/bold yellow] By User ID")
    
    choice = console.input("\n[bold green]Enter Choice: [/bold green]").strip()
    
    if choice == "1":
        query = base_query + " ORDER BY b.booking_id DESC"
        cursor.execute(query)
    elif choice == "2":
        movie_name = get_string("Enter Movie Name:")
        query = base_query + " AND m.movie_name LIKE %s ORDER BY b.booking_id DESC"
        cursor.execute(query, ("%" + movie_name + "%",))
    elif choice == "3":
        loc = get_string("Enter Theater Name or Location:")
        query = base_query + " AND (t.theater_name LIKE %s OR t.location LIKE %s) ORDER BY b.booking_id DESC"
        cursor.execute(query, ("%" + loc + "%", "%" + loc + "%"))
    elif choice == "4":
        show_date = console.input("[bold green]Enter Date (YYYY-MM-DD): [/bold green]").strip()
        query = base_query + " AND s.show_date = %s ORDER BY s.show_time"
        cursor.execute(query, (show_date,))
    elif choice == "5" and not user_id:
        uid = console.input("[bold green]Enter User ID: [/bold green]").strip()
        if not uid.isdigit():
            console.print("[bold red]Invalid User ID.[/bold red]")
            return None
        query = base_query + " AND b.user_id = %s ORDER BY b.booking_id DESC"
        cursor.execute(query, (int(uid),))
    else:
        console.print("[bold red]Invalid choice.[/bold red]")
        return None
        
    return cursor.fetchall()

def display_tickets_table(records, title, status_color):
    if not records:
        console.print(f"\n[bold yellow]⚠️ No {title.lower()} found.[/bold yellow]")
        return

    table = Table(title=f"🎟️ {title}", border_style=status_color)
    table.add_column("Booking ID", style="cyan")
    table.add_column("User ID", style="white")
    table.add_column("Movie", style="green")
    table.add_column("Theater", style="yellow")
    table.add_column("Date", style="blue")
    table.add_column("Time", style="cyan")
    table.add_column("Seat", style="magenta")
    table.add_column("Amount", style="green")

    for row in records:
        table.add_row(str(row[0]), str(row[1]), row[2], f"{row[3]} ({row[4]})", str(row[5]), str(row[6]), row[7], f"₹{row[8]}")
    console.print(table)

def view_tickets(user_id=None):
    try:
        console.print(Panel.fit("[bold cyan]VIEW ACTIVE TICKETS (Upcoming Shows Only)[/bold cyan]"))
        records = get_filtered_tickets("Booked", user_id, active_only=True)
        if records is not None:
            display_tickets_table(records, "ACTIVE TICKETS", "cyan")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

def search_ticket(user_id=None):
    try:
        booking_id = console.input("\n[bold green]Enter Booking ID : [/bold green]").strip()
        if not booking_id.isdigit():
            console.print("[bold red]Invalid Booking ID.[/bold red]")
            return
            
        if user_id:
            cursor.execute("SELECT booking_id, user_id, show_id, seat_id, booking_date, total_amount, status FROM bookings WHERE booking_id = %s AND user_id = %s", (int(booking_id), user_id))
        else:
            cursor.execute("SELECT booking_id, user_id, show_id, seat_id, booking_date, total_amount, status FROM bookings WHERE booking_id = %s", (int(booking_id),))
            
        row = cursor.fetchone()
        
        if not row:
            console.print("[bold red]❌ Ticket not found or access denied.[/bold red]")
            return

        table = Table(title="🎟️ TICKET DETAILS", border_style="green")
        table.add_column("Field", style="bold cyan")
        table.add_column("Value", style="bold white")
        table.add_row("Booking ID", str(row[0]))
        table.add_row("User ID", str(row[1]))
        table.add_row("Show ID", str(row[2]))
        table.add_row("Seat ID", str(row[3]))
        table.add_row("Amount", f"₹{row[5]}")
        table.add_row("Status", str(row[6] or 'Booked'))
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

def cancel_ticket(user_id=None):
    try:
        console.print(Panel.fit("[bold cyan]CANCEL TICKET[/bold cyan]"))
        booking_id = console.input("\n[bold green]Enter Booking ID to cancel : [/bold green]").strip()
        if not booking_id.isdigit():
            console.print("[bold red]Invalid Booking ID.[/bold red]")
            return
            
        if user_id:
            cursor.execute("""
                SELECT b.status, s.show_date, s.show_time, b.total_amount 
                FROM bookings b JOIN shows s ON b.show_id = s.show_id 
                WHERE b.booking_id = %s AND b.user_id = %s
            """, (int(booking_id), user_id))
        else:
            cursor.execute("""
                SELECT b.status, s.show_date, s.show_time, b.total_amount 
                FROM bookings b JOIN shows s ON b.show_id = s.show_id 
                WHERE b.booking_id = %s
            """, (int(booking_id),))
            
        row = cursor.fetchone()
        
        if not row:
            console.print("[bold red]❌ Ticket not found or access denied.[/bold red]")
            return

        status, show_date, show_time, total_amount = row[0], row[1], row[2], float(row[3])
        
        if status and status.lower() == "cancelled":
            console.print("[bold yellow]⚠️️ This ticket is already cancelled.[/bold yellow]")
            return

        show_datetime = datetime.combine(show_date, (datetime.min + show_time).time())
        current_datetime = datetime.now()
        
        time_diff = show_datetime - current_datetime
        hours_diff = time_diff.total_seconds() / 3600

        if hours_diff < 0:
            console.print("[bold red]❌ The show has already passed. Cancellation is not allowed.[/bold red]")
            return
            
        refund_amount = total_amount
        if hours_diff < 10:
            refund_amount = total_amount * 0.60
            console.print(f"[bold yellow]⚠️ Cancellation within 10 hours of the show. Only 60% (₹{refund_amount:.2f}) will be refunded.[/bold yellow]")
        else:
            console.print(f"[bold green]Full refund of ₹{refund_amount:.2f} will be processed.[/bold green]")

        if get_yes_no("Are you sure you want to cancel this ticket?"):
            cursor.execute("UPDATE bookings SET status = 'Cancelled' WHERE booking_id = %s", (int(booking_id),))
            conn.commit()
            console.print(Panel.fit(f"[bold green]✅ Ticket cancelled successfully. Refund Amount: ₹{refund_amount:.2f}[/bold green]"))
        else:
            console.print("[bold cyan]Cancellation aborted.[/bold cyan]")
            
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

def view_cancelled_tickets(user_id=None):
    try:
        console.print(Panel.fit("[bold cyan]VIEW CANCELLED TICKETS[/bold cyan]"))
        records = get_filtered_tickets("Cancelled", user_id, active_only=False)
        if records is not None:
            display_tickets_table(records, "CANCELLED TICKETS", "red")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")