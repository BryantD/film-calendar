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

    def __str__(self):
        cal_string = self.cal.to_ical()
        return cal_string.decode("utf-8")
        
    def append_calendar(self, calendar):
        for event in calendar.cal.walk(name="vevent"):
            self.cal.add_component(event)

    def add_event(self, summary=None, dtstart=None, url=None, duration=0, location=None):
        event = Event()
        event.add("summary", summary)
        event.add("dtstart", vDatetime(dtstart))
        if duration:
            event.add("duration", timedelta(seconds=duration))
        if url:
            event.add("url", url)
        if location:
            event.add("location", location)
        event.add("description", f"{self.theater}\n{url}")
        self.cal.add_component(event)

    def write(self, filename="film_calendar.ics"):
        self.cal.add("last-modified", vDatetime(datetime.now()))
        f = open(filename, "wb")
        f.write(self.cal.to_ical())
        f.close()
