#!/usr/bin/env python3

import importlib

import click

import filmcalendar.filmcalendar

theater_list = {
    "thebeacon": "The Beacon",
    "centralcinema": "Central Cinema",
    "grandillusion": "Grand Illusion",
    "nwff": "NWFF",
    "siff": "SIFF",
}


@click.command()
@click.option(
    "--theaters",
    help="Theaters to crawl",
    default=theater_list.keys(),
    multiple=True,
    type=click.Choice(theater_list.keys()),
)
@click.argument(
    "directory",
    default=".",
    type=click.Path(exists=True),
)
def cli(theaters, directory):
    """
    This script crawls movie theaters and generates calendar and RSS files.
    By default, all known theaters are crawled.
    """

    seattle_films = filmcalendar.filmcalendar.FilmCalendar()

    for theater in theaters:
        print(f"Scraping {theater_list[theater]}")
        theater_module = importlib.import_module(f"filmcalendar.{theater}")
        klass = getattr(
            theater_module, f"FilmCalendar{theater_list[theater].replace(' ', '')}"
        )

        theater_calendar = klass(
            calendar_name=f"{theater_list[theater]} Movie Calendar"
        )
        theater_calendar.fetch_films()
        theater_calendar.write(f"{directory}/{theater}.ics")
        seattle_films.append_filmcalendar(theater_calendar)

    seattle_films.write(f"{directory}/film_calendar.ics")
    seattle_films.writerss(f"{directory}/film_calendar.rss")
