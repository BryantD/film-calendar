import html
import json
import logging
from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from filmcalendar import filmcalendar

# Configure logging
logger = logging.getLogger(__name__)

# Try to import curl_cffi first (better browser impersonation)
# Fall back to requests if curl_cffi is not available
try:
    from curl_cffi import requests as curl_requests

    USE_CURL_CFFI = True
except ImportError:
    import requests

    USE_CURL_CFFI = False
    logger.warning(
        "curl_cffi not available, using standard requests. "
        "For better anti-bot protection bypass, install curl_cffi: "
        "pip install curl_cffi"
    )


class FilmCalendarCentralCinema(filmcalendar.FilmCalendar):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.address = "1411 21st Ave., Seattle, WA 98122"
        self.base_url = "https://www.goelevent.com"

    def __str__(self):
        return super().__str__()

    def fetch_films(self):
        req_payload = {"t": "", "s": "", "v": "", "st": "null"}
        url = f"{self.base_url}/CentralCinema/e/List"

        # Enhanced headers to better mimic a real browser
        headers = {
            "User-Agent": self.req_headers.get(
                "user-agent",
                "movie-calendar/1.1 (https://github.com/BryantD/film-calendar)",
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
        }

        try:
            if USE_CURL_CFFI:
                # Use curl_cffi with browser impersonation for better anti-bot bypass
                logger.info("Using curl_cffi with Chrome impersonation")
                req = curl_requests.get(
                    url,
                    params=req_payload,
                    headers=headers,
                    impersonate="chrome131",
                    timeout=30,
                )
            else:
                # Fallback to standard requests
                logger.info("Using standard requests library")
                req = requests.get(
                    url,
                    params=req_payload,
                    headers=headers,
                    timeout=30,
                )

            # Check for common anti-bot responses
            if req.status_code == 403:
                logger.error(
                    f"Access denied (403) by {self.base_url}. "
                    "The website may be blocking automated access. "
                    "This could be due to anti-bot protection. "
                    "Try installing curl_cffi (pip install curl_cffi) for "
                    "better browser impersonation."
                )
                raise RuntimeError(
                    f"Central Cinema scraper blocked by anti-bot protection "
                    f"(HTTP 403). The website at {self.base_url} is denying "
                    f"access to automated requests."
                )

            req.raise_for_status()

        except Exception as e:
            logger.error(f"Error fetching Central Cinema events: {e}")
            raise

        soup = BeautifulSoup(req.text, "html.parser")

        # Find the event data element
        event_data_elem = soup.find("div", id="event-search-list-module")

        if not event_data_elem:
            logger.error(
                "Could not find event-search-list-module div. "
                "The website structure may have changed."
            )
            raise ValueError(
                "Failed to parse Central Cinema website: "
                "event-search-list-module not found. "
                "The website structure may have changed."
            )

        if not event_data_elem.get("model"):
            logger.error(
                "event-search-list-module div found but has no 'model' attribute. "
                "The website structure may have changed."
            )
            raise ValueError(
                "Failed to parse Central Cinema website: model attribute not found. "
                "The website structure may have changed."
            )

        try:
            event_data = event_data_elem["model"]
            event_json = json.loads(html.unescape(event_data))
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing event JSON data: {e}")
            raise ValueError(f"Failed to parse Central Cinema event data: {e}")

        if "Events" not in event_json:
            logger.warning("No 'Events' key found in parsed JSON")
            return

        events_count = len(event_json["Events"])
        logger.info(f"Successfully fetched {events_count} events from Central Cinema")

        for film in event_json["Events"]:
            try:
                film_title = film["EventName"]
                film_url = f"{self.base_url}/{film['EventUrl']}"
                film_duration = timedelta(minutes=film["LengthInMinutes"])
                film_location = f"{self.theater}: {self.address}"

                for showing in film["Schedule"]:
                    film_date = self.timezone.localize(
                        datetime.fromisoformat(showing["StartDateTime"])
                    )
                    if film_title != "Private Party Rental":
                        # Hardcoding a skip for rental slots
                        self.add_event(
                            summary=film_title,
                            dtstart=film_date,
                            duration=film_duration,
                            url=film_url,
                            location=film_location,
                        )
            except (KeyError, ValueError) as e:
                logger.warning(
                    f"Error processing film '{film.get('EventName', 'unknown')}': {e}"
                )
                continue
