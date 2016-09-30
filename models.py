#!/usr/bin/env python

"""

models.py - class definitions for datastore entities, other game model data.

Guess the location game server-side Python App Engine

"""

from datetime import date
from google.appengine.ext import ndb

# Note - could add this to main.py, add to a web address to run a datastore population script based on this list.
# Might move this list to that function.
CITIES_LIST = [
    ['Hong Kong', 'China', 'Asia'],
    ['London', 'United Kingdom', 'Europe'],
    ['Singapore', 'Singapore', 'Asia'],
    ['Bangkok', 'Thailand', 'Asia'],
    ['Paris', 'France', 'Europe'],
    ['Shenzhen', 'China', 'Asia'],
    ['New York City', 'United States', 'North America'],
    ['Seoul', 'South Korea', 'Asia'],
    ['Rome', 'Italy', 'Europe'],
    ['Taipei', 'Taiwan', 'Asia'],
    ['Miami', 'United States', 'North America'],
    ['Shanghai', 'China', 'Asia'],
    ['Las Vegas', 'United States', 'North America'],
    ['Tokyo', 'Japan', 'Asia'],
    ['Barcelona', 'Spain', 'Europe'],
    ['Amsterdam', 'Netherlands', 'Europe'],
    ['Los Angeles', 'United States', 'North America'],
    ['Venice', 'Italy', 'Europe'],
    ['Orlando', 'United States', 'North America'],
    ['Beijing', 'China', 'Asia'],
    ['San Francisco', 'United States', 'North America'],
    ['Vancouver', 'Canada', 'North America'],
    ['Boston', 'United States', 'North America'],
    ['Seattle', 'United States', 'North America'],
    ['Portland', 'United States', 'North America'],
    ['Washington, D.C.', 'United States', 'North America'],
    ['Austin', 'United States', 'North America'],
    ['Chicago', 'United States', 'North America']
]


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()


class City(ndb.Model):
    """City information """
    city_name = ndb.StringProperty(required=True)
    country = ndb.StringProperty()
    region = ndb.StringProperty()

    @classmethod
    def get_city(cls, city_name, country, region):
        city = City.query()
        city = city.filter(City.city_name == city_name)
        city = city.filter(City.country == country)
        city = city.filter(City.region == region)

        return city.get()

    @classmethod
    def add_city(cls, city_name, country, region):
        city = City.get_city(city_name, country, region)

        if not city:
            print 'New city!'
            city = City(
                city_name=city_name,
                country=country,
                region=region
            )
            city.put()

        return city
