#!/usr/bin/env python3

import argparse
import importlib
from pathlib import Path

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
        "directory", nargs="?", help="Directory to write to", default="."
    )
    args = parser.parse_args()

    output_dir = Path(args.directory)
    if output_dir.is_dir():
        seattle_films = filmcalendar.filmcalendar.FilmCalendar()

        for theater in args.theaters:
            print(f"Scraping {theaters[theater]}")
            theater_module = importlib.import_module(f"filmcalendar.{theater}")
            klass = getattr(
                theater_module, f"FilmCalendar{theaters[theater].replace(' ', '')}"
            )

            theater_calendar = klass(
                calendar_name=f"{theaters[theater]} Movie Calendar"
            )
            theater_calendar.fetch_films()
            theater_calendar.write(f"{args.directory}/{theater}.ics")
            seattle_films.append_filmcalendar(theater_calendar)

        seattle_films.write(f"{args.directory}/film_calendar.ics")
        seattle_films.writerss(f"{args.directory}/film_calendar.rss")

    else:
        print(f"ERROR: {args.directory} is not a directory")


if __name__ == "__main__":
    main()
