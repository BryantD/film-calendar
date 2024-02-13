import json
import re
from datetime import datetime, timedelta

import requests

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
            base_location = film["taxonomy"][0]
            film_title = film["event_title"]
            film_location = (
                f"{base_location.capitalize()}: {self.addresses[base_location]}"
            )
            film_url = (
                self.base_url + "/events/" + base_location + "/" + film["event_slug"]
            )
            film["date"] = re.sub(r"(\d)(st|nd|rd|th)", r"\1", film["date"])
            film_date = datetime.strptime(
                f"{film['date']} {film['time']}",
                "%A, %B %d, %Y %I:%M %p",
            )
            film_date = film_date.replace(tzinfo=self.timezone)

            self.add_event(
                summary=film_title,
                dtstart=film_date,
                duration=film_duration,
                url=film_url,
                location=film_location,
            )
