class Booking:
    def __init__(self, booking_id=None, user_id=None, show_id=None, seat_id=None, booking_date=None, total_amount=0):
        self.booking_id = booking_id
        self.user_id = user_id
        self.show_id = show_id
        self.seat_id = seat_id
        self.booking_date = booking_date
        self.total_amount = total_amount

    def __str__(self):
        return (f"Booking ID : {self.booking_id}\nUser ID : {self.user_id}\nShow ID : {self.show_id}\nSeat ID : {self.seat_id}\nBooking Date : {self.booking_date}\nTotal Amount : {self.total_amount}")