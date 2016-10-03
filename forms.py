#!/usr/bin/env python

"""

forms.py - message forms and resource containers for use by api.

Guess the location game server-side Python App Engine

"""

from protorpc import messages


class UserForm(messages.Message):
    """UserForm -- create new users"""
    user_name = messages.StringField(1)
    email = messages.StringField(2)


class NewGameForm(messages.Message):
    user = messages.StringField(1)
    regions = messages.StringField(2, repeated=True)
    cities_total = messages.IntegerField(3)


class GameForm(messages.Message):
    urlsafe_key = messages.StringField(1)
    cities_total = messages.IntegerField(2)
    user = messages.StringField(3)
    message = messages.StringField(4)

# potentially deprecated.
# class NewCityQuestionForm(messages.Message):
#     """NewCityQuestionForm -- request requirements for new city question"""


class CityQuestionForm(messages.Message):
    """CityQuestionForm -- response form"""
    # TODO
