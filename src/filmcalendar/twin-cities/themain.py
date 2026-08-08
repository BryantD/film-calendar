import json
import logging
import re
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from filmcalendar import filmcalendar

# Configure logging
logger = logging.getLogger(__name__)


class FilmCalendarTheMainCinema(filmcalendar.FilmCalendar):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.address = "115 SE Main Street, Minneapolis, MN 55414"
        self.base_url = "https://mspfilm.org"
        self.calendar_api_url = f"{self.base_url}/wp-json/gecko-theme/v1/show-list"

    def __str__(self):
        return super().__str__()

    def _scrape_and_save_film_page(self, film_url, headers):
        film_location = f"{self.theater}: {self.address}"
        clean_date_re = re.compile(r"(\d+)(?:st|nd|rd|th)\b", re.I)

        try:
            logger.info(f"Fetching film page: {film_url}")
            req = requests.get(film_url, headers=headers, timeout=30)
            req.raise_for_status()
        except Exception as e:
            logger.error(f"Error fetching Main Cinema film page: {e}")
            raise

        soup = BeautifulSoup(req.text, "html.parser")

        film_title = (
            soup.find("h1", class_="gecko-single-show__title").get_text().strip()
        )

        # Assuming the "XXX min" format is consistent here.
        film_duration_element = soup.find("span", string="Runtime:").find_next_sibling()

        if film_duration_element:
            film_duration_str = film_duration_element.get_text()
        else:
            # Fallback for duration is 120 minutes
            logger.info(f"Duration not found for {film_url}")
            film_duration_str = "120 min"
        try:
            film_duration = timedelta(minutes=int(film_duration_str[:-3]))
        except ValueError:
            logger.info(f"{film_duration_str} could not be converted to int")
            film_duration = timedelta(minutes=120)

        # On to showtimes
        current_year = datetime.now(tz=self.timezone).year
        for showtime_day in soup.find_all("div", class_="gecko-show-events__day"):
            date_str = showtime_day.find(
                "h3", class_="gecko-show-events__date"
            ).get_text()
            date_str = clean_date_re.sub(r"\1", f"{date_str} {current_year}")

            for showtime_time in showtime_day.find_all(
                "button", class_="gecko-show-events__showtime"
            ):
                time_str = showtime_time.get_text().strip()

                try:
                    showtime_date = datetime.strptime(
                        f"{date_str} {time_str}",
                        "%A, %B %d %Y %I:%M %p",
                        # "Saturday, August 8th 2026 3:40 pm"
                    )
                    showtime_date = self.timezone.localize(showtime_date)
                except Exception as e:
                    logger.error(f"Error: {e} getting showtimes from {film_url}")

                self.add_event(
                    summary=film_title,
                    dtstart=showtime_date,
                    duration=film_duration,
                    url=film_url,
                    location=film_location,
                )

    def _fetch_film_group(self, headers, group):
        """Fetch now playing or coming soon using the WP API"""
        group_url = f"{self.calendar_api_url}?page={group}"
        print(f"scraping {group_url}")
        try:
            logger.info(f"Fetching calendar page: {group_url}")
            req = requests.get(group_url, headers=headers, timeout=30)
            req.raise_for_status()
        except Exception as e:
            logger.error(f"Error fetching Main Cinema calendar: {e}")
            raise

        film_data = json.loads(req.text)
        return list(map(lambda x: x["permalink"], film_data["shows"]))

    def fetch_films(self):
        """Fetch films from Main Cinema."""
        headers = {
            "User-Agent": self.req_headers.get(
                "user-agent",
                "movie-calendar/1.1 (https://github.com/BryantD/film-calendar)",
            ),
        }

        # Step 1: scrape showings. This breaks down into now showing plus
        # upcoming and we need to use the WP API since the page is built
        # dynamically: ?page=now-showing or ?page=coming-soon
        film_pages = []
        film_pages.extend(self._fetch_film_group(headers, "now-showing"))
        # FIX ME: uncomment
        # film_pages.extend(self._fetch_film_group(headers, "coming-soon"))
        logger.info(f"Found {len(film_pages)} movie pages to scrape")

        # Step 2: Scrape each individual movie page
        # for movie in film_showings:
        for film_url in film_pages:
            try:
                self._scrape_and_save_film_page(film_url, headers)
            except Exception as e:
                logger.warning(f"Error scraping movie page {film_url}: {e}")
                continue
