#!/usr/bin/env python3

# https://icalendar.readthedocs.io/en/latest/index.html

import filmcalendar.filmcalendar
import filmcalendar.nwff


def main():
    f = filmcalendar.nwff.FilmCalendarNWFF()
    f.fetch_films()
    j = filmcalendar.filmcalendar.FilmCalendar()
    j.append_calendar(f)
    j.write("film_calendar.ics")
        
if __name__ == "__main__":
    main()    
    
