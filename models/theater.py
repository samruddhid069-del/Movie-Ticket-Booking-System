class Theater:
    def __init__(self, theater_id=None, theater_name=None, location=None):
        self.theater_id = theater_id
        self.theater_name = theater_name
        self.location = location

    def __str__(self):
        return (f"Theater ID : {self.theater_id}\nTheater Name : {self.theater_name}\nLocation : {self.location}")