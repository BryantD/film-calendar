from filmcalendar.sf.cinemasf import CinemaSF


class FilmCalendarVogue(CinemaSF):
    def __init__(self, **kwds):
        super().__init__(
            "3290 Sacramento Street, San Francisco, CA 94115",
            "https://www.voguemovies.com",
            "616e04d8e4d9fb14d6cd620d",
            **kwds
        )
