from db import conn, cursor
from utils import send_pdf_email
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def generate_ticket(booking_id, user_id=None):
    try:
        if user_id:
            query = """
                SELECT
                    b.booking_id, b.user_id, b.booking_date, b.total_amount,
                    m.movie_name, m.language,
                    t.theater_name, t.location,
                    s.show_date, s.show_time,
                    se.seat_number, se.seat_type, se.seat_price,
                    p.payment_mode, p.payment_amount, p.payment_date
                FROM bookings b
                JOIN shows s ON b.show_id = s.show_id
                JOIN movies m ON s.movie_id = m.movie_id
                JOIN theaters t ON s.theater_id = t.theater_id
                JOIN seats se ON b.seat_id = se.seat_id
                LEFT JOIN payments p ON b.booking_id = p.booking_id
                WHERE b.booking_id = %s AND b.user_id = %s AND (b.status = 'Booked' OR b.status IS NULL)
            """
            cursor.execute(query, (booking_id, user_id))
        else:
            query = """
                SELECT
                    b.booking_id, b.user_id, b.booking_date, b.total_amount,
                    m.movie_name, m.language,
                    t.theater_name, t.location,
                    s.show_date, s.show_time,
                    se.seat_number, se.seat_type, se.seat_price,
                    p.payment_mode, p.payment_amount, p.payment_date
                FROM bookings b
                JOIN shows s ON b.show_id = s.show_id
                JOIN movies m ON s.movie_id = m.movie_id
                JOIN theaters t ON s.theater_id = t.theater_id
                JOIN seats se ON b.seat_id = se.seat_id
                LEFT JOIN payments p ON b.booking_id = p.booking_id
                WHERE b.booking_id = %s AND (b.status = 'Booked' OR b.status IS NULL)
            """
            cursor.execute(query, (booking_id,))
            
        ticket = cursor.fetchone()
        
        if not ticket:
            console.print("[bold red]❌ No active booking found or access denied for this Booking ID.[/bold red]")
            return

        table = Table(title="🍿 MOVIE TICKET 🍿", show_header=False, border_style="cyan")
        table.add_row("Booking ID", str(ticket[0]))
        table.add_row("User ID", str(ticket[1]))
        table.add_row("Movie", ticket[4].upper())
        table.add_row("Language", ticket[5].title())
        table.add_row("Theater", f"{ticket[6]} ({ticket[7]})")
        table.add_row("Show Date", str(ticket[8]))
        table.add_row("Show Time", str(ticket[9]))
        table.add_row("Seat", ticket[10])
        table.add_row("Seat Type", ticket[11])
        table.add_row("Total Amount", f"₹{ticket[3]:.2f}")
        
        payment_status = "PAID" if ticket[13] else "PENDING"
        if ticket[13]:
            table.add_row("Payment Status", "[bold green]PAID[/bold green]")
        else:
            table.add_row("Payment Status", "[bold yellow]PENDING[/bold yellow]")

        console.print()
        console.print(table)
        
        if user_id:
            cursor.execute("SELECT email FROM users WHERE user_id = %s", (user_id,))
            email_res = cursor.fetchone()
            if email_res:
                user_email = email_res[0]
                ticket_text = f"MOVIE TICKET\n------------------------------\nBooking ID : {ticket[0]}\nMovie      : {ticket[4].upper()}\nLanguage   : {ticket[5].title()}\nTheater    : {ticket[6]} ({ticket[7]})\nDate       : {ticket[8]}\nTime       : {ticket[9]}\nSeat       : {ticket[10]} ({ticket[11]})\nAmount     : Rs. {ticket[3]:.2f}\nPayment    : {payment_status}\n------------------------------\nEnjoy the movie!"
                
                console.print("[bold cyan]Generating and sending PDF ticket to your email...[/bold cyan]")
                if send_pdf_email(user_email, "Your Movie Ticket", ticket_text, "Movie_Ticket.pdf"):
                    console.print(Panel.fit("[bold green]✅ Ticket generated and emailed successfully![/bold green]"))
        else:
            console.print(Panel.fit("[bold green]✅ Ticket generated successfully![/bold green]"))

    except Exception as e:
        console.print(f"[bold red]❌ Unable to generate ticket: {e}[/bold red]")