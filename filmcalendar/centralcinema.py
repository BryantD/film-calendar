from . import filmcalendar

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import html


class FilmCalendarCentralCinema(filmcalendar.FilmCalendar):
    def __init__(self):
        super().__init__()
        self.theater = "Central Cinema"
        self.address = "1411 21st Ave., Seattle, WA 98122"
        self.base_url = "https://www.goelevent.com"

    def __str__(self):
        return super().__str__()

    def fetch_films(self):
        req_payload = {"t": "1"}
        try:
            req = requests.get(
                "https://www.goelevent.com/CentralCinema/e/List?s=&v=&t=1&st=null",
                headers=self.req_headers,
                params=req_payload,
            )
        except requests.exceptions.RequestException:
            raise

        soup = BeautifulSoup(req.text, "html.parser")

        event_data = soup.find("div", id="event-search-list-module")["model"]
        event_json = json.loads(html.unescape(event_data))
        for film in event_json["Events"]:
            film_title = film["EventName"]
            film_url = f"{self.base_url}/{film['EventUrl']}"
            film_duration = film["LengthInMinutes"] * 60  # We use seconds everywhere
            film_location = f"{self.theater}: {self.address}"
            for showing in film["Schedule"]:
                film_date = self.timezone.localize(
                    datetime.fromisoformat(showing["StartDateTime"])
                )
                self.add_event(
                    summary=film_title,
                    dtstart=film_date,
                    duration=film_duration,
                    url=film_url,
                    location=film_location,
                )
