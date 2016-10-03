# -*- coding: utf-8 -*-`
"""
api.py - game APIs.

Guess the location game server-side Python App Engine

"""

import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

import foursquareApi as fApi
import models
from utils import get_by_urlsafe
import forms
from settings import *

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID
USER_REQUEST = endpoints.ResourceContainer(forms.User_Form)
NEW_GAME_REQUEST = endpoints.ResourceContainer(forms.New_Game_Form)

# TODO: Monument ndb and form.
# TODO: main.py handler to cycle through cities list and fill Monument datastore.


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
        response_message=forms.User_Form,
        path='user',
        name='create_user',
        http_method='POST'
    )
    def create_user(self, request):
        """Create a User.  Requires unique username"""

        user = models.User.add_user(request.user_name, request.email)
        return forms.User_Form(user_name=user.name, email=user.email)

    @endpoints.method(
        request_message=NEW_GAME_REQUEST,
        response_message=forms.Game_Form,
        path='game',
        name='new_game',
        http_method='POST'
    )
    def new_game(self, request):
        game = models.Game.new_game(request.user, request.regions, request.cities_total)

        return game.to_form('New game created.  Best of luck!')


api = endpoints.api_server([GuessLocationApi])
