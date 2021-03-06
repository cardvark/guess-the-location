#!/usr/bin/env python

"""
game_logic.py - game logic functions

Guess the location game server-side Python App Engine


Rules:
- A game can have a variable number of city questions, max 5
- Choose the region(s) you want cities from.
- You have 3 tries to answer a City Question.  Information is increased with each incorrect guess.
    - 1) Roads, min zoom: 16 (0)
    - 2) Marker and image, min zoom 12 (1)
    - 3) Monument name, min zoom out 6 (2)
- If failed, set zoom to 4 and city name.
- Score is based on how many tries.
- Score bonus applied for number of potential cities. (increases with more regions selected on game creation)

"""

import models
import random
from google.appengine.api import taskqueue

# Game constants
SCORE_DICT = {
    2: 10,
    1: 5,
    0: 2
}

MINZOOM_DICT = {
    3: 16,
    2: 12,
    1: 6,
    0: 4
}

MONUMENT_PROPERTIES_UNLOCKS_DICT = {
    3: ['lat', 'lng'],
    2: ['img_prefix', 'img_suffix'],
    1: ['name'],
    0: ['url']
}

RECENT_CITIES_LIMIT = 3  # prevents duplicate city question for at least 3
MAX_CITY_QUESTIONS = 5  # Max 5 city questions per game
QUESTION_ATTEMPTS = 3  # Max 3 guess attempts per city question.
MINIMUM_QUESTIONS_RANKING = 5  # Min number of questions to be ranked


def calculate_bonus(score):
    """Calculate bonus to score based on total possible cities in a game"""
    parent_game = score.key.parent().get()
    possible_cities = models.City.get_cities_by_regions(parent_game.regions)

    bonus = 1 + len(possible_cities) / 100.0

    return bonus


def update_recent_cities(new_city_key, recent_cities):
    """Update Game recent cities list"""
    recent_cities.append(new_city_key)

    if len(recent_cities) >= RECENT_CITIES_LIMIT:
        recent_cities = recent_cities[-RECENT_CITIES_LIMIT:]

    return recent_cities


def get_unique_random_key(prev_list, possible_list):
    """Return a random item from possible_list that was not in prev_list

    :param prev_list: list of urlsafe keys
    :param possible_list: list of entities
    :return: key of random item from possible_list
    """
    found = False

    while not found:
        new_item = random.choice(possible_list)
        new_item_key = new_item.key

        if new_item_key.urlsafe() not in prev_list:
            found = True

    return new_item_key


def get_new_city_question(game):
    """Build and return a new CityQuestion entity"""
    # Gather game object data.
    recent_cities = game.last_cities
    previous_monuments = game.monuments_list

    # Get a new city.
    possible_cities = models.City.get_cities_by_regions(game.regions)
    new_city_key = get_unique_random_key(recent_cities, possible_cities)
    recent_cities = update_recent_cities(new_city_key.urlsafe(), recent_cities)

    # Get a monument.
    monuments_list = models.Monument.get_monuments_from_parent(new_city_key)

    # Safeguards against chance that City has no Monuments
    # TODO: implement logging / monitoring to ensure Foursquare API cron job
    # always triggers correctly, avoid this necessity.
    while not monuments_list:
        monuments_list = models.Monument.get_monuments_from_parent(new_city_key)

    new_monument_key = get_unique_random_key(previous_monuments, monuments_list)

    # Create new city question
    new_city_question = models.CityQuestion.new_city_question(
        game.key,
        new_city_key.get().city_name,
        new_monument_key,
        QUESTION_ATTEMPTS
    )

    # Update game
    game.new_question_update(
        recent_cities,
        new_monument_key,
        new_city_question.key
        )

    return new_city_question


def get_allowed_properties(city_question):
    """Return form properties based on attempts remaining or question over"""
    allowed_list = []
    start_value = 0 if city_question.question_over else city_question.attempts_remaining

    for i in range(start_value, city_question.attempts_allowed + 1):
        allowed_list += MONUMENT_PROPERTIES_UNLOCKS_DICT[i]

    return allowed_list


def check_city_question_guess(city_question, guess):
    """Compare correct city with user guess, returns boolean and message"""
    correct_city = city_question.city_name.lower()
    user_guess = guess.lower()

    return correct_city == user_guess


def manage_city_question_attempt(city_question, guess):
    """Evaluate user guess, update data and respond accordingly"""
    game_over = False
    question_over = False
    guess_correct = check_city_question_guess(city_question, guess)
    parent_game = city_question.key.parent().get()
    attempts_remaining = city_question.guess_update(guess)

    if guess_correct or attempts_remaining <= 0:
        city_question.end_question(guess_correct)
        question_points = get_question_points(city_question)
        question_over = True
        game_score = models.Score.get_from_parent(parent_game.key)
        game_score.update_score(question_points)
        game_over = parent_game.end_question_update()

        if game_over:
            # Recalculates and caches user rankings
            taskqueue.add(url='/jobs/cache_user_rankings')
            parent_game.end_game()

    return game_over, question_over, guess_correct


def get_question_points(city_question):
    """Evaluate question for points received"""
    score = 0
    if city_question.guessed_correct:
        score = SCORE_DICT[city_question.attempts_remaining]

    return score


def avg_guess_rate(user, all_questions):
    """Calculate avg number of guesses per question for a user"""
    guess_attempts_list = []
    for question in all_questions:
        guess_attempts = question.attempts_allowed - question.attempts_remaining
        guess_attempts_list.append(guess_attempts)

    return float(sum(guess_attempts_list)) / len(guess_attempts_list)


def get_all_questions(user):
    """Retrieve list of all questions a user has answered"""
    completed_games = models.Game.get_all_games(user=user, game_over=True, completed=True)

    all_questions = []
    for game in completed_games:
        questions_list = models.CityQuestion.get_questions_from_parent(game.key)
        all_questions += questions_list

    return all_questions


def get_user_rankings():
    """Retrieve user rankings by avg guess rate"""
    all_users = models.User.query().fetch()
    rankings_list = []

    for user in all_users:
        print user.name
        all_questions = get_all_questions(user)
        questions_count = len(all_questions)
        print questions_count
        if questions_count < MINIMUM_QUESTIONS_RANKING:
            continue

        avg_attempts = avg_guess_rate(user, all_questions)
        if avg_attempts is not None:
            rankings_list.append({
                'user_name': user.name,
                'guess_rate': avg_attempts,
                'questions_count': questions_count
            })

    rankings_list = sorted(rankings_list, key=lambda x: x['guess_rate'])

    return rankings_list


def get_last_move_time(game):
    """Find the last time the user made a move on a game"""
    if game.active_question:
        return game.active_question.get().date

    return game.last_modified


def filter_games_by_time(games, min_time, max_time):
    """Filter list of games by min and max times user last made a move"""

    def filter_function(game):
        last_move_time = get_last_move_time(game)
        if not last_move_time:
            return False

        return max_time < last_move_time and last_move_time <= min_time

    filtered_games = filter(filter_function, games)

    return filtered_games
