import json
from datetime import datetime, timedelta

import requests

from filmcalendar import filmcalendar


class CinemaSF(filmcalendar.FilmCalendar):
    def __init__(self, address, base_url, collection_id, **kwds):
        super().__init__(**kwds)
        self.address = address
        self.base_url = base_url
        self.collection_id = collection_id

    def __str__(self):
        return super().__str__()

    def fetch_films(self):
        month = datetime.today().strftime("%m-%Y")
        try:
            req = requests.get(
                f"{self.base_url}/api/open/GetItemsByMonth?month={month}&collectionId={self.collection_id}",
                headers=self.req_headers,
            )
        except requests.exceptions.RequestException:
            raise

        data = req.json()
        film_location = f"{self.theater}: {self.address}"
        for film in data:
            film_title = film["title"]
            film_url = f"{self.base_url}{film['fullUrl']}"
            film_start_date = datetime.fromtimestamp(film["startDate"] / 1000)
            film_end_date = datetime.fromtimestamp(film["endDate"] / 1000)
            # FIXME duration seems wonky
            film_duration = film_end_date - film_start_date

            self.add_event(
                summary=film_title,
                dtstart=self.timezone.localize(film_start_date),
                duration=film_duration,
                url=film_url,
                location=film_location,
            )
