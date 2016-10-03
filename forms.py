#!/usr/bin/env python

"""

forms.py - message forms and resource containers for use by api.

Guess the location game server-side Python App Engine

"""

from protorpc import messages


class User_Form(messages.Message):
    """User_Form -- create new users"""
    user_name = messages.StringField(1)
    email = messages.StringField(2)


class New_Game_Form(messages.Message):
    user = messages.StringField(1)
    regions = messages.StringField(2, repeated=True)
    cities_total = messages.IntegerField(3)


class Game_Form(messages.Message):
    urlsafe_key = messages.StringField(1)
    cities_total = messages.IntegerField(2)
    user = messages.StringField(3)
    message = messages.StringField(4)


# Deprecated for now.
# class city_form(messages.Message):
#     """city_form - provide city information"""
#     city_name = messages.StringField(1)
#     country = messages.StringField(2)
#     region = messages.StringField(3)
