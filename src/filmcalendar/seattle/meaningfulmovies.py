import re
import string
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from filmcalendar import filmcalendar


class FilmCalendarMeaningfulMovies(filmcalendar.FilmCalendar):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.base_url = "https://meaningfulmovies.org/neighborhoods"
        self.chapters = [
            "ballard",
            "meaning-movies-rainier-beach",
            "mt-baker",
            "west-seattle",
        ]

    def __str__(self):
        return super().__str__()

    def _parse_duration(self, duration_raw):
        minutes = 120  # fall through value
        # No satisfying way to use match / case here since the format of the
        # duration string is pretty random.
        # "1h 26m" and "95 minutes" are cases I've seen so far
        # Tossed in "1 hour 40 minutes" just in case
        # # And, hey, "2 hours"

        if match := re.fullmatch(r"(\d+) minutes", duration_raw):
            minutes = int(match.group(1))
        elif match := re.fullmatch(r"(\d+)h (\d+)m", duration_raw):
            minutes = (int(match.group(1)) * 60) + (int(match.group(2)))
        elif match := re.fullmatch(r"(\d+) hours* (\d+) minutes*", duration_raw):
            minutes = (int(match.group(1)) * 60) + (int(match.group(2)))
        elif match := re.fullmatch(r"(\d+) hours*", duration_raw):
            minutes = int(match.group(1) * 60)
        else:
            minutes = 120

        return timedelta(minutes=minutes)

    def _scrape_movie_page(self, film_url):
        try:
            req = requests.get(film_url, headers=self.req_headers)
        except requests.exceptions.RequestException:
            raise
        film_soup = BeautifulSoup(req.text, "html.parser")

        duration_span = film_soup.find(
            "span", string=lambda text: text and "Running Time: " in text
        )
        if duration_span:
            film_duration = self._parse_duration(
                duration_span.parent.text.removeprefix("Running Time: ")
            )

        # Location appears to be freeform text so we'll pass it through.
        # Weirdly there's a consistent missing space between "Seattle" and "WA"
        # so I special cased that.

        location_span = film_soup.find("span", class_="event-address")
        if location_span:
            film_location = location_span.text.replace(",WA", ", WA").strip()
        else:
            film_location = "Unknown -- check event page for details"

        return film_location, film_duration

    def fetch_films(self):
        for chapter in self.chapters:
            try:
                req = requests.get(
                    f"{self.base_url}/{chapter}", headers=self.req_headers
                )
            except requests.exceptions.RequestException:
                raise

            soup = BeautifulSoup(req.text, "html.parser")

            # All the <li class="mmp-event"> in the <ul class="mmp-event-list">
            # with sibling <h2 class="main-title">Our Upcoming Events</h2>

            header = soup.find("h2", class_="main-title", string="Our Upcoming Events")
            if header:
                upcoming_films = header.find_next_sibling()
                if upcoming_films and not upcoming_films.text == "Our Past Events":
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
                        (film_location, film_duration) = self._scrape_movie_page(
                            film_url
                        )

                        self.add_event(
                            summary=film_title,
                            dtstart=film_date,
                            duration=film_duration,
                            url=film_url,
                            location=film_location,
                        )
