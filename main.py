#!/usr/bin/env python

"""
main.py -- Guess the location game server-side Python App Engine
HTTP controller handlers.

$Id$

created by James Wang, 2016-09-29

"""

__author__ = 'wang.james.j@gmail.com'

import webapp2
from google.appengine.api import app_identity
from google.appengine.api import mail
from api import GuessLocationApi
from models import City, CITIES_LIST
# from forms import city_form


class BuildCityDataHandler(webapp2.RequestHandler):
    def get(self):
        """Clears and builds the datastore City entities"""

        for city_list in CITIES_LIST:
            City.add_city(city_list[0], city_list[1], city_list[2])

        # return 'Done'


app = webapp2.WSGIApplication([
    ('/jobs/build_city_data', BuildCityDataHandler),
], debug=True)
