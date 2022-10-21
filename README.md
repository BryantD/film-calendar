# Introduction

This is an aggregator and calendar generator for local movie times. Out of the box it works for Seattle, since that's where I live, but it should be relatively easy to extend it to other cities.

# film-calendar Usage

```
Usage: film-calendar [OPTIONS] [DIRECTORY]
  This script crawls movie theaters and generates calendar and RSS files.
  By default, all known theaters are crawled. Optionally specify DIRECTORY
  for output files; the default is the current directory.

Options:
  --config FILENAME  Configuration file
  --theater TEXT     Theater to crawl
  --help             Show this message and exit.
```

# Installation

This assumes you want to use python's venv functionality, which you probably should. You will also need python 3 (tested with python 3.8, you're on your own if you use an older version).

Also check and make sure you have setuptools installed:

`python3 -m pip install setuptools`

1. Download the code and make sure you're in the top level directory of the source tree
1. Run `python3 -m venv venv`
1. Run `source venv/bin/activate`
1. Run `python3 -m pip install .`

You should be good. If you want a global install for some reason, you probably know how to modify the above instructions to achieve your desires.

# Configuration

You must supply a TOML configuration file to run the included script. Fortunately the format is pretty simple, and the one that comes with the package will work out of the box so you can stop reading now if you don't want to change anything.

It looks like this:

```city = "seattle"
calendar_name = "Seattle Arthouse Movie Calendar"
timezone = "US/Pacific"

[Theaters]
thebeacon = "The Beacon"
centralcinema = "Central Cinema"
grandillusion = "Grand Illusion"
nwff = "NWFF"
siff = "SIFF"
```

`city` is the name of the city you're making calendars for. This is only used for finding the right module -- see below for more details on this. It should be lower case; you can use underscores if you feel the need but I wouldn't.

`calendar_name` will be used in the calendar and RSS files. 

`timezone` must be a timezone as understood by [pytz](https://pytz.sourceforge.net/#helpers).

`[Theaters]` is a table used to define module and class names. Each line defines one theater. If we use `shortname = "Full Name"` as an example, `film-calendar` parses the line as follows:

- `shortname.py` will be the name of the theater's module
- `shortname.ics` will be the name of generated calendar files
- `Full Name Movie Calendar` will be the calendar name used in generated calendar and RSS files
- `FullName` will be the name of the theater's class (spaces are removed)

This is a bit contrived but it works for me as a naming scheme. 

# Extending the Code

First off, make a new directory in `src/filmcalendar` named after your city, in lowercase. Drop an empty `__init__.py` file in the new directory. As per the Configuration section above, `film-calendar` loads per-theater modules from a specified directory. This is the directory you'll specify.

Second, check out `src/filmcalendar/seattle/centralcinema.py` as a model for your new class.

## Module Structure

### Imports

You may or may not need to import `html` or `json`, depending on what kind of parsing you need to do. Personally I leave those imports in everywhere because there's a good chance I'll be parsing json data and unescaping random strings. 

`BeautifulSoup` and `requests` are musts for me, but if you have a different preference for retrieving and parsing Web pages, go for it. Or if you're reading your data from something other than a Web page or even a REST API, you probably won't need the same libraries I did. 

`datetime` is necessary, because you're going to call `self.add_event` with parameters that have to be datetime objects.

### Class 

The `__init__` and `__str__` functions are pretty cut and dried. I set the various constants in `__init__` since it means they're in a consistent place across all the classes I wrote for this. 

`fetch_films` does the hard work. For each showing of a film your scraper finds, call `self.add_event` (inherited from the parent class) with the parameters `summary`, `dtstart`, `duration`, `url`, and `location`. Easy as pie.

`duration` is an integer containing the duration of the movie in seconds.

`film_date` is a datetime object.

If you poke around a bit you'll notice that the FilmCalendar class converts `duration` to a timedelta under the hood, and you may wonder why it doesn't expect a timedelta to start with. Isn't that inconsistent? Yes, it is, and I'm writing this note so that I fix it before I roll out the customizability branch.

## HTML

The files in `html` are static and do not use templating. Change these however you like.

## film-calendar

My goal was to write the script so that it'd work for other cities with only configuration changes. However, there's nothing stopping you from writing your own script. If you do this, you can do away with all the funky `importlib.import_module` tricks I'm doing; the core of the code is really just something like:

```
# Instantiate classes -- one for all the movies, and one for each theater
films = FilmCalendar()
classic_theater_films = FilmCalendarClassic()
movieplex_films = FilmCalendarMovieplex()

# For each theater:
# 1) fetch the movie showings
# 2) write out a calendar file
# 3) append the theater's movies to the master list
classic_theater_films.fetch_films()
classic_theater_films.write("classic_theater.ics")
seattle_films.append_filmcalendar(classic_theater_films)

movieplex_films.fetch_films()
movieplex_films.write("movieplex.ics")
films.append_filmcalendar(movieplex_films)

# Write out the master list as a calendar and as an RSS file
films.write("film_calendar.ics")
films.writerss("film_calendar.rss")
```