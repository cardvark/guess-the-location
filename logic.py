#!/usr/bin/env python

"""
Game logic, including API calls to Foursquare.

Guess the location game server-side Python App Engine

"""
import requests
import json
import pprint
import random

from settings import FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET


def get_monument_by_city(city, count):
    api_url = 'https://api.foursquare.com/v2/venues/explore'
    params = {
        'near': city,
        'query': 'Monument',
        'client_id': FOURSQUARE_CLIENT_ID,
        'client_secret': FOURSQUARE_CLIENT_SECRET,
        'venuePhotos': 1,
        'v': '20130815'
    }

    # Get call to Foursquare API
    try:
        response = requests.get(api_url, params=params)
    except requests.exceptions.RequestException as e:
        print e

    response = response.json()

    try:
        # Skips down to the items list.
        monuments_list = response.get('response').get('groups')[0].get('items')
    except:
        raise Exception('Incorrect data structure in json response.')

    monument = random.choice(monuments_list[0:count])
    monument_venue = monument.get('venue')

    img_size = '200x200'
    img_prefix = monument_venue.get('featuredPhotos').get('items')[0].get('prefix')
    img_suffix = monument_venue.get('featuredPhotos').get('items')[0].get('suffix')

    monument_dict = {
        'name': monument_venue.get('name'),
        'lat': monument_venue.get('location').get('lat'),
        'lng': monument_venue.get('location').get('lng'),
        'url': monument.get('tips')[0].get('canonicalUrl'),
        'img_url': img_prefix + img_size + img_suffix
    }

    return monument_dict
