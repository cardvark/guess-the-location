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
QUESTION_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafe_game_key=messages.StringField(1)
)
QUESTION_ATTEMPT_POST_REQUEST = endpoints.ResourceContainer(
    forms.QuestionAttemptForm,
    websafe_question_key=messages.StringField(1)
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
        if models.User.query(User.name == name).get():
            raise endpoints.ConflictException('A user with that name already exists!')

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
        """Create a new game"""
        user = models.User.query(models.User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException('A User with that name does not exist!')

        if request.cities_total > gl.MAX_CITY_QUESTIONS:
            raise endpoints.BadRequestException('Max number of cities is {}'.format(gl.MAX_CITY_QUESTIONS))

        if not set(request.regions).issubset(models.City.get_available_regions()):
            raise endpoints.BadRequestException('Region(s) requested are not available.')

        game = models.Game.new_game(user, request.regions, request.cities_total)
        game_score = models.Score.new_score(user.key, game.key)

        return game.to_form('New game created.  Best of luck!')

    # TODO: maybe deprecate this in favor a of a "next_move" options.
    # next_move should determine whether to create new question.
    # Alt, it could be 'get question' - either gets current active, or creates new.
    @endpoints.method(
        request_message=QUESTION_GET_REQUEST,
        response_message=forms.CityQuestionForm,
        path='get_question',
        name='get_question',
        http_method='GET'
    )
    def get_question(self, request):
        """Request question for a game.  Returns active or next question."""
        game = utils.get_by_urlsafe(request.websafe_game_key, models.Game)

        if game.game_over:
            raise endpoints.BadRequestException('Game is already over!  Try another one!')

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

    @endpoints.method(
        request_message=QUESTION_ATTEMPT_POST_REQUEST,
        response_message=forms.CityQuestionForm,
        path='submit_question_guess',
        name='submit_question_guess',
        http_method='POST'
    )
    def submit_question_guess(self, request):
        """
        - request: ws question key and guess string.

        # TODO:
        functionality to handle (in models and game_logic):
        - check if question is still active, respond accordingly.
        - check number of attempts, respond accordingly.
        - check if guess is correct.  (make both to lower case)
            - Update guess history.
            - if incorrect, decrement attempts remaining.  send response.  More property info, and a string message.  (either default, or actual distance.)
            - if correct, RECORD SCORE, make question inactive.
                - check if GAME should be over.  Make game inactive, send response accordingly.

        """
        question = utils.get_by_urlsafe(request.websafe_question_key, models.CityQuestion)
        guess = request.city_guess

        if question.question_over:
            return question.to_form('This question is resolved!  Try another question.')

        game_over, question_over, correct = gl.manage_city_question_attempt(question, guess)

        message = 'Your guess: ' + guess
        if correct:
            message += '<br><br>Correct!  Good job!'
        else:
            message += '<br><br>Wrong answer!'

        if question_over and not correct:
            message += '<br><br>Out of attempts!  The correct answer was: ' + question.city_name

        if game_over:
            message += '<br><br>Game over!  Start a new game!'

        return question.to_form(message)


api = endpoints.api_server([GuessLocationApi])
