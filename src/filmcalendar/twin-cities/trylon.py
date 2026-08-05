import logging
import re
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from filmcalendar import filmcalendar

# Configure logging
logger = logging.getLogger(__name__)


class FilmCalendarTrylonCinema(filmcalendar.FilmCalendar):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.address = "2820 E 33rd St, Minneapolis, MN 55406"
        self.base_url = "https://www.trylon.org"
        self.calendar_url = f"{self.base_url}/calendar"

    def __str__(self):
        return super().__str__()

    def parse_iso_duration(self, duration_str):
        """Parse ISO 8601 duration format (e.g., PT1H45M) to timedelta."""
        if not duration_str:
            return timedelta(minutes=120)  # Default duration

        match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?", duration_str)
        if not match:
            return timedelta(minutes=120)

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        return timedelta(hours=hours, minutes=minutes)

    def parse_showtime_text(self, text):
        """Parse showtime text like 'October 21, 9:30 pm' to datetime."""
        # Handle formats like "October 21, 9:30 pm" or "November 1, 4:00 pm"
        match = re.match(r"(\w+)\s+(\d+),\s+(\d+):(\d+)\s+(am|pm)", text.strip())
        if not match:
            return None

        month_name, day, hour, minute, meridiem = match.groups()
        hour = int(hour)
        minute = int(minute)
        day = int(day)

        # Convert to 24-hour format
        if meridiem.lower() == "pm" and hour != 12:
            hour += 12
        elif meridiem.lower() == "am" and hour == 12:
            hour = 0

        # Parse month name to number
        month_map = {
            "january": 1,
            "february": 2,
            "march": 3,
            "april": 4,
            "may": 5,
            "june": 6,
            "july": 7,
            "august": 8,
            "september": 9,
            "october": 10,
            "november": 11,
            "december": 12,
        }
        month = month_map.get(month_name.lower())
        if not month:
            return None

        # Determine year (assume current year, or next year if month has passed)
        now = datetime.now()
        year = now.year
        # If the month is before current month, assume next year
        if month < now.month:
            year += 1

        try:
            dt = datetime(year, month, day, hour, minute)
            return self.timezone.localize(dt)
        except ValueError:
            return None

    def _scrape_and_save_film_page(self, film_url, headers):
        duration_minutes_re = re.compile(r"(\d+)m")
        duration_re = re.compile(
            r"^\([\d\-\u2010\u2011\u2012\u2013\u2014\u2015]{4,},.* \d+m.*\)"
        )
        film_location = f"{self.theater}: {self.address}"
        # Note: in theory Trylon does showings at the Heights, too, so keep
        # an eye on this simplification.

        try:
            logger.info(f"Fetching film page: {film_url}")
            req = requests.get(film_url, headers=headers, timeout=30)
            req.raise_for_status()
        except Exception as e:
            logger.error(f"Error fetching Trylon Cinema film page: {e}")
            raise

        soup = BeautifulSoup(req.text, "html.parser")

        film_title = soup.find("h1", class_="single-event-title").get_text()

        # Film duration is pretty non-structured so here's a lot of effort to extract it

        # The horrible regex is because Trylon film pages sometimes use en-dash as
        # opposed to a bare dash, so there's I use this horrible escaped bit to
        # catch every possible dash.
        film_duration_element = soup.find("strong", string=duration_re)
        if film_duration_element:
            film_duration_str = film_duration_element.get_text()
        else:
            # Fallback for duration is 120 minutes
            logger.info(f"Duration not found for {film_url}")
            film_duration_str = "120m"

        try:
            film_duration = timedelta(
                minutes=int(duration_minutes_re.search(film_duration_str).group(1))
            )
        except Exception as e:
            logger.error(
                f"{e} while getting duration for {film_url} from {film_duration_str}"
            )
            film_duration = timedelta(minutes=120)

        # On to showtimes
        for showtime in soup.find_all("div", class_="mt-ticket-field"):
            # As of time of coding, only one label per showtime div
            try:
                showtime_date = datetime.strptime(
                    showtime.find("label").get_text(),
                    "%a %b %d, %Y, %I:%M %p",
                    # "Sun Jul 26, 2026, 1:00 pm"
                )
                showtime_date = self.timezone.localize(showtime_date)
            except Exception as e:
                logger.error(f"Error: {e} getting showtimes from {film_url}")

            if showtime_date > self.timezone.localize(datetime.now()):
                self.add_event(
                    summary=film_title,
                    dtstart=showtime_date,
                    duration=film_duration,
                    url=film_url,
                    location=film_location,
                )

    def fetch_films(self):
        """Fetch films from Trylon."""
        headers = {
            "User-Agent": self.req_headers.get(
                "user-agent",
                "movie-calendar/1.1 (https://github.com/BryantD/film-calendar)",
            ),
        }

        # Step 1: scrape showings. The big JSON blob is not actually accurate,
        # so future me should ignore the tempting easy path.
        try:
            logger.info(f"Fetching calendar page: {self.calendar_url}")
            req = requests.get(self.calendar_url, headers=headers, timeout=30)
            req.raise_for_status()
        except Exception as e:
            logger.error(f"Error fetching Trylon Cinema calendar: {e}")
            raise

        soup = BeautifulSoup(req.text, "html.parser")

        # Find all h3.event-title -- these have title plus URL
        # and process them into film_showings, which will also
        # serve as our cache so we don't get pages twice
        # Keeping this simple since we're gonna rescrap the showtimes
        # from the individual pages anyhow, so all we need to track now
        # is the URLs
        film_pages = []
        for film_h3 in soup.find_all("h3", class_="event-title"):
            film_url = film_h3.find("a")["href"]
            # The HTML contains fully qualified URIs
            if film_url not in film_pages:
                film_pages.append(film_url)

        logger.info(f"Found {len(film_pages)} movie pages to scrape")

        # Step 2: Scrape each individual movie page
        # for movie in film_showings:
        for film_url in film_pages:
            try:
                self._scrape_and_save_film_page(film_url, headers)
            except Exception as e:
                logger.warning(f"Error scraping movie page {film_url}: {e}")
                continue
