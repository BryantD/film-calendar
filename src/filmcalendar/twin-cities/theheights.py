import logging
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from filmcalendar import filmcalendar

# Configure logging
logger = logging.getLogger(__name__)


class FilmCalendarTheHeightsTheater(filmcalendar.FilmCalendar):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.address = "3951 Central Ave NE, Columbia Heights, MN 55421"
        self.base_url = "https://www.heightstheater.com"
        self.calendar_url = f"{self.base_url}/calendar"

    def __str__(self):
        return super().__str__()

    def _scrape_and_save_film_page(self, film_url, headers):
        film_location = f"{self.theater}: {self.address}"

        try:
            logger.info(f"Fetching film page: {film_url}")
            req = requests.get(film_url, headers=headers, timeout=30)
            req.raise_for_status()
        except Exception as e:
            logger.error(f"Error fetching Heights Theater film page: {e}")
            raise

        soup = BeautifulSoup(req.text, "html.parser")

        film_title = soup.find("h1").get_text()

        runtime_span = soup.find("label", string="Run Time: ")
        try:
            runtime_string = runtime_span.next_sibling.get_text().split()[0]
            film_duration = timedelta(minutes=int(runtime_string))
        except Exception as e:
            logger.error(f"Error: {e} parsing showtime from {film_url}")

        # On to showtimes -- beautiful HTML here, thanks Heights
        for showtime in soup.find_all("time"):
            try:
                showtime_date = datetime.strptime(
                    showtime["datetime"],
                    "%Y-%m-%d %H:%M",
                    # 2026-09-19 13:30
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
        """Fetch films from The Heights."""
        headers = {
            "User-Agent": self.req_headers.get(
                "user-agent",
                "movie-calendar/1.6.0 (https://github.com/BryantD/film-calendar)",
            ),
        }

        # Step 1: scrape showings -- current month and next month
        today = datetime.today()
        year = today.year
        month = today.strftime("%B").lower()

        try:
            logger.info(f"Fetching calendar page: {self.calendar_url}/{month}/{year}")
            req = requests.get(self.calendar_url, headers=headers, timeout=30)
            req.raise_for_status()
        except Exception as e:
            logger.error(f"Error fetching Heights calendar: {e}")
            raise

        # Narrow the soup down to the main tag first to avoid random
        # navigational h3s
        soup = BeautifulSoup(req.text, "html.parser")
        main_soup = soup.find("main")

        # Find all h3 tags within div class=calendar-listing -- these have title
        # plus URL and process them into film_showings, which will also serve as
        # our cache so we don't get pages twice Keeping this simple since we're
        # gonna rescrap the showtimes from the individual pages anyhow, so all
        # we need to track now is the URLs
        film_pages = []
        for film_h3 in main_soup.find_all("h3"):
            film_url = f"{self.base_url}{film_h3.find("a")["href"]}"
            # The HTML contains unqualified URIs
            if film_url not in film_pages:
                film_pages.append(film_url)

        logger.info(f"Found {len(film_pages)} movie pages to scrape")

        # Step 2: Scrape each individual movie page
        for film_url in film_pages:
            try:
                self._scrape_and_save_film_page(film_url, headers)
            except Exception as e:
                logger.warning(f"Error scraping movie page {film_url}: {e}")
                continue
