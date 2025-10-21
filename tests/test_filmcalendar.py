import os
import tempfile
from datetime import datetime, timedelta

import pytest
import pytz

from filmcalendar import FilmCalendar


@pytest.fixture
def film_calendar():
    return FilmCalendar(
        calendar_name="Test Calendar",
        theater_name="Test Theater",
        timezone="US/Pacific",
        site_url="https://example.com",
    )


class TestFilmCalendar:
    def test_init(self, film_calendar):
        assert film_calendar.calendar_name == "Test Calendar"
        assert film_calendar.theater == "Test Theater"
        assert film_calendar.timezone_string == "US/Pacific"
        assert film_calendar.site_url == "https://example.com"
        assert film_calendar.req_headers == {
            "user-agent": "movie-calendar/1.1 (https://example.com)"
        }
        assert str(film_calendar.timezone) == "US/Pacific"

    def test_init_invalid_timezone(self):
        with pytest.raises(pytz.exceptions.UnknownTimeZoneError):
            FilmCalendar(timezone="Invalid/Timezone")

    def test_str(self, film_calendar):
        cal_string = str(film_calendar)
        assert "BEGIN:VCALENDAR" in cal_string
        assert "VERSION:2.0" in cal_string
        assert "PRODID:-//Test Calendar//NONSGML Event Calendar//EN" in cal_string
        assert "X-WR-CALNAME:Test Calendar" in cal_string
        assert "X-WR-TIMEZONE:US/Pacific" in cal_string
        assert "END:VCALENDAR" in cal_string

    def test_len_empty(self, film_calendar):
        assert len(film_calendar) == 0

    def test_add_event(self, film_calendar):
        tz = pytz.timezone("US/Pacific")
        start_time = tz.localize(datetime(2025, 1, 1, 19, 0))
        film_calendar.add_event(
            summary="Test Film",
            dtstart=start_time,
            url="https://example.com/film",
            duration=timedelta(minutes=90),
            location="Test Theater: 123 Main St",
        )
        assert len(film_calendar) == 1
        # Get the event and verify its properties
        event = next(film_calendar.cal.walk("vevent"))
        assert event["summary"] == "Test Film"
        assert event["dtstart"].dt == start_time
        assert event["duration"].dt == timedelta(minutes=90)
        assert event["url"] == "https://example.com/film"
        assert event["description"] == "https://example.com/film"
        assert event["location"] == "Test Theater: 123 Main St"

    def test_add_event_minimal(self, film_calendar):
        tz = pytz.timezone("US/Pacific")
        start_time = tz.localize(datetime(2025, 1, 1, 19, 0))
        film_calendar.add_event(
            summary="Test Film",
            dtstart=start_time,
            url="https://example.com/film",
        )
        assert len(film_calendar) == 1
        # Get the event and verify its properties
        event = next(film_calendar.cal.walk("vevent"))
        assert event["summary"] == "Test Film"
        assert event["dtstart"].dt == start_time
        assert event["duration"].dt == timedelta(minutes=120)  # Default duration
        assert event["url"] == "https://example.com/film"
        assert "location" not in event

    def test_append_filmcalendar(self, film_calendar):
        # Create a second calendar with an event
        second_calendar = FilmCalendar()
        tz = pytz.timezone("US/Pacific")
        start_time = tz.localize(datetime(2025, 1, 1, 19, 0))
        second_calendar.add_event(
            summary="Second Film",
            dtstart=start_time,
            url="https://example.com/film2",
        )
        # Append the second calendar to the first
        film_calendar.append_filmcalendar(second_calendar)
        # Verify the event was added
        assert len(film_calendar) == 1
        event = next(film_calendar.cal.walk("vevent"))
        assert event["summary"] == "Second Film"

    def test_write(self, film_calendar):
        # Add an event
        tz = pytz.timezone("US/Pacific")
        start_time = tz.localize(datetime(2025, 1, 1, 19, 0))
        film_calendar.add_event(
            summary="Test Film",
            dtstart=start_time,
            url="https://example.com/film",
        )
        # Write to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".ics", delete=False) as tmp:
            filename = tmp.name
        try:
            film_calendar.write(filename)
            # Check that the file exists and has content
            assert os.path.exists(filename)
            with open(filename, "rb") as f:
                content = f.read().decode("utf-8")
                assert "BEGIN:VCALENDAR" in content
                assert "Test Film" in content
        finally:
            # Clean up
            if os.path.exists(filename):
                os.unlink(filename)

    def test_writerss(self, film_calendar):
        # Add an event
        tz = pytz.timezone("US/Pacific")
        start_time = tz.localize(datetime(2025, 1, 1, 19, 0))
        film_calendar.add_event(
            summary="Test Film",
            dtstart=start_time,
            url="https://example.com/film",
            location="Test Theater: 123 Main St",
        )
        # Write to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".rss", delete=False) as tmp:
            filename = tmp.name
        try:
            film_calendar.writerss(filename)
            # Check that the file exists and has content
            assert os.path.exists(filename)
            with open(filename, "r") as f:
                content = f.read()
                assert "<?xml version=\"1.0\" encoding=\"utf-8\"?>" in content
                assert "<rss " in content
                assert "Test Film" in content
                assert "Test Theater" in content
        finally:
            # Clean up
            if os.path.exists(filename):
                os.unlink(filename)
