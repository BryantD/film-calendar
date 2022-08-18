from . import filmcalendar

from icalendar import Calendar, Event
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz


class FilmCalendarSIFF(filmcalendar.FilmCalendar):
    def __init__(self):
        super().__init__()
        self.theater = "SIFF"
        self.base_url = "https://www.siff.net/"
        self.addresses = {
            "Egyptian": "805 E. Pine St, Seattle, WA, 98122",
            "Film Center": "305 Harrison St, Seattle, WA 98109",
            "Uptown": "511 Queen Anne Ave N, Seattle, WA 98109",
        }

    def __str__(self):
        return super().__str__()

    def _parse_duration(self, duration_raw):
        # Return duration in seconds -- format is "120 min."
        if duration_raw[-4:] == "min.":
            return int(duration_raw[:-5]) * 60
        else:
            return 120 * 60

    def _fetch_film_page(self, date):
        req_payload = {"type": "view", "list": start_date.strftime("%Y-%m-%d")}
        try:
            req = requests.get(
                "https://www.siff.net/calendar",
                headers=self.req_headers,
                params=req_payload,
            )
        except requests.exceptions.RequestException as e:
            raise
            # This should do something more sophisticated, it's a no-op right now

        soup = BeautifulSoup(req.text, "html.parser")

        listings = soup.find("div", class_="listing")
        for film in listings.find("div", class_="item"):
            self.add_event(
                summary=film_title,
                dtstart=film_date,
                duration=film_duration,
                url=film_url,
                location=film_location,
            )

    def fetch_films(self):
        start_date = datetime.now() - timedelta(days=datetime.now().isoweekday() - 1)
        end_date = start_date + timedelta(weeks=5)

        # Decision: we'll loop 5 weeks into the future; that looks like about how far
        # out SIFF's scheduling goes

        while start_date < end_date:
            self._fetch_film_page(start_date)
            start_date = start_date + timedelta(days=1)
        return True


