from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from filmcalendar import filmcalendar


class FilmCalendarNWFF(filmcalendar.FilmCalendar):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.base_url = "https://nwfilmforum.org/calendar"

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

        # Convert all to seconds or set 120 minutes as the default
        try:
            dt = timedelta(
                days=int(days),
                hours=int(hours),
                minutes=int(minutes),
                seconds=int(seconds),
            )
        except ValueError:
            dt = timedelta(minutes=120)

        return dt

    def _fetch_film_page(self, start_date):
        req_payload = {"type": "film", "start": start_date.strftime("%Y-%m-%d")}
        try:
            req = requests.get(
                self.base_url,
                headers=self.req_headers,
                params=req_payload,
            )
        except requests.exceptions.RequestException:
            raise
            # This should do something more sophisticated, it's a no-op right now

        soup = BeautifulSoup(req.text, "html.parser")

        for film in soup.find_all("div", class_="calendar__item--film"):
            try:
                film_title = film.find("meta", itemprop="name")["content"]
            except TypeError as error:
                raise ValueError("Couldn't find film name") from error
            try:
                film_date_raw = film.find("meta", itemprop="startDate")["content"]
            except TypeError as error:
                raise ValueError(
                    (
                        f"Couldn't find film start time for {film_title}",
                        f" on {start_date.strftime('%Y-%m-%d')}",
                    )
                ) from error
            try:
                if film_date_raw[-1] == "T":
                    film_date_raw += "10:00:00"
                film_date = self.timezone.localize(
                    datetime.fromisoformat(film_date_raw)
                )
            except ValueError as error:
                raise ValueError(
                    f"Error parsing start time {film_date_raw} for {film_title}"
                ) from error
            try:
                film_duration = self._parse_isoduration(
                    film.find("meta", itemprop="duration")["content"]
                )
            except TypeError:
                film_duration = timedelta(minutes=120)
            try:
                film_url = film.find("meta", itemprop="mainEntityOfPage")["content"]
            except TypeError:
                film_url = None
            try:
                film_location = film.find("meta", itemprop="address")["content"]
            except TypeError:
                film_location = None
            film_location = f"{self.theater}: {film_location}"

            self.add_event(
                summary=film_title,
                dtstart=film_date,
                duration=film_duration,
                url=film_url,
                location=film_location,
            )

    def fetch_films(self):
        start_date = datetime.now(tz=self.timezone) - timedelta(
            days=datetime.now().isoweekday() - 1
        )
        end_date = start_date + timedelta(weeks=8)

        # Decision: we'll loop eight weeks into the future; I was thinking we could
        # loop until there are no films in a given week but that happens w/in a month
        # and I'd rather have a couple months of data than just a week or two

        while start_date < end_date:
            self._fetch_film_page(start_date)
            start_date = start_date + timedelta(days=7)
        return True
