#!/usr/bin/env python

"""

forms.py - message forms and resource containers for use by api.

Guess the location game server-side Python App Engine

"""

from protorpc import messages


class UserForm(messages.Message):
    """UserForm -- create new users"""
    user_name = messages.StringField(1, required=True)
    email = messages.StringField(2)


class NewGameForm(messages.Message):
    """NewGameForm -- create new games"""
    user_name = messages.StringField(1)
    regions = messages.StringField(2, repeated=True)
    cities_total = messages.IntegerField(3)


class GameForm(messages.Message):
    """GameForm -- outbound Game form message"""
    urlsafe_game_key = messages.StringField(1)
    cities_total = messages.IntegerField(2)
    user_name = messages.StringField(3)
    cities_remaining = messages.IntegerField(4)
    active_question = messages.StringField(5)
    message = messages.StringField(6)


class GameForms(messages.Message):
    """GameForms --multiple Game outbound form message """
    items = messages.MessageField(GameForm, 1, repeated=True)
    message = messages.StringField(2)


# Should match game_logic.MONUMENT_PROPERTIES_UNLOCKS_DICT
class CityQuestionForm(messages.Message):
    """CityQuestionForm -- response form"""
    urlsafe_city_key = messages.StringField(1)
    lat = messages.FloatField(2)
    lng = messages.FloatField(3)
    min_zoom = messages.IntegerField(4)
    name = messages.StringField(5)
    img_prefix = messages.StringField(6)
    img_suffix = messages.StringField(7)
    url = messages.StringField(8)
    attempts_remaining = messages.IntegerField(9)
    question_score = messages.IntegerField(10)
    message = messages.StringField(11)
    # TODO: Add question_over bool?


class QuestionAttemptForm(messages.Message):
    """QuestionAttemptForm -- city guess request form
    - Remaining request information in ResourceContainer
    """
    city_guess = messages.StringField(1, required=True)


class UserGamesForm(messages.Message):
    """UserGamesForm -- request user's games.  All or Active only"""
    user_name = messages.StringField(1, required=True)
    all_games = messages.BooleanField(2)
