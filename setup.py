from setuptools import setup

setup(
    name="filmcalendar",
    version="1.0.0",
    include_package_data=True,
    install_requires=[
        "bs4",
        "Click",
        "feedgenerator",
        "icalendar",
        "pytz",
        "requests",
        "xxhash",
    ],
    entry_points={
        "console_scripts": [
            "film-calendar = filmcalendar.scripts.film_calendar:cli",
        ],
    },
)
