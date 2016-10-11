# -*- coding: utf-8 -*-`
"""
api.py - game APIs.

Guess the location game server-side Python App Engine

Error checking for user inputs primarily handled here.

"""
# External libraries
import logging
import endpoints
from protorpc import remote, messages, message_types
from google.appengine.api import memcache
from google.appengine.api import taskqueue

# Internal modules
import foursquareApi as fApi
import models
import game_logic as gl
import utils
import forms
from settings import *

# Ensures all characters can be handled (foreign language covered)
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID

MEMCACHE_USER_RANKINGS = 'USER_RANKINGS'

GAME_KEY_GET_CONTAINER = endpoints.ResourceContainer(
    message_types.VoidMessage,
    urlsafe_game_key=messages.StringField(1, required=True)
)
QUESTION_ATTEMPT_POST_CONTAINER = endpoints.ResourceContainer(
    forms.QuestionAttemptForm,
    urlsafe_question_key=messages.StringField(1, required=True)
)


@endpoints.api(
    name='guess_the_location',
    version='v1',
    # allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
    # scopes=[EMAIL_SCOPE]
)
class GuessLocationApi(remote.Service):
    """Guess the location game API"""

    @endpoints.method(
        request_message=forms.UserForm,
        response_message=forms.UserForm,
        path='user',
        name='create_user',
        http_method='POST'
    )
    def create_user(self, request):
        """Create a User.  Requires unique username
        :param request: user_name, email.
        """
        if models.User.query(models.User.name == request.user_name).get():
            raise endpoints.ConflictException('A user with that name already exists!')

        user = models.User.add_user(request.user_name, request.email)
        return forms.UserForm(user_name=user.name, email=user.email)

    @endpoints.method(
        request_message=forms.NewGameForm,
        response_message=forms.GameForm,
        path='game',
        name='new_game',
        http_method='POST'
    )
    def new_game(self, request):
        """Create a new game
        :param request: user_name, regions, cities_total
        """
        user = models.User.query(models.User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException('A User with that name does not exist!')

        if request.cities_total < 1:
            raise endpoints.BadRequestException('Must have at least 1 city.')

        if request.cities_total > gl.MAX_CITY_QUESTIONS:
            raise endpoints.BadRequestException('Max number of cities is {}'.format(gl.MAX_CITY_QUESTIONS))

        if not set(request.regions).issubset(models.City.get_available_regions()):
            raise endpoints.BadRequestException('Region(s) requested are not available.')

        game = models.Game.new_game(user, request.regions, request.cities_total)
        game_score = models.Score.new_score(user.key, game.key)

        return game.to_form('New game created.  Best of luck!')

    @endpoints.method(
        request_message=GAME_KEY_GET_CONTAINER,
        response_message=forms.QuestionResponseForm,
        path='get_question',
        name='get_question',
        http_method='GET'
    )
    def get_question(self, request):
        """Request question for a game.  Returns active or next question.
        :param request: urlsafe_game_key
        """
        game = utils.get_by_urlsafe(request.urlsafe_game_key, models.Game)

        if game.game_over:
            raise endpoints.BadRequestException('Game is already over!  Try another one!')

        if game.active_question:
            question = game.active_question.get()
            message = 'Active question in progress!'
        else:
            question = gl.get_new_city_question(game)
            message = 'New question!  Good luck!'

        return gl.evaluate_question_response_form(question, message)

    @endpoints.method(
        request_message=QUESTION_ATTEMPT_POST_CONTAINER,
        response_message=forms.QuestionResponseForm,
        path='submit_question_guess',
        name='submit_question_guess',
        http_method='POST'
    )
    def submit_question_guess(self, request):
        """Submit question and guess. Updates CityQuestion, Game, Score.
        :param request: urlsafe_question_key, city_guess
        """
        question = utils.get_by_urlsafe(request.urlsafe_question_key, models.CityQuestion)
        guess = request.city_guess

        if question.question_over:
            message = 'This question is resolved!  Try another question.  Answer was: ' + question.city_name
            return gl.evaluate_question_response_form(question, message)

        # Shouldn't occur; question should be over before this case can arise.
        if question.attempts_remaining <= 0:
            raise endpoints.BadRequestException('No attempts remaining!')

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

        return gl.evaluate_question_response_form(question, message)

    @endpoints.method(
        request_message=forms.UserGamesRequestForm,
        response_message=forms.GameForms,
        path='get_games_by_user',
        name='get_games_by_user',
        http_method='GET'
    )
    def get_games_by_user(self, request):
        """Get list of games (active or all) by user_name.
        :param request: user_name, game_over
        """
        user = models.User.query(models.User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException('A User with that name does not exist!')

        games = models.Game.get_all_games(user=user, game_over=request.game_over)
        active_message = ''
        if request.game_over:
            active_message += 'completed '
        elif request.game_over is False:
            active_message += 'active '

        if not games:
            raise endpoints.NotFoundException('No {}games found!'.format(active_message))

        games_message = 'User: {user_name} -- {active}games found!'.format(
            user_name=request.user_name,
            active=active_message)

        form_items = [game.to_form() for game in games]

        return forms.GameForms(items=form_items, message=games_message)

    @endpoints.method(
        request_message=forms.GameKeyRequestForm,
        response_message=forms.GameForm,
        path='cancel_game',
        name='cancel_game',
        http_method='POST'
    )
    def cancel_game(self, request):
        """Cancels game in progress
        :param request: urlsafe_game_key
        """
        game = utils.get_by_urlsafe(request.urlsafe_game_key, models.Game)

        if game.game_over:
            return game.to_form('Game is already over!')

        if game.active_question:
            game.end_question_update()

        game.end_game()

        return game.to_form('Game canceled.')

    @endpoints.method(
        request_message=forms.MaxResultsRequestForm,
        response_message=forms.ScoreForms,
        path='get_high_scores',
        name='get_high_scores',
        http_method='GET'
    )
    def get_high_scores(self, request):
        """List of high scores per game
        :param request: max_results (optional)
        :return: Top games by score, Score and User name.
        """
        inactive_games = models.Game.get_all_games(game_over=True, keys_only=True)
        score_results = models.Score.get_top_scores()
        top_scores_list = []
        for score in score_results:
            if score.key.parent() in inactive_games:
                top_scores_list.append(score.to_form())

        if not top_scores_list:
            raise endpoints.NotFoundException('No completed game scores found!')

        return forms.ScoreForms(items=top_scores_list[0:request.max_results], message='Top scores')

    @staticmethod
    def _cache_user_rankings():
        """Populates memcache with rankings by avg guess rate"""
        print 'Auto caching'
        rankings_list = gl.get_user_rankings()
        memcache.set(MEMCACHE_USER_RANKINGS, rankings_list)

    @endpoints.method(
        request_message=forms.MaxResultsRequestForm,
        response_message=forms.UserRankForms,
        path='get_user_rankings',
        name='get_user_rankings',
        http_method='GET'
    )
    def get_user_rankings(self, request):
        """List of users by ranking metric (guess_rate)
        :param request: max_results (optional)
        :return: Top users by ranking metric.
        """
        rankings_list = memcache.get(MEMCACHE_USER_RANKINGS)
        message = 'User Rankings'

        if not rankings_list:
            print 'Manual Caching'
            rankings_list = gl.get_user_rankings()
            memcache.set(MEMCACHE_USER_RANKINGS, rankings_list)

        if request.max_results:
            rankings_list = rankings_list[0:request.max_results]
            message += ' - limited to top {}'.format(request.max_results)

        form_list = []
        for user_dict in rankings_list:
            form = forms.UserRankForm(
                user_name=user_dict['user_name'],
                guess_rate=user_dict['guess_rate'],
                questions_count=user_dict['questions_count']
            )
            form_list.append(form)

        return forms.UserRankForms(items=form_list, message=message)

    def _extract_guesses_from_question(self, question):
        """Extract guesses and build guess form list from a question"""
        guess_history = question.guess_history
        guess_form_list = []

        for guess in guess_history:
            guess_form = forms.GuessResponseForm()
            guess_form.user_guess = guess
            guess_form.guessed_correct = gl.check_city_question_guess(question, guess)

            guess_form_list.append(guess_form)

        return guess_form_list

    def _extract_questions_from_game(self, game):
        """Extract questions and build questions form list from a game"""
        questions_list = models.CityQuestion.get_questions_from_parent(game.key, ordered=True)
        question_form_list = []

        for question in questions_list:
            question_form = forms.QuestionHistoryForm()
            question_form.city_name = question.city_name
            question_form.monument_name = question.monument.get().name
            if question.question_over:
                question_form.question_score = gl.get_question_points(question)

            question_form.guess_responses = self._extract_guesses_from_question(question)

            question_form_list.append(question_form)

        return question_form_list

    # TODO: get the questions and responses sorted in the right order.

    @endpoints.method(
        request_message=GAME_KEY_GET_CONTAINER,
        response_message=forms.GameHistoryForm,
        path='get_game_history',
        name='get_game_history',
        http_method='GET'
    )
    def get_game_history(self, request):
        """Get a game's guess and response history
        :param request: urlsafe_game_key
        """
        game = utils.get_by_urlsafe(request.urlsafe_game_key, models.Game)
        game_form = forms.GameHistoryForm()

        game_form.user_name = game.user.get().name
        game_form.regions = game.regions

        score_object = models.Score.get_from_parent(game.key)
        game_form.total_score = score_object.total_score
        game_form.game_over = game.game_over
        if game.game_over:
            game_form.bonus_modifier = gl.calculate_bonus(score_object)
            game_form.bonus_score = score_object.bonus_score

        game_form.question_history = self._extract_questions_from_game(game)

        return game_form


    # To be implemented:
    # get_game_history - provides history of moves (with responses) for each game.

    # cron job of some kinds.  and notifications.
    # full readme
    # Design thoughts in Design.txt

api = endpoints.api_server([GuessLocationApi])
