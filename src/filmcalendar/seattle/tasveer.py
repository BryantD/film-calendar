import logging
import re
from datetime import datetime, timedelta

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from filmcalendar import filmcalendar

# Configure logging
logger = logging.getLogger(__name__)


class FilmCalendarTasveer(filmcalendar.FilmCalendar):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.address = "4812 Rainier Ave. S, Seattle, WA 98118"
        self.gql_query_string = """query ($date: String, $siteIds: [ID]) {
          showingsForDate(date: $date, siteIds: $siteIds) {
            data {
              id
              time
              showingId
              published
              seatsRemaining
              screenId
              showingBadgeIds
              movie {
                id
                name
                urlSlug
                synopsis
                duration
                rating
                ratingReason
                genre
                directedBy
                starring
                posterImage
                releaseDate
              }
            }
            count
          }
        }
        """
        self.query = gql(self.gql_query_string)
        self.gql_url = "https://filmcenter.tasveer.org/"
        self.headers = {
            "User-Agent": self.req_headers.get(
                "user-agent",
                f"movie-calendar/{self.__version__} (https://github.com/BryantD/film-calendar)",
            ),
            "Content-Type": "application/json",
            "Accept": "application/graphql-response+json,application/json;q=0.9",
            "site-id": "262",
            "client-type": "consumer",
            "circuit-id": "138",
            "Origin": "https://filmcenter.tasveer.org",
            "Referer": "https://filmcenter.tasveer.org/showtimes/",
        }
        self.transport = RequestsHTTPTransport(
            url=self.gql_url,
            headers=self.headers,
            verify=True,
            retries=2,
        )
        self.client = Client(
            transport=self.transport, fetch_schema_from_transport=False
        )

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

    def fetch_films(self):
        """Fetch films from Tasveer -- one day at a time but no need to get
        movie details pages"""

        # Decision: we'll loop 4 weeks into the future; that looks like about how far
        # out Tasveer's scheduling usually goes
        start_date = datetime.now(tz=self.timezone)
        end_date = start_date + timedelta(weeks=4)

        while start_date <= end_date:
            self._fetch_day_data(start_date)
            start_date = start_date + timedelta(days=1)
        return True

    def fetch_day_data(self, schedule_date):
        try:
            logger.info(f"Fetching calendar page: {self.calendar_url}")
            result = self.client.execute(
                self.query, variable_values={"date": schedule_date, "siteIds": [262]}
            )

        except Exception as e:
            logger.error(f"Error fetching Tasveer GQL: {e}")
            raise

        # Iterate over movies. Unnecessary two step because I want to
        # process the data a bit.

        for showing in result["showingsForDate"]["data"]:
            # Tasveer returns movie titles like
            # "Disclosure Day (2026, English, USA)"

            film_title = showing["movie"]["name"]
            film_date = datetime.fromtimestamp(showing["time"])
            film_duration = timedelta(minutes=showing["movie"]["duration"])
            film_url = (
                f"https://filmcenter.tasveer.org/movie/{showing['movie']['urlSlug']}"
            )

            self.add_event(
                summary=film_title,
                dtstart=film_date,
                duration=film_duration,
                url=film_url,
                location=self.address,
            )

            print(film_title)
            print(film_date)
            print(film_duration)
            print(film_url)
