#!/usr/bin/env python3

import filmcalendar.filmcalendar
import filmcalendar.nwff
import filmcalendar.beacon


def main():
    nwff = filmcalendar.nwff.FilmCalendarNWFF()
    nwff.fetch_films()

    beacon = filmcalendar.beacon.FilmCalendarBeacon()
    beacon.fetch_films()
    
    seattle_films = filmcalendar.filmcalendar.FilmCalendar()
    seattle_films.append_filmcalendar(nwff)
    seattle_films.append_filmcalendar(beacon)
    seattle_films.write("film_calendar.ics")
        
if __name__ == "__main__":
    main()    
    
