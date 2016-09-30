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
    ['Singapore', 'Singapore', 'Asia'],
    ['Bangkok', 'Thailand', 'Asia'],
    ['Shenzhen', 'China', 'Asia'],
    ['Seoul', 'South Korea', 'Asia'],
    ['Taipei', 'Taiwan', 'Asia'],
    ['Shanghai', 'China', 'Asia'],
    ['Tokyo', 'Japan', 'Asia'],
    ['Beijing', 'China', 'Asia'],
    ['London', 'United Kingdom', 'Europe'],
    ['Paris', 'France', 'Europe'],
    ['Rome', 'Italy', 'Europe'],
    ['Barcelona', 'Spain', 'Europe'],
    ['Amsterdam', 'Netherlands', 'Europe'],
    ['Venice', 'Italy', 'Europe'],
    ['New York City', 'United States', 'North America'],
    ['Miami', 'United States', 'North America'],
    ['Las Vegas', 'United States', 'North America'],
    ['Los Angeles', 'United States', 'North America'],
    ['Orlando', 'United States', 'North America'],
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
        """Queries and returns city entity"""
        city = City.query()
        city = city.filter(City.city_name == city_name)
        city = city.filter(City.country == country)
        city = city.filter(City.region == region)

        return city.get()

    @classmethod
    def add_city(cls, city_name, country, region):
        """Adds new city entity, unless already exists"""
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


class Monument(ndb.Model):
    """Monument information"""
    fsq_id = ndb.StringProperty()
    name = ndb.StringProperty()
    lat = ndb.FloatProperty()
    lng = ndb.FloatProperty()
    url = ndb.StringProperty()
    img_prefix = ndb.StringProperty()
    img_suffix = ndb.StringProperty()

    @classmethod
    def get_monument(cls, fsq_id):
        m_key = ndb.Key(Monument, fsq_id)

        return m_key.get()

    @classmethod
    def add_monument(cls, monument_dict):
        fsq_id = monument_dict.get('fsq_id')
        monument = Monument.get_monument(fsq_id)

        if not monument:
            m_key = ndb.Key(Monument, fsq_id)
            monument = Monument(
                key=m_key,
                fsq_id=fsq_id,
                name=monument_dict.get('name'),
                lat=monument_dict.get('lat'),
                lng=monument_dict.get('lng'),
                url=monument_dict.get('url'),
                img_prefix=monument_dict.get('img_prefix'),
                img_suffix=monument_dict.get('img_suffix')
            )
        else:
            print 'exists! updating'
            for prop, val in monument_dict.iteritems():
                monument.prop = val

        monument.put()

        return monument
