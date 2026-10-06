class Payment:
    def __init__(self, payment_id=None, booking_id=None, payment_amount=0.0, payment_mode="", status="Pending", payment_date=None):
        self.payment_id = payment_id
        self.booking_id = booking_id
        self.payment_amount = payment_amount
        self.payment_mode = payment_mode
        self.status = status
        self.payment_date = payment_date

    def display_payment(self):
        print("\n========== PAYMENT DETAILS ==========")
        print(f"Payment ID     : {self.payment_id}")
        print(f"Booking ID     : {self.booking_id}")
        print(f"Amount         : ₹{self.payment_amount:.2f}")
        print(f"Payment Mode   : {self.payment_mode}")
        print(f"Status         : {self.status}")
        print(f"Payment Date   : {self.payment_date}")