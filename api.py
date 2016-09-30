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
from models import User
from utils import get_by_urlsafe
import forms
from settings import *

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID

# TODO: Monument ndb and form.
# TODO: main.py handler to cycle through cities list and fill Monument datastore.


@endpoints.api(
    name='guess_the_location',
    version='v1',
    # allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
    # scopes=[EMAIL_SCOPE]
)
class GuessLocationApi(remote.Service):
    """Guess the location game API"""

    @endpoints.method(
        request_message=forms.user_form,
        response_message=forms.user_form,
        path='user',
        name='create_user',
        http_method='POST'
    )
    def create_user(self, request):
        """Create a User.  Requires unique username"""

        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException('A user with that name already exists!')

        user = User(
            name=request.user_name,
            email=request.email
        )
        user.put()

        return forms.user_form(user_name=user.name, email=user.email)


api = endpoints.api_server([GuessLocationApi])
