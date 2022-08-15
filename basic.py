#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
import pytz
from datetime import datetime, timedelta
import os


def get_isosplit(s, split):
    if split in s:
        n, s = s.split(split)
    else:
        n = 0
    return n, s


def parse_isoduration(s):
        
    # Remove prefix
    s = s.split('P')[-1]
    
    # Step through letter dividers
    days, s = get_isosplit(s, 'D')
    _, s = get_isosplit(s, 'T')
    hours, s = get_isosplit(s, 'H')
    minutes, s = get_isosplit(s, 'M')
    seconds, s = get_isosplit(s, 'S')

    # Convert all to seconds
    dt = timedelta(days=int(days), hours=int(hours), minutes=int(minutes), seconds=int(seconds))
    return int(dt.total_seconds())
    

def main():
    req_headers = {'user-agent': 'seattle-movie-calendar/0.1'}
    req_payload = {'type': 'film', 'attributes': ''}
    try:
        req = requests.get('https://nwfilmforum.org/calendar', headers=req_headers, params=req_payload)
    except requests.exceptions.RequestException as e:
        print(e)

    soup = BeautifulSoup(req.text, 'html.parser')

    cal = Calendar()

    for day in soup.find_all("div", class_="calendar__grid__col"):
        date = day["data-id"]
        for film in day.find_all("div", class_="calendar__item--film"):
            film_title = film.find("meta", itemprop="name")["content"]
            film_date = datetime.fromisoformat(film.find("meta", itemprop="startDate")["content"])
            film_duration = parse_isoduration(film.find("meta", itemprop="duration")["content"])

            event = Event()
            event.add("summary", film_title)
            event.add("dtstart", film_date)
            event.add("dtend", film_date + timedelta(seconds=film_duration))
            cal.add_component(event)
            
    f = open('basic.ics', 'wb')
    f.write(cal.to_ical())
    f.close()

if __name__ == "__main__":
    main()    
    
