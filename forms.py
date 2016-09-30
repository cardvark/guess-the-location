#!/usr/bin/env python

"""

forms.py - message forms and resource containers for use by api.

Guess the location game server-side Python App Engine

"""

from protorpc import messages


class user_form(messages.Message):
    """user_form -- create new users"""
    user_name = messages.StringField(1)
    email = messages.StringField(2)


class city_form(messages.Message):
    """city_form - provide city information"""
    city_name = messages.StringField(1)
    country = messages.StringField(2)
    region = messages.StringField(3)
