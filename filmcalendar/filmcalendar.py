from icalendar import Calendar, Event, vDatetime
from datetime import datetime, timedelta


class FilmCalendar:
    req_headers = {"user-agent": "seattle-movie-calendar/0.1"}

    def __init__(self):
        self.cal = Calendar()
        self.cal.add("version", "2.0")
        self.cal.add("prodid", "-//Seattle Arthouse Film Calendar//NONSGML Event Calendar//EN")
        self.cal.add("x-wr-calname", "Seattle Arthouse Film Calendar")
        self.cal.add("x-wr-timezone", "US/Pacific")
        self.theater = ""
        self.uid_base = "seattle-movies.innocence.com"

    def __str__(self):
        cal_string = self.cal.to_ical()
        return cal_string.decode("utf-8")
        
    def append_filmcalendar(self, calendar):
        for event in calendar.cal.walk(name="vevent"):
            self.cal.add_component(event)

    def add_event(self, summary=None, dtstart=None, url=None, duration=120*60, location=None):
        event = Event()
        
        # Required components
        event.add("summary", summary)
        event.add("dtstart", vDatetime(dtstart))
        event.add("duration", timedelta(seconds=duration))
        event.add("description", f"{self.theater}\n{url}")

        # Optional components
        if url:
            event.add("url", url)
        if location:
            event.add("location", location)
        
        # Auto-generated components
        event.add("dtstamp", vDatetime(datetime.now()))
        
        self.cal.add_component(event)

    def write(self, filename="film_calendar.ics"):
        self.cal.add("last-modified", vDatetime(datetime.now()))
        event_count = 0
        for event in self.cal.walk(name="vevent"):
            uid_timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
            event_count = event_count + 1
            uid = f"{uid_timestamp}-{event_count}@{self.uid_base}"
            event.add("uid", uid)

        f = open(filename, "wb")
        f.write(self.cal.to_ical())
        f.close()
