#!/usr/bin/env python

"""
main.py -- Guess the location game server-side Python App Engine
HTTP controller handlers.

$Id$

created by James Wang, 2016-09-29

"""

__author__ = 'wang.james.j@gmail.com'

import webapp2
import sys
# from google.appengine.api import app_identity
# from google.appengine.api import mail
from google.appengine.api import taskqueue
from api import GuessLocationApi
import models
import foursquareApi as fApi
import utils
import game_logic as gl
from google.appengine.ext import ndb
# import random

reload(sys)
sys.setdefaultencoding('utf-8')


class BuildCityDataHandler(webapp2.RequestHandler):
    def get(self):
        """Builds the datastore City entities"""

        ndb.delete_multi(models.City.query().fetch(keys_only=True))

        for city_list in models.CITIES_LIST:
            models.City.add_city(city_list[0], city_list[1], city_list[2])


class BuildMonumentsDataHandler(webapp2.RequestHandler):
    def get(self):
        """Builds Monument entities via Foursquare API"""
        # TODO: potentially remove monuments not in the API results.

        cities_list = models.City.query().fetch()
        for city in cities_list:
            print '------------------------------------------------------'
            print city.city_name

            monuments_list = fApi.monuments_by_city(city.city_name)

            for monument in monuments_list:
                mon = models.Monument.add_monument(monument, city.key)
                print city.city_name, mon.name


# class CronTasksHandler(webapp2.RequestHandler):
#     """Cron jobs into taskqueue"""
#     taskqueue.add(url='/jobs/build_monuments_data')


class PlayGroundHandler(webapp2.RequestHandler):
    def get(self):
        """General testing ground"""
        # print models.City.get_available_regions()

        possible_cities = models.City.get_cities_by_regions(['North America'])

        i = 50
        while i > 0:
            new_city_key = gl.get_unique_random_key([], possible_cities)
            print new_city_key.get().city_name
            i -= 1

        # game_results = models.Game.get_all_games(game_over=True, keys_only=True)
        # # print game_results

        # score_results = models.Score.get_top_scores()

        # output_list = []
        # for score in score_results:
        #     if score.key.parent() in game_results:
        #         output_list.append(score)

        # print output_list[0:3]


        # game = utils.get_by_urlsafe('aghkZXZ-Tm9uZXIRCxIER2FtZRiAgICAgODPCAw', models.Game)

        # question = utils.get_by_urlsafe('aghkZXZ-Tm9uZXIqCxIER2FtZRiAgICAgODXCgwLEgxDaXR5UXVlc3Rpb24YgICAgIDg9woM', models.CityQuestion)
        # print question.question_over
        # question.end_question()
        # print question.question_over
        # question.question_over = False
        # question.put()
        # print question.question_over

        # print question.city_name
        # print question.key.parent().get()

        # print game.last_cities
        # print game.monuments_list

        # new_city_question = gl.get_new_city_question(game)

        # question = game.active_question.get()
        # question.attempts_remaining = 3
        # question.put()
        # print question.city_name, question.monument.get().name
        # print question.to_form('Hey, that worked')

        # gl.evaluate_question_response(question)
        # print new_city_question
        # print new_city_question.city_name, new_city_question.monument.get().name
        # print monument_key

        # print game
        # print game.cities_total
        # print game.user
        # print game.regions


        # cities = models.City.get_cities_by_regions(['Asia', 'North America', 'Europe'])

        # city = random.choice(cities)
        # print city.key, city.city_name

        # for city in cities:
        #     print city.key, city.city_name


        # Get by ancestor works!
        # city = City.get_city('San Francisco', 'United States', 'North America')

        # monuments = city.get_monuments()
        # # print monuments
        # for monument in monuments:
        #     print monument.name


app = webapp2.WSGIApplication([
    ('/jobs/build_city_data', BuildCityDataHandler),
    ('/crons/build_monuments_data', BuildMonumentsDataHandler),
    # ('/crons/task_trigger', CronTasksHandler),
    ('/jobs/playground', PlayGroundHandler)
], debug=True)
