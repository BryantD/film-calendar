import logging
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from filmcalendar import filmcalendar


class FilmCalendarLightHouse(filmcalendar.FilmCalendar):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.address = "Market St S, Smithfield, Dublin 7, D07 R6YE"
        self.base_url = "https://www.lighthousecinema.ie/ajax/films-by-day"

    def __str__(self):
        return super().__str__()

    def fetch_film_day(self, relative_day):
        log = logging.getLogger(__name__)

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
            # Try to find duration
            duration_text = ""
            duration_elem = film.find("div", class_="shortened-aside")
            if duration_elem:
                duration_text = duration_elem.get_text(strip=True)
                # Format is usually "Rating / X Mins"
                if "Mins" in duration_text:
                    try:
                        minutes = int(
                            duration_text.split("/")[-1].replace("Mins", "").strip()
                        )
                        film_duration = timedelta(minutes=minutes)
                    except ValueError:
                        log.warning(
                            f"Could not parse duration from '{duration_text}' for {film_title}"  # noqa: E501
                        )
                        continue
                else:
                    log.warning(
                        f"Could not find 'Mins' in '{duration_text}' for {film_title}"
                    )
                    continue
            else:
                continue
            film_location = f"{self.theater}: {self.address}"
            for showing in film.find("div", class_="times").find_all("a"):
                movie_hour, movie_minute = showing.get_text().split(":")
                # Clean up "Sold out" or other text
                movie_minute = "".join(filter(str.isdigit, movie_minute))
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
        for day in range(0, 14):
            # 15 days is arbitrary but I think two weeks is a good window
            self.fetch_film_day(day)
