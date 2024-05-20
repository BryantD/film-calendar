import html
import json
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from filmcalendar import filmcalendar


class FilmCalendarRoxie(filmcalendar.FilmCalendar):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.address = "3125 16th Street, San Francisco, CA 94103"
        self.base_url = "https://roxie.com"

    def __str__(self):
        return super().__str__()

    def fetch_films(self):
        try:
            req = requests.get(
                f"{self.base_url}/calendar/",
                headers=self.req_headers,
            )
        except requests.exceptions.RequestException:
            raise

        soup = BeautifulSoup(req.text, "html.parser")

        film_location = f"{self.theater}: {self.address}"
        for month_item in soup.find_all("div", class_="calendar-block__month"):
            for item in month_item.find_all("div", class_="film-strip"):
                film_title = item.find("h4").text
                film_url = item.find("h4").find("a")["href"]
                showtimes_item = item.find("div", class_="film-strip__showtimes")
                date_item = showtimes_item.find("p", class_="film-strip__date")
                dt_date = datetime.strptime(date_item.text, "%A, %B %d, %Y")
                # FIXME we need to scrape the duration from the show page
                film_duration = timedelta(minutes=120)
                for showtimes_link_item in showtimes_item.find_all("a"):
                    dt_time = datetime.strptime(
                        showtimes_link_item.text.strip(), "%I:%M %p"
                    )
                    film_date = datetime(
                        dt_date.year,
                        dt_date.month,
                        dt_date.day,
                        dt_time.hour,
                        dt_time.minute,
                    )
                    self.add_event(
                        summary=film_title,
                        dtstart=film_date,
                        duration=film_duration,
                        url=film_url,
                        location=film_location,
                    )
