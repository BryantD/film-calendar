from setuptools import setup

setup(
    name="filmcalendar",
    version="1.0.0",
    include_package_data=True,
    install_requires=[
        "beautifulsoup4 ==4.11.1",
        "Click ==8.1.3",
        "feedgenerator ==2.0.0",
        "icalendar ==4.1.0",
        "pytz ==2022.1",
        "requests ==2.28.1",
        "tomli",
        "xxhash ==3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "film-calendar = filmcalendar.scripts.film_calendar:cli",
        ],
    },
)
