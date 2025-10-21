from filmcalendar.sf.cinemasf import CinemaSF


class FilmCalendarBalboa(CinemaSF):
    def __init__(self, **kwds):
        super().__init__(
            "3630 Balboa Street, San Francisco, CA 94121",
            "https://www.balboamovies.com",
            "616e03c4b792dc0e9cf140e7",
            **kwds,
        )
