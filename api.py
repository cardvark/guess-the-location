# -*- coding: utf-8 -*-`
"""
api.py - game APIs.

Guess the location game server-side Python App Engine

"""

import logging
import endpoints
from protorpc import remote, messages, message_types
from google.appengine.api import memcache
from google.appengine.api import taskqueue

import foursquareApi as fApi
import models
import game_logic as gl
import utils
import forms
from settings import *

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID
USER_REQUEST = endpoints.ResourceContainer(forms.UserForm)
NEW_GAME_REQUEST = endpoints.ResourceContainer(forms.NewGameForm)
GET_QUESTION_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafe_game_key=messages.StringField(1)
)


@endpoints.api(
    name='guess_the_location',
    version='v1',
    allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
    scopes=[EMAIL_SCOPE]
)
class GuessLocationApi(remote.Service):
    """Guess the location game API"""

    @endpoints.method(
        request_message=USER_REQUEST,
        response_message=forms.UserForm,
        path='user',
        name='create_user',
        http_method='POST'
    )
    def create_user(self, request):
        """Create a User.  Requires unique username"""

        user = models.User.add_user(request.user_name, request.email)
        return forms.UserForm(user_name=user.name, email=user.email)

    @endpoints.method(
        request_message=NEW_GAME_REQUEST,
        response_message=forms.GameForm,
        path='game',
        name='new_game',
        http_method='POST'
    )
    def new_game(self, request):
        game = models.Game.new_game(request.user_name, request.regions, request.cities_total)

        return game.to_form('New game created.  Best of luck!')

    # TODO: maybe deprecate this in favor a of a "next_move" options.
    # next_move should determine whether to create new question.
    # Alt, it could be 'get question' - either gets current active, or creates new.
    @endpoints.method(
        request_message=GET_QUESTION_REQUEST,
        response_message=forms.CityQuestionForm,
        path='get_question',
        name='get_question',
        http_method='POST'
    )
    def get_question(self, request):
        game = utils.get_by_urlsafe(request.websafe_game_key, models.Game)

        if game.game_over:
            return game.to_form('Game is already over!  Try another one!')

        # NOTE: shouldn't need this one; game should either have active or be in game_over status.  Shouldn't have the case where this is necessary.
        # if game.cities_asked >= gl.MAX_CITY_QUESTIONS:
        #     return game.to_form('Already generated max questions for this game!')

        if game.active_question:
            question = game.active_question.get()
            message = 'Active question in progress!'
        else:
            question = gl.get_new_city_question(game)
            message = 'New question!  Good luck!'

        return question.to_form(message)


api = endpoints.api_server([GuessLocationApi])
