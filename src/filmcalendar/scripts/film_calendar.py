#!/usr/bin/env python3

import importlib

import click
import tomli

from filmcalendar import FilmCalendar


def load_config(file):
    with open(file, "rb") as f:
        config = tomli.load(f)
    return config


def load_config_click(ctx, param, value):
    config = load_config(value.name)
    ctx.default_map = {"theater": config["Theaters"]}
    return value


def check_theaters_click(ctx, param, value):
    for v in value:
        if v not in ctx.default_map["theater"]:
            raise click.BadParameter(v)
    return value


@click.command()
@click.option(
    "--config",
    help="Configuration file",
    default="film_calendar.toml",
    callback=load_config_click,
    is_eager=True,
    type=click.File(mode="rb")
    # Little bit hacky here -- we're using click.File() to validate input, but
    # we extract the file name before opening it. Why? Because Click tosses away
    # the context so you can't read a click.File file more than once.
)
@click.option(
    "--theater",
    help="Theater to crawl",
    multiple=True,
    callback=check_theaters_click,
)
@click.argument(
    "directory",
    default=".",
    type=click.Path(exists=True),
)
def cli(config, theater, directory):
    """
    This script crawls movie theaters and generates calendar and RSS files.
    By default, all known theaters are crawled. Optionally specify DIRECTORY
    for output files; the default is the current directory.
    """

    config_data = load_config(config.name)

    seattle_films = FilmCalendar(
        calendar_name=config_data["calendar_name"],
        timezone=config_data["timezone"],
        site_url=config_data["site_url"],
    )

    for t in theater:
        print(f"Scraping {config_data['Theaters'][t]}")
        theater_module = importlib.import_module(
            f"filmcalendar.{config_data['city']}.{t}"
        )
        klass = getattr(
            theater_module, f"FilmCalendar{config_data['Theaters'][t].replace(' ', '')}"
        )

        theater_calendar = klass(
            calendar_name=f"{config_data['Theaters'][t]} Movie Calendar",
            theater_name=config_data["Theaters"][t],
            timezone=config_data["timezone"],
            site_url=config_data["site_url"],
        )
        theater_calendar.fetch_films()
        theater_calendar.write(f"{directory}/{t}.ics")
        seattle_films.append_filmcalendar(theater_calendar)

    seattle_films.write(f"{directory}/film_calendar.ics")
    seattle_films.writerss(f"{directory}/film_calendar.rss")
