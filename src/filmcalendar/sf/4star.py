from filmcalendar.sf.cinemasf import CinemaSF


class FilmCalendar4Star(CinemaSF):
    def __init__(self, **kwds):
        super().__init__(
            "2200 Clement Street, San Francisco, CA 94121",
            "https://www.4-star-movies.com",
            "616e05fa520d8e7b1cd0ae3d",
            **kwds,
        )
