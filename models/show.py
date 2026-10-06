class Show:
    def __init__(self, show_id=None, movie_id=None, theater_id=None, show_date=None, show_time=None):
        self.show_id = show_id
        self.movie_id = movie_id
        self.theater_id = theater_id
        self.show_date = show_date
        self.show_time = show_time

    def __str__(self):
        return (f"Show ID : {self.show_id}\nMovie ID : {self.movie_id}\nTheater ID : {self.theater_id}\nShow Date : {self.show_date}\nShow Time : {self.show_time}")