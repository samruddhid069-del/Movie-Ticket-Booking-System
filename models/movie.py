class Movie:
    def __init__(self, movie_name, genre, language, duration, release_date):
        self.movie_name = movie_name
        self.genre = genre
        self.language = language
        self.duration = duration
        self.release_date = release_date

    def __str__(self):
        return (f"Movie Name : {self.movie_name}\nGenre : {self.genre}\nLanguage : {self.language}\nDuration : {self.duration} Minutes\nRelease Date : {self.release_date}")