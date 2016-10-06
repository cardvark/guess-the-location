#!/usr/bin/env python

"""

foursquareApi.py - call functions to Foursquare API

Guess the location game server-side Python App Engine

"""
import requests
import requests_toolbelt.adapters.appengine
# import json
# import random

from settings import FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET

requests_toolbelt.adapters.appengine.monkeypatch()


def get_url_from_id(venue_id):
    print 'Getting url for ' + venue_id
    api_url = 'https://api.foursquare.com/v2/venues/' + venue_id
    params = {
        'client_id': FOURSQUARE_CLIENT_ID,
        'client_secret': FOURSQUARE_CLIENT_SECRET,
        'v': '20130815'
    }

    try:
        response = requests.get(api_url, params=params)
    except requests.exceptions.RequestException as e:
        print e

    response = response.json()
    response = response.get('response')
    venue = response.get('venue')
    url = venue.get('canonicalUrl')

    return url


def monuments_by_city(city):
    api_url = 'https://api.foursquare.com/v2/venues/explore'
    params = {
        'near': city,
        'query': 'Monument',
        'client_id': FOURSQUARE_CLIENT_ID,
        'client_secret': FOURSQUARE_CLIENT_SECRET,
        'venuePhotos': 1,
        'v': '20130815'
    }
    # query_params = urllib.urlencode(params)

    # Get call to Foursquare API
    # try:
    #     response = urllib2.Request(api_url, query_params)
    # except urllib2.URLError:
    #     print 'Caught exception fetching monuments_by_city'
    #     return

    # response = json.load(response)
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

    output_list = []
    for monument in monuments_list:
        monument_venue = monument.get('venue')
        image = True

        try:
            img_prefix = monument_venue.get('featuredPhotos').get('items')[0].get('prefix')
            img_suffix = monument_venue.get('featuredPhotos').get('items')[0].get('suffix')
        except:
            image = False
            print 'No image, skipping ' + monument_venue.get('name')

        page_id = monument_venue.get('id')
        page_url = monument.get('tips')

        # 'tips' only exist if user posted a tip.
        # Without a tip, page url isn't listed in explore response.
        # Must do a specific page request to obtain the 'canonicalUrl'

        if image:
            if page_url:
                page_url = page_url[0].get('canonicalUrl')
            else:
                page_url = get_url_from_id(page_id)

            monument_dict = {
                'fsq_id': page_id,
                'name': monument_venue.get('name'),
                'lat': monument_venue.get('location').get('lat'),
                'lng': monument_venue.get('location').get('lng'),
                'url': page_url,
                'img_prefix': img_prefix,
                'img_suffix': img_suffix
            }
            output_list.append(monument_dict)

    return output_list
