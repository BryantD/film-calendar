import string
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from filmcalendar import filmcalendar


class FilmCalendarTheBeacon(filmcalendar.FilmCalendar):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.base_url = "https://thebeacon.film"

    def __str__(self):
        return super().__str__()

    def fetch_films(self):
        try:
            req = requests.get(f"{self.base_url}/calendar", headers=self.req_headers)
        except requests.exceptions.RequestException:
            raise

        soup = BeautifulSoup(req.text, "html.parser")

        for film in soup.find_all("section", class_="showtime"):
            try:
                film_title = string.capwords(
                    film.find("section", itemprop="name").get_text()
                )
            except TypeError as error:
                raise ValueError("Couldn't find film name") from error
            if film_title != "Rent The Beacon":
                # Hardcoding a skip for rental slots
                try:
                    film_date = self.timezone.localize(
                        datetime.fromisoformat(
                            film.find("section", itemprop="startDate")["content"]
                        )
                    )
                except TypeError as error:
                    raise ValueError("Couldn't find film start time") from error
                try:
                    film_url = film.find("a")["href"]
                except TypeError:
                    film_url = None
                try:
                    film_street = film.find("span", itemprop="streetAddress").get_text()
                    film_city = film.find("span", itemprop="addressLocality").get_text()
                    film_state = film.find("span", itemprop="addressRegion").get_text()
                    film_zip = film.find("span", itemprop="postalCode").get_text()
                    film_location = (
                        f"{self.theater}: "
                        f"{film_street}, "
                        f"{film_city}, {film_state} {film_zip}"
                    )

                except TypeError:
                    film_location = self.theater
                film_duration = timedelta(minutes=120)

                self.add_event(
                    summary=film_title,
                    dtstart=film_date,
                    duration=film_duration,
                    url=film_url,
                    location=film_location,
                )
