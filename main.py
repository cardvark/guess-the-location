#!/usr/bin/env python

"""
main.py -- Guess the location game server-side Python App Engine
HTTP controller handlers.

$Id$

created by James Wang, 2016-09-29

"""

__author__ = 'wang.james.j@gmail.com'

import webapp2
import logging
import datetime

# from google.appengine.api import app_identity
# from google.appengine.api import mail
from api import GuessLocationApi
import models
import foursquareApi as fApi
import game_logic as gl
from google.appengine.ext import ndb
from google.appengine.api import mail, app_identity

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

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

            if not monuments_list:
                logging.error('No monuments found for ' + city.city_name)

            for monument in monuments_list:
                mon = models.Monument.add_monument(monument, city.key)
                log_msg = '{city}, {monument}'.format(city=city.city_name, monument=mon.name)
                logging.debug(log_msg)
                # print city.city_name, mon.name


class UpdateUserRankingsCache(webapp2.RequestHandler):
    def post(self):
        """Update user rankings list in memcache"""
        GuessLocationApi._cache_user_rankings()
        self.response.set_status(204)


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send reminder email to user regarding unfinished games.  Runs hourly, checks for games without movement for X hours"""
        min_inactive = 0.1  # hours inactive
        max_inactive = 48 # none older than these hours.

        now = datetime.datetime.now()
        min_time = now - datetime.timedelta(hours=min_inactive)
        max_time = now - datetime.timedelta(hours=max_inactive)

        app_id = app_identity.get_application_id()
        valid_users = models.User.get_all_users(email_only=True, keys_only=True)
        incomplete_games = models.Game.get_all_games(game_over=False, completed=False)
        filtered_games = gl.filter_games_by_time(incomplete_games, min_time, max_time)

        for game in filtered_games:
            if game.user in valid_users:
                user = game.user.get()
                print user.name
                print gl.get_last_move_time(game)

                subject = 'Make a move!  Guess the location city!'
                body = 'Hey {}, you\'ve got moves left on your guess the locatio game!'.format(user.name)
                body += '\n\n'
                body += 'Game key: ' + game.key.urlsafe()
                if game.active_question:
                    body += '\nActive question key: ' + game.active_question.urlsafe()
                body += '\nQuestions remaining: ' + str(game.cities_remaining)
                body += '\n\n'
                body += 'https://guess-the-location.appspot.com/'

                mail.send_mail(
                    'noreply@{}.appspotmail.com'.format(app_id),
                    user.email,
                    subject,
                    body
                )


# class CronTasksHandler(webapp2.RequestHandler):
#     """Cron jobs into taskqueue"""
#     taskqueue.add(url='/jobs/build_monuments_data')


class PlayGroundHandler(webapp2.RequestHandler):
    def get(self):
        """General testing ground"""
        min_inactive = 0.1  # hours inactive
        max_inactive = 48 # none older than these hours.

        now = datetime.datetime.now()
        min_time = now - datetime.timedelta(hours=min_inactive)
        max_time = now - datetime.timedelta(hours=max_inactive)

        app_id = app_identity.get_application_id()
        valid_users = models.User.get_all_users(email_only=True, keys_only=True)
        incomplete_games = models.Game.get_all_games(game_over=False, completed=False)
        filtered_games = gl.filter_games_by_time(incomplete_games, min_time, max_time)

        # Game filtering seems to work.
        # TODO:
        # Next - filter further via valid users.
        # then figure out email message.

        for game in filtered_games:
            if game.user in valid_users:
                user = game.user.get()
                print user.name
                print gl.get_last_move_time(game)

                subject = 'Make a move!  Guess the location city!'
                body = 'Hey {}, you\'ve got moves left on your guess the locatio game!'.format(user.name)
                body += '\n\n'
                body += 'Game key: ' + game.key.urlsafe()
                if game.active_question:
                    body += '\nActive question key: ' + game.active_question.urlsafe()
                body += '\nQuestions remaining: ' + str(game.cities_remaining)
                body += '\n\n'
                body += 'https://guess-the-location.appspot.com/'

                mail.send_mail(
                    'noreply@{}.appspotmail.com'.format(app_id),
                    user.email,
                    subject,
                    body
                )

        # user = models.User.query(models.User.name == 'jimmy').get()
        # all_users = models.User.query().fetch()
        # for user in all_users:
        #     attempts = gl.avg_guess_rate(user)
        #     if attempts is not None:
        # #         print user.name, '{:.4f}'.format(attempts)
        # city = models.City.get_city('San Francisco', 'United States', 'North America')

        # monuments_list = fApi.monuments_by_city(city.city_name)

        # if not monuments_list:
        #     logging.error('No monuments found for ' + city.city_name)

        # for monument in monuments_list:
        #     mon = models.Monument.add_monument(monument, city.key)
        #     log_msg = '{city}, {monument}'.format(city=city.city_name, monument=mon.name)
        #     logging.debug(log_msg)
        #     # print city.city_name, mon.name


        # cities_list = models.City.query().fetch()
        # for city in cities_list:
        #     print '------------------------------------------------------'
        #     print city.city_name
        #     monuments_list = models.Monument.get_monuments_from_parent(city.key)
        #     for monument in monuments_list:
        #         print city.city_name, monument.name
        #     # for i in range(100):
            #     monument = gl.get_unique_random_key([], monuments_list)
            #     print monument.get().name

        # print models.City.get_available_regions()

        # possible_cities = models.City.get_cities_by_regions(['North America'])

        # i = 50
        # while i > 0:
        #     new_city_key = gl.get_unique_random_key([], possible_cities)
        #     print new_city_key.get().city_name
        #     i -= 1

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
    ('/jobs/cache_user_rankings', UpdateUserRankingsCache),
    ('/crons/build_monuments_data', BuildMonumentsDataHandler),
    ('/crons/email_reminder', SendReminderEmail),
    ('/jobs/playground', PlayGroundHandler)
], debug=True)
