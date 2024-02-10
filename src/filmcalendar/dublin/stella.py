import json
import re
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from filmcalendar import filmcalendar


class FilmCalendarStella(filmcalendar.FilmCalendar):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.addresses = {
            "rathmines": "207-209 Rathmines Rd Lower, Rathmines, Dublin 6, D06 W403",
            "ranelagh": "117-119 Ranelagh, Dublin 6, D06 WY50",
        }
        self.base_url = "https://stellacinemas.ie"

    def __str__(self):
        return super().__str__()

    def fetch_film_day(self, relative_day):
        try:
            req = requests.get(
                f"{self.base_url}/{relative_day}", headers=self.req_headers
            )
        except requests.exceptions.RequestException:
            raise

        movie_date = datetime.now(self.timezone) + timedelta(days=relative_day)
        movie_date = movie_date.replace(hour=0, minute=0, second=0, microsecond=0)

        soup = BeautifulSoup(req.text, "html.parser")

        event_data = soup.find_all("li", class_="on")
        for film in event_data:
            film_title = film.find("h3").find("a").get_text(strip=True)
            film_url = film.find("h3").find("a")["href"]
            film_duration = timedelta(
                minutes=int(film.find("span", class_="where").get_text()[:-5])
            )
            film_location = f"{self.theater}: {self.address}"
            for showing in film.find("div", class_="times").find_all("a"):
                movie_hour, movie_minute = showing.get_text().split(":")
                film_date = movie_date.replace(
                    hour=int(movie_hour), minute=int(movie_minute)
                )
                self.add_event(
                    summary=film_title,
                    dtstart=film_date,
                    duration=film_duration,
                    url=film_url,
                    location=film_location,
                )

    def fetch_films(self):
        try:
            req = requests.get(f"{self.base_url}/", headers=self.req_headers)
        except requests.exceptions.RequestException:
            raise

        # The HTML is not well-formed, so we need to find the right line manually
        film_data = ""
        for line in req.text.splitlines():
            if "data-categories" in line:
                film_data = line
        if not film_data:
            return

        # text between 'data-data="' and '" data-events', non-inclusive
        film_json = json.loads(
            film_data.split('data-data="')[1].split('" data-events')[0]
        )

        film_duration = timedelta(minutes=120)

        for film in film_json:
            film_title = film["event_title"]
            film_location = self.addresses[film["taxonomy"][0]]
            film_url = (
                self.base_url
                + "/events/"
                + film["taxonomy"][0]
                + "/"
                + film["event_slug"]
            )
            film["date"] = re.sub(r"(\d)(st|nd|rd|th)", r"\1", film["date"])
            film_date = datetime.strptime(
                f"{film['date']} {film['time']}",
                "%A, %B %d, %Y %I:%M %p",
            )

            self.add_event(
                summary=film_title,
                dtstart=film_date,
                duration=film_duration,
                url=film_url,
                location=film_location,
            )
