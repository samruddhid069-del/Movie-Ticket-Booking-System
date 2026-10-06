class Seat:
    def __init__(self, seat_id, theater_id, seat_number, seat_type, seat_price, is_blocked=False):
        self.seat_id = seat_id
        self.theater_id = theater_id
        self.seat_number = seat_number
        self.seat_type = seat_type
        self.seat_price = seat_price
        self.is_blocked = is_blocked