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
NEW_QUESTION_REQUEST = endpoints.ResourceContainer(
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
        game = models.Game.new_game(request.user, request.regions, request.cities_total)

        return game.to_form('New game created.  Best of luck!')

    @endpoints.method(
        request_message=NEW_QUESTION_REQUEST,
        response_message=forms.CityQuestionForm,
        path='new_question',
        name='new_question',
        http_method='POST'
    )
    def new_question(self, request):
        game = utils.get_by_urlsafe(request.websafe_game_key, models.Game)

        if game.game_over:
            return game.to_form('Game already over!  Try another.')

        new_city_question = gl.get_new_city_question(game)
        # TODO


api = endpoints.api_server([GuessLocationApi])
