import string
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from filmcalendar import filmcalendar


class FilmCalendarMeaningfulMovies(filmcalendar.FilmCalendar):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.base_url = "https://meaningfulmovies.org/neighborhoods/ballard/"

    def __str__(self):
        return super().__str__()

    def fetch_film(self, film_url):
        # <span class="event-address">Center for Spiritual Living Ballard 2007 NW 61st St&nbsp;Seattle,WA </span> # noqa: E501
        # <p><span>Running Time: </span>96 m</p>
        film_location = "Center for Spiritual Living"
        film_duration = timedelta(minutes=120)
        return film_location, film_duration

    def fetch_films(self):
        try:
            req = requests.get(f"{self.base_url}", headers=self.req_headers)
        except requests.exceptions.RequestException:
            raise

        soup = BeautifulSoup(req.text, "html.parser")

        # All the <li class="mmp-event"> in the <ul class="mmp-event-list">
        # with sibling <h2 class="main-title">Our Upcoming Events</h2>

        upcoming_films = soup.find(
            "h2", class_="main-title", string="Our Upcoming Events"
        ).next_sibling
        for film in upcoming_films.find_all("li", class_="mmp-event"):
            try:
                film_title = string.capwords(
                    film.find("h4", class_="event-title").get_text()
                )
            except TypeError as error:
                raise ValueError("Couldn't find film name") from error
            try:
                film_date = self.timezone.localize(
                    datetime.strptime(
                        film.find("div", class_="event-time").string,
                        "%A | %m/%d/%Y | %I:%M %p",
                    )
                )
            except TypeError as error:
                raise ValueError("Couldn't find film start time") from error
            try:
                film_url = film.find("h4", class_="event-title").a["href"]
            except TypeError:
                film_url = None

            # Address and duration on details page
            film_location, film_duration = self.fetch_film(film_url)

            self.add_event(
                summary=film_title,
                dtstart=film_date,
                duration=film_duration,
                url=film_url,
                location=film_location,
            )
