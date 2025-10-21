from datetime import datetime, timedelta

import feedgenerator
import pytz
import xxhash
from icalendar import Calendar, Event, vDatetime


class FilmCalendar:
    def __init__(
        self,
        calendar_name="Arthouse Movie Calendar",
        theater_name="",
        timezone="US/Pacific",
        site_url="https://github.com/BryantD/film-calendar",
    ):
        self.timezone_string = timezone
        try:
            self.timezone = pytz.timezone(self.timezone_string)
        except pytz.exceptions.UnknownTimeZoneError:
            raise pytz.exceptions.UnknownTimeZoneError(
                f"Timezone {timezone} is unknown by pytz"
            )

        self.calendar_name = calendar_name
        self.theater = theater_name

        self.site_url = site_url

        self.req_headers = {"user-agent": f"movie-calendar/1.1 ({site_url})"}

        self.cal = Calendar()
        self.cal.add("version", "2.0")
        self.cal.add("prodid", f"-//{calendar_name}//NONSGML Event Calendar//EN")
        self.cal.add("x-wr-calname", calendar_name)
        self.cal.add("x-wr-timezone", self.timezone_string)

    def __str__(self):
        cal_string = self.cal.to_ical()
        return cal_string.decode("utf-8")

    def __len__(self):
        return len(self.cal.walk(name="vevent"))

    def append_filmcalendar(self, calendar):
        for event in calendar.cal.walk(name="vevent"):
            self.cal.add_component(event)

    def add_event(
        self,
        summary,
        dtstart,
        url,
        duration=timedelta(minutes=120),
        location=None,
    ):
        event = Event()

        # Required components
        event.add("summary", summary)
        event.add("dtstart", vDatetime(dtstart))
        event.add("duration", duration)

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
            event_time = vDatetime.from_ical(event["dtstart"].to_ical()).strftime(
                "%b %d, %I:%M %p"
            )
            event_description = f"{theater_name}: {event_name} ({event_time})"
            feed.add_item(
                title=event_description,
                link=event.decoded("url"),
                description=event_description,
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
