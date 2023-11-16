import html
import json
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from filmcalendar import filmcalendar


class FilmCalendarSIFF(filmcalendar.FilmCalendar):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.addresses = {
            "SIFF Cinema Egyptian": "805 E. Pine St, Seattle, WA 98122",
            "SIFF Film Center": "305 Harrison St, Seattle, WA 98109",
            "SIFF Cinema Uptown": "511 Queen Anne Ave N, Seattle, WA 98109",
            "SIFF Cinema Downtown": "2100 4th Ave, Seattle, WA 98121",
            # Following locations are for SIFF 2023
            "Paramount Theatre": "911 Pine St, Seattle, WA 98101",
            "AMC Pacific Place": "600 Pine St #400, Seattle, WA 98101",
            "Ark Lodge Cinemas": "4816 Rainier Ave S, Seattle, WA 98118",
            "Shoreline Community College": "16101 Greenwood Ave N. (Building 1600), Shoreline, WA 98133",  # NOQA
        }
        self.base_url = "https://www.siff.net"

    def __str__(self):
        return super().__str__()

    def _fetch_film_page(self, date):
        req_payload = {"view": "list", "date": date.strftime("%Y-%m-%d")}
        try:
            req = requests.get(
                f"{self.base_url}/calendar",
                headers=self.req_headers,
                params=req_payload,
            )
        except requests.exceptions.RequestException:
            raise
            # This should do something more sophisticated, it's a no-op right now

        soup = BeautifulSoup(req.text, "html.parser")

        if listings := soup.find("div", class_="listing thumbs"):
            for film in listings.find_all("div", class_="item"):
                film_anchor = film.find("div", class_="small-copy").find("h3").find("a")
                film_title = film_anchor.get_text().strip()
                film_url = f"{self.base_url}{film_anchor['href']}"

                film_times = film.find("div", class_="times")
                try:
                    film_theater = (
                        film_times.find("span", class_="dark-gray-text")
                        .get_text()
                        .strip()
                    )
                    film_location = f"{self.theater}: {self.addresses[film_theater]}"
                except AttributeError:
                    break
                for screening in film.find_all("a", class_="elevent"):
                    event_json = json.loads(html.unescape(screening["data-screening"]))
                    film_duration = timedelta(minutes=event_json["LengthInMinutes"])
                    film_date = datetime.fromtimestamp(
                        int(event_json["Showtime"][6:-2]) / 1000, self.timezone
                    )

                    self.add_event(
                        summary=film_title,
                        dtstart=film_date,
                        duration=film_duration,
                        url=film_url,
                        location=film_location,
                    )

    def fetch_films(self):
        start_date = datetime.now(tz=self.timezone)
        end_date = start_date + timedelta(weeks=5)

        # Decision: we'll loop 5 weeks into the future; that looks like about how far
        # out SIFF's scheduling goes
        while start_date < end_date:
            self._fetch_film_page(start_date)
            start_date = start_date + timedelta(days=1)
        return True
