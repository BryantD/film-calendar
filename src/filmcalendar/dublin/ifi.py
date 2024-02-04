from datetime import datetime, timedelta
from string import capwords

import requests
from bs4 import BeautifulSoup

from filmcalendar import filmcalendar


class FilmCalendarIFI(filmcalendar.FilmCalendar):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.address = "6 Eustace Street, Temple Bar, Dublin 2, D02 PD85, Ireland"
        self.base_url = "https://shop.ifi.ie/"

    def __str__(self):
        return super().__str__()

    def _fetch_film(self, film_url):
        try:
            req = requests.get(film_url, headers=self.req_headers)
        except requests.exceptions.RequestException:
            raise

        soup = BeautifulSoup(req.text, "html.parser")

        film_details_div = soup.find("div", class_="eventItemDetail")

        film_title = capwords(soup.find("h3").get_text(strip=True))
        film_location = f"{self.theater}: {self.address}"
        film_duration_string = (
            film_details_div.find("p", text=lambda t: t and t.startswith("Run Time: "))
            .get_text(strip=True)
            .split(": ")[1][:-5]
        )
        film_duration = timedelta(minutes=int(film_duration_string))

        current_date = datetime.now()

        for film_date_div in soup.find_all("div", class_="date"):
            film_date = datetime.strptime(
                film_date_div.get_text(strip=True), "%A %d %b"
            )

            # Check if the month in the date string is earlier than the current month
            if film_date.month < current_date.month:
                film_date = film_date.replace(year=current_date.year + 1)
            else:
                film_date = film_date.replace(year=current_date.year)

            film_time_div = film_date_div.next_sibling

            for film_time in film_time_div.find_all("div", class_="time"):
                film_hour, film_minute = film_time.get_text().split(":")
                film_date = film_date.replace(
                    hour=int(film_hour), minute=int(film_minute)
                )

                self.add_event(
                    summary=film_title,
                    dtstart=film_date,
                    duration=film_duration,
                    url=film_url,
                    location=film_location,
                )

    def fetch_films(self):
        try:
            req = requests.get(self.base_url, headers=self.req_headers)
        except requests.exceptions.RequestException:
            raise

        soup = BeautifulSoup(req.text, "html.parser")

        event_data = soup.find_all("div", class_="eventItem")

        for film in event_data:
            self._fetch_film(film.find("a")["href"])
