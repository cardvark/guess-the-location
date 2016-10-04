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
import endpoints

# Game constants
SCORE_DICT = {
    3: 10,
    2: 5,
    1: 2,
    0: 0
}

# TODO: Implement use of this dict.
MINZOOM_DICT = {
    3: 16,
    2: 12,
    1: 6,
    0: 4
}

# TODO: Not sure how this'll work yet.
MONUMENT_PARAM_UNLOCKS_DICT = {
    3: ['lat', 'lng'],
    2: ['img_prefix', 'img_suffix'],
    1: ['name'],
    0: ['url']
}

RECENT_CITIES_LIMIT = 3  # prevents duplicate city question for at least 3
MAX_CITY_QUESTIONS = 5  # Max 5 city questions per game
QUESTION_ATTEMPTS = 3  # Max 3 guess attempts per city question.


# TODO: set game_over status to true upon final question result.
# TODO: Update a score for a question upon each question completion.

def update_recent_cities(new_city_key, recent_cities):
    recent_cities.append(new_city_key)

    if len(recent_cities) >= RECENT_CITIES_LIMIT:
        recent_cities = recent_cities[-RECENT_CITIES_LIMIT:]

    return recent_cities


# TODO: further testing. want to ensure this is working as intended.
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
    cities_asked = game.cities_asked
    recent_cities = game.last_cities
    game_over_status = game.game_over
    previous_monuments = game.monuments_list

    if game_over_status:
        raise endpoints.BadRequestException('Game is already over!  Pick another.')

    # Get a new city.
    possible_cities = models.City.get_cities_by_regions(game.regions)
    new_city_key = get_unique_random_key(recent_cities, possible_cities)
    recent_cities = update_recent_cities(new_city_key.urlsafe(), recent_cities)

    # Get a monument.
    monuments_list = new_city_key.get().get_monuments()
    new_monument_key = get_unique_random_key(previous_monuments, monuments_list)
    previous_monuments.append(new_monument_key.urlsafe())

    # Create new city question
    new_city_question = models.CityQuestion.new_city_question(
        game.key,
        new_city_key.get().city_name,
        new_monument_key,
        QUESTION_ATTEMPTS
    )

    # Update the game's data
    game.last_cities = recent_cities
    game.cities_asked = cities_asked + 1
    game.monuments_list = previous_monuments
    game.active_question = new_city_question.key
    game.put()

    print new_city_key.get().city_name
    print new_monument_key.get().name

    return new_city_question


# TODO: pass to user map and info parameters based on # of tries / attempts remaining.
def create_question_response(city_question):
    """ Take CityQuestion entity, return appropriate response based on entity

    - websafe key for the CityQuestion
    - lat, lng floats
    - minZoom (dependent on attempts_remaining)
    """
    pass


def check_city_question_attempt(city_question, guess):
    pass
