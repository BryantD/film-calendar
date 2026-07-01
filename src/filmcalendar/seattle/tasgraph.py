#!/usr/bin/env python
# /// script
# dependencies = [
#   "gql",
#   "requests",
# ]
# ///

import pprint
from collections import defaultdict

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

transport = RequestsHTTPTransport(
    url="https://filmcenter.tasveer.org/graphql",
    headers={
        "Content-Type": "application/json",
        "Accept": "application/graphql-response+json,application/json;q=0.9",
        "site-id": "262",
        "client-type": "consumer",
        "circuit-id": "138",
        "Origin": "https://filmcenter.tasveer.org",
        "Referer": "https://filmcenter.tasveer.org/showtimes/",
    },
    verify=True,
    retries=2,
)

client = Client(transport=transport, fetch_schema_from_transport=False)

query_string = """query ($date: String, $siteIds: [ID]) {
  showingsForDate(date: $date, siteIds: $siteIds) {
    data {
      id
      time
      showingId
      published
      seatsRemaining
      screenId
      showingBadgeIds
      movie {
        id
        name
        urlSlug
        synopsis
        duration
        rating
        ratingReason
        genre
        directedBy
        starring
        posterImage
        releaseDate
      }
    }
    count
  }
}
"""

variables = {
    "date": "2026-07-01",
    "siteIds": [262],
}


query = gql(query_string)
result = client.execute(query, variable_values=variables)
screenings = result["showingsForDate"]["data"]  # flat list, one entry per screening

pprint.pp(screenings)

films = defaultdict(lambda: {"movie": None, "showtimes": []})

for s in screenings:
    print(s["movie"]["name"])
    print(s["time"])
    print(s["movie"]["duration"])
    print(f"https://filmcenter.tasveer.org/movie/{s['movie']['urlSlug']}")
