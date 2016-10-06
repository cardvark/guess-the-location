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

"""

import models
import random

# Game constants
SCORE_DICT = {
    2: 10,
    1: 5,
    0: 2
}

# TODO: Implement use of this dict.
MINZOOM_DICT = {
    3: 16,
    2: 12,
    1: 6,
    0: 4
}

# TODO: Not sure how this'll work yet.
MONUMENT_PROPERTIES_UNLOCKS_DICT = {
    3: ['lat', 'lng'],
    2: ['img_prefix', 'img_suffix'],
    1: ['name'],
    0: ['url']
}

RECENT_CITIES_LIMIT = 3  # prevents duplicate city question for at least 3
MAX_CITY_QUESTIONS = 5  # Max 5 city questions per game
QUESTION_ATTEMPTS = 3  # Max 3 guess attempts per city question.


def update_recent_cities(new_city_key, recent_cities):
    """Update Game recent cities list"""
    recent_cities.append(new_city_key)

    if len(recent_cities) >= RECENT_CITIES_LIMIT:
        recent_cities = recent_cities[-RECENT_CITIES_LIMIT:]

    return recent_cities


def get_unique_random_key(prev_list, possible_list):
    """Return a random item from possible_list that was not in prev_list

    :param prev_list: list of websafe keys
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
    monuments_list = new_city_key.get().get_monuments()
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


def evaluate_question_response(city_question, form):
    """Evaluate appropriate response based on CityQuestion entity properties

    :param city_question: CityQuestion object
    :param form: QuestionResponseForm object
    :return: form with allowed monument properties, min zoom and score if question_over.

    """
    monument = city_question.monument.get()
    allowed_properties = get_allowed_properties(city_question)

    setattr(form, 'min_zoom', MINZOOM_DICT[city_question.attempts_remaining])
    if city_question.question_over:
        parent_game = city_question.key.parent().get()
        setattr(form, 'question_score', get_question_points(city_question))
        setattr(form, 'min_zoom', MINZOOM_DICT[0])
        setattr(form, 'cities_remaining', parent_game.cities_remaining)
        setattr(form, 'guessed_correct', city_question.guessed_correct)
        if parent_game.game_over:
            score_object = models.Score.get_from_parent(parent_game.key)
            setattr(form, 'total_score', score_object.total_score)
            setattr(form, 'game_over', True)

    for prop in allowed_properties:
        setattr(form, prop, getattr(monument, prop))

    return form


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
        # To be implemented, somehow:
        game_score = models.Score.get_from_parent(parent_game.key)
        game_score.update_score(question_points)
        game_over = parent_game.end_question_update()

        if game_over:
            parent_game.end_game()

    return game_over, question_over, guess_correct


def get_question_points(city_question):
    """Evaluate question for points received"""
    score = 0
    if city_question.guessed_correct:
        score = SCORE_DICT[city_question.attempts_remaining]

    return score
