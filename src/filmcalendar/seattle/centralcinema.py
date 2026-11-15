import json
import logging
from datetime import datetime, timedelta

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from filmcalendar import filmcalendar

# Configure logging
logger = logging.getLogger(__name__)


class FilmCalendarCentralCinema(filmcalendar.FilmCalendar):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.address = "1411 21st Ave., Seattle, WA 98122"
        self.base_url = "https://www.central-cinema.com"
        self.gql_url = f"{self.base_url}/graphql"
        self.gql_headers = {
            "User-Agent": self.req_headers.get(
                "user-agent",
                "movie-calendar/1.1 (https://github.com/BryantD/film-calendar)",
            ),
            "site-id": "275",
            "client-type": "consumer",
        }

    def __str__(self):
        return super().__str__()

    def fetch_films(self):
        """Fetch films from Central Cinema via GQL."""

        # Decision: we're going four weeks into the future. Central Cinema
        # sometimes schedules further in the future but I'd rather be a bit
        # conservative.
        start_date = datetime.now(tz=self.timezone)
        end_date = start_date + timedelta(weeks=4)

        while start_date < end_date:
            self._fetch_gql_for_date(start_date.isoformat())
            start_date = start_date + timedelta(days=1)
        return True

    def _fetch_gql_for_date(self, date):
        transport = RequestsHTTPTransport(url=self.gql_url, headers=self.gql_headers)
        client = Client(transport=transport, fetch_schema_from_transport=False)

        # Every showing at the theater on one (local) date, movie included
        SHOWINGS_FOR_DATE = gql("""
        query ShowingsForDate($date: String, $movieId: ID) {
          showingsForDate(date: $date, movieId: $movieId) {
            data {
              id
              time
              past
              published
              seatsRemaining
              movie { id name urlSlug duration rating }
            }
            count
          }
        }
        """)

        logger.info(f"Fetching showings for: {date}")
        SHOWINGS_FOR_DATE.variable_values = {"date": date}  # omit movieId for all films
        movies = client.execute(SHOWINGS_FOR_DATE)

        for movie in movies["showingsForDate"]["data"]:
            logger.info(f"Adding: {movie['movie']['name']}")
            if not movie["past"] and movie["published"]:
                self.add_event(
                    summary=movie["movie"]["name"],
                    dtstart=datetime.fromisoformat(movie["time"]),
                    duration=timedelta(minutes=movie["movie"]["duration"]),
                    url=f"{self.base_url}/movie/{movie['movie']['urlSlug']}/",
                    location=f"{self.theater}: {self.address}",
                )
            else:
                logger.info(
                    f"Skipped {movie['movie']['name']}: past = {movie['past']}, published = {movie['published']}"
                )
        return
