from setuptools import setup

setup(
    name="filmcalendar",
    version="1.1.4",
    description="Film calendar aggregator",
    author="Bryant Durrell",
    author_email="durrell@innocence.com",
    url="https://github.com/BryantD/film-calendar",
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=[
        "beautifulsoup4 ==4.12.2",
        "Click ==8.1.4",
        "feedgenerator ==2.1.0",
        "pytz ==2023.3",
        "icalendar ==5.0.7",
        "requests ==2.31.0",
        "tomli ==2.0.1",
        "xxhash ==3.2.0",
    ],
    entry_points={
        "console_scripts": [
            "film-calendar = filmcalendar.scripts.film_calendar:cli",
        ],
    },
)
