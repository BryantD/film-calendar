from setuptools import setup, find_packages

setup(
    name="filmcalendar",
    version="1.2.2",
    description="Film calendar aggregator",
    author="Bryant Durrell",
    author_email="durrell@innocence.com",
    url="https://github.com/BryantD/film-calendar",
    packages=find_packages("src"),
    package_dir={"": "src"},
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
        "beautifulsoup4 ==4.12.3",
        "Click ==8.1.7",
        "feedgenerator ==2.1.0",
        "pytz ==2024.2",
        "icalendar ==6.1.1",
        "requests ==2.32.3",
        "tomli ==2.2.1",
        "xxhash ==3.5.0",
    ],
    entry_points={
        "console_scripts": [
            "film-calendar = filmcalendar.scripts.film_calendar:cli",
        ],
    },
)

print(find_packages())
