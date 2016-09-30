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

app = webapp2.WSGIApplication([

], debug=True)
