from datetime import datetime, timedelta

import feedgenerator
import pytz
import xxhash
from icalendar import Calendar, Event, vDatetime


class FilmCalendar:
    site_url = "https://seattle-movies.innocence.com/"
    req_headers = {"user-agent": f"seattle-movie-calendar/1.0 ({site_url})"}

    def __init__(self, calendar_name="Seattle Arthouse Movie Calendar"):
        self.timezone_string = "US/Pacific"
        self.timezone = pytz.timezone(self.timezone_string)
        self.theater = ""
        self.uid_base = "seattle-movies.innocence.com"
        self.calendar_name = calendar_name

        self.cal = Calendar()
        self.cal.add("version", "2.0")
        self.cal.add("prodid", f"-//{calendar_name}//NONSGML Event Calendar//EN")
        self.cal.add("x-wr-calname", calendar_name)
        self.cal.add("x-wr-timezone", self.timezone_string)

    def __str__(self):
        cal_string = self.cal.to_ical()
        return cal_string.decode("utf-8")

    def append_filmcalendar(self, calendar):
        for event in calendar.cal.walk(name="vevent"):
            self.cal.add_component(event)

    def add_event(self, summary, dtstart, url, duration=120 * 60, location=None):
        event = Event()

        # Required components
        event.add("summary", summary)
        event.add("dtstart", vDatetime(dtstart))
        event.add("duration", timedelta(seconds=duration))

        # Optional components
        if url:
            event.add("url", url)
            event.add("description", url)
            # Google Calendar doesn't support the URL field
        if location:
            event.add("location", location)

        # Auto-generated components
        event.add("dtstamp", vDatetime(datetime.now(tz=self.timezone)))

        uid_hash = xxhash.xxh64()
        uid_hash.update(f"{dtstart}-{url}")
        event.add("uid", uid_hash.hexdigest())

        self.cal.add_component(event)

    def writerss(self, filename="film_calendar.rss"):

        feed = feedgenerator.Rss201rev2Feed(
            title=self.calendar_name,
            link=self.site_url,
            description=self.calendar_name,
            language="en",
        )
        for event in self.cal.walk(name="vevent"):
            theater_name = event.decoded("location").decode("utf-8").split(":")[0]
            event_name = event.decoded("summary").decode("utf-8")
            event_time = vDatetime.from_ical(event["dtstart"].to_ical())
            feed.add_item(
                title=event.decoded("summary"),
                link=event.decoded("url"),
                description=f"{theater_name}: {event_name} ({event_time})",
                unique_id=event.decoded("uid"),
                unique_id_is_permalink=False,
            )

        f = open(filename, "w")
        feed.write(f, "utf-8")
        f.close()

    def write(self, filename="film_calendar.ics"):
        self.cal.add("last-modified", vDatetime(datetime.now(tz=self.timezone)))
        f = open(filename, "wb")
        f.write(self.cal.to_ical())
        f.close()
