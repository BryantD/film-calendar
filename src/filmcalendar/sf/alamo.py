import json
from datetime import datetime, timedelta

import requests

from filmcalendar import filmcalendar


class FilmCalendarAlamoDrafthouseNewMission(filmcalendar.FilmCalendar):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.address = "2250 Misson St, San Francisco, CA 94110"
        self.base_url = "https://drafthouse.com/sf"

    def __str__(self):
        return super().__str__()

    def fetch_films(self):
        try:
            req = requests.get(
                "https://drafthouse.com/s/mother/v2/schedule/market/sf",
                headers=self.req_headers,
            )
        except requests.exceptions.RequestException:
            raise

        data = req.json()["data"]
        for film in data["presentations"]:
            film_title = film["show"]["title"]
            film_url = f"{self.base_url}/show/{film['slug']}"
            if film["event"] and film["event"]["runtimeMinutes"]:
                film_duration = timedelta(minutes=film["event"]["runtimeMinutes"])
            else:
                # FIXME we need to scrape the duration from the show page
                film_duration = timedelta(minutes=120)
            film_location = f"{self.theater}: {self.address}"
            for showing in data["sessions"]:
                if showing["presentationSlug"] != film["slug"]:
                    continue
                film_date = self.timezone.localize(
                    datetime.fromisoformat(showing["showTimeClt"])
                )
                self.add_event(
                    summary=film_title,
                    dtstart=film_date,
                    duration=film_duration,
                    url=film_url,
                    location=film_location,
                )
