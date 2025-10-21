import pytest
from unittest import mock
from datetime import datetime, timedelta

import pytz
import requests

from filmcalendar.seattle.centralcinema import FilmCalendarCentralCinema


@pytest.fixture
def mock_response():
    """Create a mock response with sample data from Central Cinema."""
    mock_resp = mock.Mock()
    # Sample HTML response with event data structure
    mock_resp.text = '''
    <div id="event-search-list-module" model='{
        "Events": [
            {
                "EventName": "Test Movie",
                "EventUrl": "CentralCinema/e/test-movie",
                "LengthInMinutes": 120,
                "Schedule": [
                    {
                        "StartDateTime": "2025-01-01T19:00:00"
                    },
                    {
                        "StartDateTime": "2025-01-02T19:00:00"
                    }
                ]
            },
            {
                "EventName": "Private Party Rental",
                "EventUrl": "CentralCinema/e/rental",
                "LengthInMinutes": 180,
                "Schedule": [
                    {
                        "StartDateTime": "2025-01-03T19:00:00"
                    }
                ]
            }
        ]
    }'>
    </div>
    '''
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
        assert calendar.base_url == "https://www.goelevent.com"

    @mock.patch('requests.get')
    def test_fetch_films(self, mock_get, mock_response):
        # Setup
        mock_get.return_value = mock_response
        calendar = FilmCalendarCentralCinema(
            calendar_name="Test Calendar",
            theater_name="Central Cinema",
            timezone="US/Pacific",
        )
        # Execute
        calendar.fetch_films()
        # Assert
        # Only 2 events for "Test Movie", skips "Private Party Rental"
        assert len(calendar) == 2
        # Check that request was made with the correct URL and headers
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert args[0] == "https://www.goelevent.com/CentralCinema/e/List"
        assert "headers" in kwargs
        # Get the events and verify their properties
        events = list(calendar.cal.walk("vevent"))
        # Check all events are for "Test Movie"
        for event in events:
            assert event["summary"] == "Test Movie"
            url = "https://www.goelevent.com/CentralCinema/e/test-movie"
            assert event["url"] == url
            assert event["duration"].dt == timedelta(minutes=120)
            location = "Central Cinema: 1411 21st Ave., Seattle, WA 98122"
            assert event["location"] == location
        # Check the dates of the events
        tz = pytz.timezone("US/Pacific")
        expected_dates = [
            tz.localize(datetime(2025, 1, 1, 19, 0)),
            tz.localize(datetime(2025, 1, 2, 19, 0)),
        ]
        actual_dates = [event["dtstart"].dt for event in events]
        assert sorted(actual_dates) == sorted(expected_dates)

    @mock.patch('requests.get')
    def test_fetch_films_request_exception(self, mock_get):
        # Setup mock to raise exception
        mock_get.side_effect = requests.exceptions.RequestException("Test error")
        calendar = FilmCalendarCentralCinema()
        # Test that the exception is propagated
        with pytest.raises(requests.exceptions.RequestException):
            calendar.fetch_films()
