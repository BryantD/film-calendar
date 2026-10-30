import json
import logging
import re
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from filmcalendar import filmcalendar

# Configure logging
logger = logging.getLogger(__name__)


class FilmCalendarCentralCinema(filmcalendar.FilmCalendar):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.address = "1411 21st Ave., Seattle, WA 98122"
        self.base_url = "https://www.central-cinema.com"
        self.calendar_url = f"{self.base_url}/calendar"

    def __str__(self):
        return super().__str__()

    def parse_iso_duration(self, duration_str):
        """Parse ISO 8601 duration format (e.g., PT1H45M) to timedelta."""
        if not duration_str:
            return timedelta(minutes=90)  # Default duration

        match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?", duration_str)
        if not match:
            return timedelta(minutes=90)

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        return timedelta(hours=hours, minutes=minutes)

    def parse_showtime_text(self, text):
        """Parse showtime text like 'Sunday, October 21, 2026, 9:30 pm' to datetime."""
        match = re.match(
            r"(\w+),\s+(\w+)\s+(\d+),\s(\d+),\s+(\d+):(\d+)\s+(am|pm)",
            text.strip(),
        )
        if not match:
            return None

        weekday, month_name, day, year, hour, minute, meridiem = match.groups()
        hour = int(hour)
        minute = int(minute)
        day = int(day)
        year = int(year)

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

        # # Determine year (assume current year, or next year if month has passed)
        # now = datetime.now()
        # year = now.year
        # # If the month is before current month, assume next year
        # if month < now.month:
        #     year += 1

        try:
            dt = datetime(year, month, day, hour, minute)
            return self.timezone.localize(dt)
        except ValueError:
            return None

    def fetch_films(self):
        """Fetch films from Central Cinema using a two-step scraping process."""
        headers = {
            "User-Agent": self.req_headers.get(
                "user-agent",
                "movie-calendar/1.1 (https://github.com/BryantD/film-calendar)",
            ),
        }

        # Step 1: Get all movie URLs from the calendar page
        try:
            logger.info(f"Fetching calendar page: {self.calendar_url}")
            req = requests.get(self.calendar_url, headers=headers, timeout=30)
            req.raise_for_status()
        except Exception as e:
            logger.error(f"Error fetching Central Cinema calendar: {e}")
            raise

        soup = BeautifulSoup(req.text, "html.parser")

        # Find all links that contain /movie/ in the href
        movie_links = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "/movie/" in href:
                # Convert relative URLs to absolute
                if href.startswith("/"):
                    full_url = f"{self.base_url}{href}"
                elif href.startswith("http"):
                    full_url = href
                else:
                    continue

                if full_url not in movie_links:
                    movie_links.append(full_url)

        logger.info(f"Found {len(movie_links)} movie pages to scrape")

        # Step 2: Scrape each individual movie page
        for movie_url in movie_links:
            if not "private-rental-event" in movie_url:
                try:
                    self._scrape_movie_page(movie_url, headers)
                except Exception as e:
                    logger.warning(f"Error scraping movie page {movie_url}: {e}")
                    continue

    def _scrape_movie_page(self, url, headers):
        """Scrape an individual movie page for showtime data."""
        logger.info(f"Scraping movie page: {url}")

        try:
            req = requests.get(url, headers=headers, timeout=30)
            req.raise_for_status()
        except Exception as e:
            logger.warning(f"Error fetching movie page {url}: {e}")
            return

        soup = BeautifulSoup(req.text, "html.parser")

        # Extract JSON-LD structured data
        json_ld_scripts = soup.find_all("script", type="application/ld+json")
        movie_data = None

        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                # Look for Movie schema
                if isinstance(data, dict) and (
                    data.get("@type") == "Movie" or data.get("@type") == "MovieTheater"
                ):
                    movie_data = data
                    break
            except (json.JSONDecodeError, AttributeError):
                continue

        if not movie_data:
            logger.warning(f"No parsable JSON-LD movie data found on {url}")
            # Try to get title from page as fallback
            title_tag = soup.find("h1")
            film_title = title_tag.get_text(strip=True) if title_tag else "Unknown Film"
            film_duration = timedelta(minutes=90)  # Default
        else:
            film_title = movie_data.get("name", "Unknown Film")
            duration_str = movie_data.get("duration", "")
            film_duration = self.parse_iso_duration(duration_str)

        # Find all showtime links -- first iterate through the h3 tags
        # This feels a bit fragile but I don't think I can count on the random
        # classes to stay associated with days
        h3_tags = soup.find_all("h3")
        for day in h3_tags:
            day_string = day.get_text(strip=True)

            showtime_links = day.parent.find_all(
                "a", href=re.compile(r"/checkout/showing/")
            )

            if not showtime_links:
                logger.debug(f"No showtimes found for {film_title} on {day}")
                next

            logger.info(f"Processing {len(showtime_links)} showtimes for {film_title}")
            for link in showtime_links:
                showtime_text = day_string + ", " + link.get_text(strip=True)
                showtime_dt = self.parse_showtime_text(f"{showtime_text}")
                if showtime_dt:
                    self.add_event(
                        summary=film_title,
                        dtstart=showtime_dt,
                        duration=film_duration,
                        url=url,
                        location=f"{self.theater}: {self.address}",
                    )
                else:
                    logger.warning(f"Could not parse showtime: {showtime_text}")
