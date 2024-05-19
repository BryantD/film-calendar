import html
import json
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from filmcalendar import filmcalendar


class FilmCalendarMarina(filmcalendar.FilmCalendar):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.address = "2149 Chestnut St., San Francisco, CA 94123"
        self.base_url = "https://www.lntsf.com/marina-theatre"

    def __str__(self):
        return super().__str__()

    def fetch_films(self):
        try:
            req = requests.get(
                f"{self.base_url}",
                headers=self.req_headers,
            )
        except requests.exceptions.RequestException:
            raise

        soup = BeautifulSoup(req.text, "html.parser")

        film_url = self.base_url
        film_location = f"{self.theater}: {self.address}"
        year = datetime.now().year
        for item in soup.find_all("h3"):
            film_title = item.text
            duration_str = item.parent.find("em").text.split("‧")[2].strip()
            duration_dt = datetime.strptime(duration_str, "%Hh %Mm")
            film_duration = timedelta(
                hours=duration_dt.hour, minutes=duration_dt.minute
            )
            for per_day_item in item.parent.find_all("strong"):
                per_day = per_day_item.text.strip()
                day_str, times_str = per_day.split(":", 1)
                days = day_str.split(" to ")
                times = times_str.strip().split()
                for day in days:
                    for time in times:
                        film_date = datetime.strptime(
                            f"{year} {day} {time} PM", "%Y %a %m/%d %I:%M %p"
                        )
                        self.add_event(
                            summary=film_title,
                            dtstart=film_date,
                            duration=film_duration,
                            url=film_url,
                            location=film_location,
                        )
