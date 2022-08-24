#!/usr/bin/env python3

import argparse
import importlib

import filmcalendar.filmcalendar


def main():
    theaters = {
        "thebeacon": "The Beacon",
        "centralcinema": "Central Cinema",
        "grandillusion": "Grand Illusion",
        "nwff": "NWFF",
        "siff": "SIFF",
    }

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--theaters",
        "-t",
        nargs="*",
        help="Theaters to scrape",
        choices=theaters.keys(),
        default=theaters.keys(),
    )
    parser.add_argument(
        "output", nargs="?", help="File name to write to", default="film_calendar.ics"
    )
    args = parser.parse_args()

    seattle_films = filmcalendar.filmcalendar.FilmCalendar()

    for theater in args.theaters:
        print(f"Scraping {theaters[theater]}")
        theater_module = importlib.import_module(f"filmcalendar.{theater}")
        klass = getattr(
            theater_module, f"FilmCalendar{theaters[theater].replace(' ', '')}"
        )

        theater_calendar = klass()
        theater_calendar.fetch_films()
        theater_calendar.write(f"{theater}.ics")
        seattle_films.append_filmcalendar(theater_calendar)

    seattle_films.write(args.output)


if __name__ == "__main__":
    main()
