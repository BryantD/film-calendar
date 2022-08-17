#!/usr/bin/env python3

import filmcalendar.filmcalendar
import filmcalendar.beacon
import filmcalendar.centralcinema
import filmcalendar.nwff


def main():
    beacon = filmcalendar.beacon.FilmCalendarBeacon()
    beacon.fetch_films()

    central = filmcalendar.centralcinema.FilmCalendarCentralCinema()
    central.fetch_films()

    nwff = filmcalendar.nwff.FilmCalendarNWFF()
    nwff.fetch_films()

    seattle_films = filmcalendar.filmcalendar.FilmCalendar()

    seattle_films.append_filmcalendar(beacon)
    seattle_films.append_filmcalendar(central)
    seattle_films.append_filmcalendar(nwff)

    seattle_films.write("film_calendar.ics")
        
if __name__ == "__main__":
    main()    
    
