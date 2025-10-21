from datetime import datetime, timedelta
from unittest import mock

import pytest
import pytz
import requests

from filmcalendar.seattle.centralcinema import FilmCalendarCentralCinema


@pytest.fixture
def mock_calendar_response():
    """Create a mock calendar page response."""
    mock_resp = mock.Mock()
    mock_resp.status_code = 200
    mock_resp.text = """
    <html>
        <body>
            <a href="/movie/test-movie">Test Movie</a>
            <a href="/movie/test-movie-2">Test Movie 2</a>
            <a href="/other-page">Other Link</a>
        </body>
    </html>
    """
    return mock_resp


@pytest.fixture
def mock_movie_response():
    """Create a mock movie page response with JSON-LD and showtimes."""
    mock_resp = mock.Mock()
    mock_resp.status_code = 200
    mock_resp.text = """
    <html>
        <head>
            <script type="application/ld+json">
            {
                "@type": "Movie",
                "name": "Test Movie",
                "duration": "PT2H0M"
            }
            </script>
        </head>
        <body>
            <h2><a href="/checkout/showing/test/1">January 1, 7:00 pm</a></h2>
            <h2><a href="/checkout/showing/test/2">January 2, 7:00 pm</a></h2>
        </body>
    </html>
    """
    return mock_resp


class TestCentralCinema:
    def test_init(self):
        calendar = FilmCalendarCentralCinema(
            calendar_name="Test Calendar",
            theater_name="Central Cinema",
            timezone="US/Pacific",
            site_url="https://example.com",
        )
        assert calendar.calendar_name == "Test Calendar"
        assert calendar.theater == "Central Cinema"
        assert calendar.timezone_string == "US/Pacific"
        assert calendar.address == "1411 21st Ave., Seattle, WA 98122"
        assert calendar.base_url == "https://www.central-cinema.com"
        assert calendar.calendar_url == "https://www.central-cinema.com/calendar"

    @mock.patch("requests.get")
    def test_fetch_films(self, mock_get, mock_calendar_response, mock_movie_response):
        # Setup - mock returns calendar page first, then movie pages
        mock_get.side_effect = [
            mock_calendar_response,  # First call gets calendar
            mock_movie_response,  # Second call gets first movie
            mock_movie_response,  # Third call gets second movie
        ]
        calendar = FilmCalendarCentralCinema(
            calendar_name="Test Calendar",
            theater_name="Central Cinema",
            timezone="US/Pacific",
        )
        # Execute
        calendar.fetch_films()
        # Assert
        # Should have 4 events total (2 movies × 2 showtimes each)
        assert len(calendar) == 4
        # Check that requests were made
        assert mock_get.call_count == 3
        # Get the events and verify their properties
        events = list(calendar.cal.walk("vevent"))
        # Check all events are for "Test Movie"
        for event in events:
            assert event["summary"] == "Test Movie"
            assert "/movie/test-movie" in str(event["url"])
            assert event["duration"].dt == timedelta(hours=2)
            location = "Central Cinema: 1411 21st Ave., Seattle, WA 98122"
            assert event["location"] == location
        # Check the dates of the events (2 movies, each with same 2 showtimes)
        tz = pytz.timezone("US/Pacific")
        expected_dates = [
            tz.localize(
                datetime(2026, 1, 1, 19, 0)
            ),  # Year 2026 because Jan is before current Oct
            tz.localize(datetime(2026, 1, 2, 19, 0)),
            tz.localize(datetime(2026, 1, 1, 19, 0)),
            tz.localize(datetime(2026, 1, 2, 19, 0)),
        ]
        actual_dates = [event["dtstart"].dt for event in events]
        assert sorted(actual_dates) == sorted(expected_dates)

    @mock.patch("requests.get")
    def test_fetch_films_request_exception(self, mock_get):
        # Setup mock to raise exception
        mock_get.side_effect = requests.exceptions.RequestException("Test error")
        calendar = FilmCalendarCentralCinema()
        # Test that the exception is propagated
        with pytest.raises(requests.exceptions.RequestException):
            calendar.fetch_films()
