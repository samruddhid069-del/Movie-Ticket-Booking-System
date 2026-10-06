from datetime import datetime
from db import conn, cursor
from models.payment import Payment
from utils import send_pdf_email
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def process_multiple_payments(booking_data, total_amount, user_id=None):
    try:
        console.print(Panel.fit(f"[bold cyan]💳 SECURE PAYMENT GATEWAY[/bold cyan]\n[bold green]Total Amount to Pay: ₹{total_amount:.2f}[/bold green]"))
        
        console.print("\n[bold yellow]Select Payment Mode:[/bold yellow]")
        console.print("1. UPI\n2. Card\n3. Cash")
        choice = console.input("[bold green]Enter Choice: [/bold green]").strip()
        
        modes = {"1": "UPI", "2": "Card", "3": "Cash"}
        payment_mode = modes.get(choice)
        
        if not payment_mode:
            console.print("[bold red]❌ Payment Cancelled.[/bold red]")
            return False

        payment_date = datetime.now()
        booking_ids = []
        
        for booking_id, price in booking_data:
            cursor.execute("""
                INSERT INTO payments (booking_id, payment_mode, payment_amount, payment_date) 
                VALUES (%s, %s, %s, %s)
            """, (booking_id, payment_mode, price, payment_date))
            booking_ids.append(str(booking_id))
            
        conn.commit()
        
        console.print(Panel.fit("[bold green]✅ Payment Successful for all tickets![/bold green]"))
        
        # Email Receipt Logic
        if user_id:
            cursor.execute("SELECT email FROM users WHERE user_id = %s", (user_id,))
            email_res = cursor.fetchone()
            if email_res:
                user_email = email_res[0]
                receipt_text = f"PAYMENT RECEIPT\n------------------------------\nBooking IDs  : {', '.join(booking_ids)}\nTotal Amount : Rs. {total_amount:.2f}\nPayment Mode : {payment_mode}\nDate         : {payment_date}\nStatus       : SUCCESS\n------------------------------\nThank you for using Movie Ticket Booking System!"
                console.print("[bold cyan]Generating and sending PDF receipt to your email...[/bold cyan]")
                if send_pdf_email(user_email, "Your Payment Receipt", receipt_text, "Payment_Receipt.pdf"):
                    console.print("[bold green]✅ Receipt emailed successfully![/bold green]")
                
        return True
    except Exception as e:
        conn.rollback()
        console.print(f"[bold red]❌ Payment Failed: {e}[/bold red]")
        return False

def view_payments(user_id=None):
    try:
        console.print(Panel.fit("[bold cyan]VIEW PAYMENT HISTORY[/bold cyan]"))
        
        if user_id:
            cursor.execute("""
                SELECT p.payment_id, p.booking_id, p.payment_mode, p.payment_amount, p.payment_date, m.movie_name 
                FROM payments p
                JOIN bookings b ON p.booking_id = b.booking_id
                JOIN shows s ON b.show_id = s.show_id
                JOIN movies m ON s.movie_id = m.movie_id
                WHERE b.user_id = %s ORDER BY p.payment_date DESC
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT p.payment_id, p.booking_id, p.payment_mode, p.payment_amount, p.payment_date, m.movie_name 
                FROM payments p
                JOIN bookings b ON p.booking_id = b.booking_id
                JOIN shows s ON b.show_id = s.show_id
                JOIN movies m ON s.movie_id = m.movie_id
                ORDER BY p.payment_date DESC
            """)
            
        records = cursor.fetchall()
        if not records:
            console.print("[bold red]No Payments Found.[/bold red]")
            return
            
        table = Table(title="PAYMENT HISTORY", border_style="cyan")
        table.add_column("Payment ID", style="cyan")
        table.add_column("Booking ID", style="yellow")
        table.add_column("Movie", style="green")
        table.add_column("Mode", style="magenta")
        table.add_column("Amount", style="green")
        table.add_column("Date", style="white")

        for r in records:
            table.add_row(str(r[0]), str(r[1]), r[5], r[2], f"₹{r[3]:.2f}", str(r[4]))
            
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

def generate_receipt(user_id=None):
    try:
        console.print(Panel.fit("[bold cyan]🧾 GENERATE RECEIPT[/bold cyan]"))
        
        view_payments(user_id)
        
        booking_id_str = console.input("\n[bold green]Enter Booking ID for receipt: [/bold green]").strip()
        if not booking_id_str.isdigit():
            console.print("[bold red]Invalid input! Booking ID must be a number.[/bold red]")
            return
            
        booking_id = int(booking_id_str)
        
        if user_id:
            cursor.execute("""
                SELECT p.payment_id, p.booking_id, p.payment_mode, p.payment_amount, p.payment_date 
                FROM payments p JOIN bookings b ON p.booking_id = b.booking_id 
                WHERE p.booking_id = %s AND b.user_id = %s
            """, (booking_id, user_id))
        else:
            cursor.execute("""
                SELECT payment_id, booking_id, payment_mode, payment_amount, payment_date 
                FROM payments WHERE booking_id = %s
            """, (booking_id,))
            
        record = cursor.fetchone()
        
        if not record:
            console.print("[bold red]❌ Payment Not Found or you don't have access to this booking.[/bold red]")
            return
        
        payment = Payment(
            payment_id=record[0], 
            booking_id=record[1], 
            payment_mode=record[2], 
            payment_amount=record[3], 
            status="Successful", 
            payment_date=record[4]
        )
        
        table = Table(title="PAYMENT RECEIPT", show_header=False, border_style="cyan")
        table.add_row("Payment ID", str(payment.payment_id))
        table.add_row("Booking ID", str(payment.booking_id))
        table.add_row("Amount", f"₹{payment.payment_amount:.2f}")
        table.add_row("Payment Mode", str(payment.payment_mode))
        table.add_row("Status", f"[bold green]{payment.status}[/bold green]")
        table.add_row("Payment Date", str(payment.payment_date))
        
        console.print(table)
        
        if user_id:
            cursor.execute("SELECT email FROM users WHERE user_id = %s", (user_id,))
            email_res = cursor.fetchone()
            if email_res:
                user_email = email_res[0]
                receipt_text = f"PAYMENT RECEIPT\n------------------------------\nPayment ID   : {payment.payment_id}\nBooking ID   : {payment.booking_id}\nAmount       : Rs. {payment.payment_amount:.2f}\nPayment Mode : {payment.payment_mode}\nStatus       : {payment.status}\nDate         : {payment.payment_date}\n------------------------------\nThank you!"
                console.print("[bold cyan]Generating and sending PDF receipt to your email...[/bold cyan]")
                if send_pdf_email(user_email, "Your Payment Receipt", receipt_text, "Payment_Receipt.pdf"):
                    console.print("[bold green]✅ Receipt emailed successfully![/bold green]")
        else:
            console.print(Panel.fit("[bold green]✅ Receipt generated successfully![/bold green]"))
        
    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")