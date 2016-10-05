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

NEW_USER_POST_REQUEST = endpoints.ResourceContainer(forms.UserForm)
NEW_GAME_POST_REQUEST = endpoints.ResourceContainer(forms.NewGameForm)
QUESTION_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafe_game_key=messages.StringField(1, required=True)
)
QUESTION_ATTEMPT_POST_REQUEST = endpoints.ResourceContainer(
    forms.QuestionAttemptForm,
    websafe_question_key=messages.StringField(1, required=True)
)
# USER_GAMES_GET_REQUEST = endpoints.ResourceContainer(
#     forms.UserGamesForm
# )


@endpoints.api(
    name='guess_the_location',
    version='v1',
    allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
    scopes=[EMAIL_SCOPE]
)
class GuessLocationApi(remote.Service):
    """Guess the location game API"""

    @endpoints.method(
        request_message=NEW_USER_POST_REQUEST,
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
        request_message=NEW_GAME_POST_REQUEST,
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
        """Submit question and guess. Updates CityQuestion, Game, Score."""
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

    @endpoints.method(
        request_message=forms.UserGamesForm,
        response_message=forms.GameForms,
        path='get_games_by_user',
        name='get_games_by_user',
        http_method='GET'
    )
    def get_games_by_user(self, request):
        """Get list of games (active or all) by user_name."""
        user = models.User.query(models.User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException('A User with that name does not exist!')

        games = models.Game.get_games_by_user(user, request.all_games)
        active_message = ''
        if not request.all_games:
            active_message = 'active '

        if not games:
            raise endpoints.NotFoundException('No {}games found!'.format(active_message))

        games_message = '{user_name} {active}games found!'.format(
            user_name=request.user_name,
            active=active_message)

        form_items = [game.to_form() for game in games]

        return forms.GameForms(items=form_items, message=games_message)


    # To be implemented:
    # get_user_games - active games.  (all games?  maybe a bool check in request.)
    # cancel_game - cancels game in progress.  boolean property for cancelled?
    # get_high_scores - descending order.  optional param "number_of_results" to limit # of results returned.
    # get_user_rankings - all users ranked by performance.  Includes name and performance indicator. win/loss ratio or some such.
    # get_game_history - provides history of moves (with responses) for each game.

    # cron job of some kinds.  and notifications.
    # full readme
    # Design thoughts in Design.txt

api = endpoints.api_server([GuessLocationApi])
