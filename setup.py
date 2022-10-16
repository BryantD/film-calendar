from setuptools import setup

setup(
    name="film_calendar",
    version="1.0.0",
    py_modules=["film_calendar"],
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
            "film-calendar = film_calendar:cli",
        ],
    },
)
