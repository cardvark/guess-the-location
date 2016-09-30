#!/usr/bin/env python

"""
main.py -- Guess the location game server-side Python App Engine
HTTP controller handlers.

$Id$

created by James Wang, 2016-09-29

"""

__author__ = 'wang.james.j@gmail.com'

import webapp2
import sys
from google.appengine.api import app_identity
from google.appengine.api import mail
from api import GuessLocationApi
from models import City, CITIES_LIST, Monument
import foursquareApi as fApi
from google.appengine.ext import ndb
# from forms import city_form

reload(sys)
sys.setdefaultencoding('utf-8')


class BuildCityDataHandler(webapp2.RequestHandler):
    def get(self):
        """Builds the datastore City entities"""

        ndb.delete_multi(City.query().fetch(keys_only=True))

        for city_list in CITIES_LIST:
            City.add_city(city_list[0], city_list[1], city_list[2])

        # return 'Done'


class BuildMonumentsDataHandler(webapp2.RequestHandler):
    def get(self):
        """Builds Monument entities via Foursquare API"""

        cities_list = City.query().fetch(projection=[City.city_name])
        for city in cities_list:
            print city.city_name

            monuments_list = fApi.monuments_by_city(city.city_name)

            for monument in monuments_list:
                mon = Monument.add_monument(monument)
                print city.city_name, mon.name


app = webapp2.WSGIApplication([
    ('/jobs/build_city_data', BuildCityDataHandler),
    ('/jobs/build_monuments_data', BuildMonumentsDataHandler)
], debug=True)
