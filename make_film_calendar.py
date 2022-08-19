#!/usr/bin/env python3

import argparse

import filmcalendar.filmcalendar
import filmcalendar.beacon
import filmcalendar.centralcinema
import filmcalendar.grandillusion
import filmcalendar.nwff
import filmcalendar.siff


def main():
    theaters = [
        "beacon",
        "central",
        "grandillusion",
        "nwff",
        "siff",
    ]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--theaters", "-t", nargs="*", help="Theaters to scrape", choices=theaters
    )
    parser.add_argument(
        "output", nargs="?", help="File name to write to", default="film_calendar.ics"
    )
    args = parser.parse_args()

    seattle_films = filmcalendar.filmcalendar.FilmCalendar()

    if not args.theaters or "beacon" in args.theaters:
        print("Scraping The Beacon...")
        beacon = filmcalendar.beacon.FilmCalendarBeacon()
        beacon.fetch_films()
        seattle_films.append_filmcalendar(beacon)

    if not args.theaters or "central" in args.theaters:
        print("Scraping Central Cinema...")
        central = filmcalendar.centralcinema.FilmCalendarCentralCinema()
        central.fetch_films()
        seattle_films.append_filmcalendar(central)

    if not args.theaters or "grandillusion" in args.theaters:
        print("Scraping Grand Illusion...")
        grand = filmcalendar.grandillusion.FilmCalendarGrandIllusion()
        grand.fetch_films()
        seattle_films.append_filmcalendar(grand)

    if not args.theaters or "nwff" in args.theaters:
        print("Scraping NWFF...")
        nwff = filmcalendar.nwff.FilmCalendarNWFF()
        nwff.fetch_films()
        seattle_films.append_filmcalendar(nwff)

    if not args.theaters or "siff" in args.theaters:
        print("Scraping SIFF...")
        siff = filmcalendar.siff.FilmCalendarSIFF()
        siff.fetch_films()
        seattle_films.append_filmcalendar(siff)

    seattle_films.write(args.output)


if __name__ == "__main__":
    main()
