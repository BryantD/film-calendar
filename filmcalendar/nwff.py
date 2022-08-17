from . import filmcalendar 

from icalendar import Calendar, Event
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz

class FilmCalendarNWFF(filmcalendar.FilmCalendar):
    def __init__(self):
        super().__init__()
        self.theater = "Northwest Film Forum"
        
    def __str__(self):
        return super().__str__()

    def _get_isosplit(self, s, split):
        if split in s:
            n, s = s.split(split)
        else:
            n = 0
        return n, s

    def _parse_isoduration(self, s):

        # Remove prefix
        s = s.split("P")[-1]

        # Step through letter dividers
        days, s = self._get_isosplit(s, "D")
        _, s = self._get_isosplit(s, "T")
        hours, s = self._get_isosplit(s, "H")
        minutes, s = self._get_isosplit(s, "M")
        seconds, s = self._get_isosplit(s, "S")

        # Convert all to seconds
        dt = timedelta(
            days=int(days), hours=int(hours), minutes=int(minutes), seconds=int(seconds)
        )
        return int(dt.total_seconds())

    def fetch_films(self):
        req_payload = {'type': 'film', 'attributes': ''}
        try:
            req = requests.get('https://nwfilmforum.org/calendar', headers=self.req_headers, params=req_payload)
        except requests.exceptions.RequestException as e:
            raise

        soup = BeautifulSoup(req.text, 'html.parser')


        for day in soup.find_all("div", class_="calendar__grid__col"):
            date = day["data-id"]
            for film in day.find_all("div", class_="calendar__item--film"):
                try:
                    film_title = film.find("meta", itemprop="name")["content"]
                except TypeError as error:
                    raise ValueError("Couldn't find film name") from error
                try:
                    film_date = self.timezone.localize(datetime.fromisoformat(film.find("meta", itemprop="startDate")["content"]))
                except TypeError as error:
                        raise ValueError("Couldn't find film start time") from error
                try:
                    film_duration = self._parse_isoduration(film.find("meta", itemprop="duration")["content"])
                except TypeError as error:
                    film_duration = 120 * 60 
                try:
                    film_url = film.find("meta", itemprop="mainEntityOfPage")["content"]
                except TypeError as error:
                    film_url = None
                try:
                    film_location = film.find("meta", itemprop="address")["content"]
                except TypeError as error:
                    film_location = None

                self.add_event(summary=film_title, dtstart=film_date, duration=film_duration, url=film_url, location=film_location)