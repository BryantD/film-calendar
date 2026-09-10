import re
import string
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from filmcalendar import filmcalendar


class FilmCalendarTheBeacon(filmcalendar.FilmCalendar):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.base_url = "https://thebeacon.film"
        self.location_string = f"{self.theater}: 4405 Rainier Ave S, Seattle, WA 98118"

    def __str__(self):
        return super().__str__()

    def _fetch_film_page(self, film_url):
        try:
            req = requests.get(f"{self.base_url}{film_url}", headers=self.req_headers)
        except requests.exceptions.RequestException:
            raise

        soup = BeautifulSoup(req.text, "html.parser")

        # Note -- this breaks if they ever do a '1 hour 20 minutes' duration
        # but the exception catching handles that
        try:
            duration_string = soup.find(
                "p", class_="meta-value", string=re.compile(r"\d+ minutes")
            )
            film_duration = timedelta(
                minutes=int(duration_string.get_text().split()[0])
            )
        except AttributeError:
            film_duration = timedelta(minutes=120)

        return {"duration": film_duration}

    def fetch_films(self):
        # Cheap cache for repeated movies so we don't crawl the same movie
        # page twice -- index is URI
        cache = {}

        try:
            req = requests.get(f"{self.base_url}/calendar", headers=self.req_headers)
        except requests.exceptions.RequestException:
            raise

        soup = BeautifulSoup(req.text, "html.parser")

        for day in soup.find_all("p", class_="cal-list-date"):
            film_date_day_string = day.getText()

            for film in day.parent.find_all("div", class_="cal-list-entry"):
                film_a = film.find("a", class_="cal-list-movie")
                if film_a:
                    film_title = string.capwords(film_a.get_text())
                    film_url = film_a["href"]

                    film_time_string = film.find(
                        "span", class_="cal-list-time"
                    ).get_text()

                    if film_time_string:
                        # This is clunky but you can't simply + two datetime
                        # instances together
                        film_date = datetime.strptime(
                            f"{film_time_string} {film_date_day_string} {datetime.now().year}",  # noqa E501
                            "%I:%M %p %A, %B %d %Y",
                        )
                        # Hardcoding a skip for rental slots
                        if film_title != "Rent The Beacon":
                            if film_url not in cache:
                                film_data = self._fetch_film_page(film_url)
                                film_data["summary"] = film_title
                                film_data["dtstart"] = film_date
                                film_data["url"] = self.base_url + film_url
                                cache[film_url] = film_data
                            else:
                                film_data = cache[film_url]
                                film_data["dtstart"] = film_date

                            self.add_event(
                                summary=film_data["summary"],
                                dtstart=film_data["dtstart"],
                                duration=film_data["duration"],
                                url=film_data["url"],
                                location=self.location_string,
                            )

                    else:
                        print(
                            f"Couldn't find span class='cal-list-time' for {film_title} on {film_date_day_string}"  # noqa E501
                        )
                else:
                    print("Couldn't find <a> tag for movie!")
