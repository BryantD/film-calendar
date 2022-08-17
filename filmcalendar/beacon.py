from . import filmcalendar 

from icalendar import Calendar, Event
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz

class FilmCalendarBeacon(filmcalendar.FilmCalendar):
    def __init__(self):
        super().__init__()
        self.theater = "The Beacon"
        
    def __str__(self):
        return super().__str__()

    def fetch_films(self):
        try:
            req = requests.get('https://thebeacon.film/calendar', headers=self.req_headers)
        except requests.exceptions.RequestException as e:
            raise

        soup = BeautifulSoup(req.text, 'html.parser')

        for day in soup.find_all("section", class_="calendarCell"):
            for film in day.find_all("section", class_="showtime"):
                try:
                    film_title = film.find("section", itemprop="name").get_text().title()
                except TypeError as error:
                    raise ValueError("Couldn't find film name") from error
                if film_title != "Rent The Beacon":
                    # Hardcoding a skip for rental slots
                    try:
                        film_date = self.timezone.localize(datetime.fromisoformat(film.find("section", itemprop="startDate")["content"]))
                    except TypeError as error:
                            raise ValueError("Couldn't find film start time") from error     
                    try:
                        film_url = film.find("a")["href"]
                    except TypeError as error:
                        film_url = None
                    try:
                        film_street = film.find("span", itemprop="streetAddress").get_text()
                        film_city = film.find("span", itemprop="addressLocality").get_text()
                        film_state = film.find("span", itemprop="addressRegion").get_text()
                        film_zip = film.find("span", itemprop="postalCode").get_text()
                        film_location = f"{self.theater}: {film_street}, {film_city}, {film_state} {film_zip}"
                    except TypeError as error:
                        film_location = self.theater
                    film_duration = 120 * 60

                    self.add_event(summary=film_title, dtstart=film_date, duration=film_duration, url=film_url, location=film_location)