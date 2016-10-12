#!/usr/bin/env python

"""

foursquareApi.py - call functions to Foursquare API

Guess the location game server-side Python App Engine

"""
import requests
import requests_toolbelt.adapters.appengine
import logging

from settings import FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET

requests_toolbelt.adapters.appengine.monkeypatch()


def get_url_from_id(venue_id):
    out_msg = 'Getting url for ' + venue_id
    print out_msg
    logging.debug(out_msg)

    api_url = 'https://api.foursquare.com/v2/venues/' + venue_id
    params = {
        'client_id': FOURSQUARE_CLIENT_ID,
        'client_secret': FOURSQUARE_CLIENT_SECRET,
        'v': '20130815'
    }

    try:
        response = requests.get(api_url, params=params)
    except requests.exceptions.RequestException as err:
        print err
        logging.error(err)

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

    try:
        response = requests.get(api_url, params=params)
    except requests.exceptions.RequestException as err:
        print err
        logging.error(err)

    response = response.json()

    try:
        # Skips down to the items list.
        monuments_list = response.get('response').get('groups')[0].get('items')
    except:
        logging.error('Incorrect data structure in json for ' + city)
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
            no_img_msg = 'No image, skipping ' + monument_venue.get('name')
            print no_img_msg
            logging.debug(no_img_msg)

        page_id = monument_venue.get('id')
        page_url = monument.get('tips')  # 'tips' only exist if user posted a tip.

        if image:
            if page_url:
                page_url = page_url[0].get('canonicalUrl')
            else:
                # Without a tip, page url isn't listed in venues/explore response.
                # Must make a specific page request to obtain the 'canonicalUrl'
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
