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

from api import GuessLocationApi
import models
import foursquareApi as fApi
import game_logic as gl
from google.appengine.ext import ndb
from google.appengine.api import mail
from google.appengine.api import app_identity
from google.appengine.api import taskqueue

import sys
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


class SendEmailHandler(webapp2.RequestHandler):
    def post(self):
        """Send out email via taskqueue"""
        logging.debug('New email added: ' + self.request.get('subject'))
        logging.debug('body: ' + self.request.get('body'))
        app_id = app_identity.get_application_id()
        mail.send_mail(
            'noreply@{}.appspotmail.com'.format(app_id),
            self.request.get('email'),
            self.request.get('subject'),
            self.request.get('body'),
            html=self.request.get('html')
        )


# TODO: This is shit.  I hate it.  need to reconsider how I want this to run.
class EmailCronJob(webapp2.RequestHandler):
    def get(self):
        """Send reminder email to user regarding unfinished games.  Runs hourly, checks for games without movement for X hours"""

        min_inactive = 24  # hours inactive
        max_inactive = 24.99  # none older than these hours.

        now = datetime.datetime.now()
        min_time = now - datetime.timedelta(hours=min_inactive)
        max_time = now - datetime.timedelta(hours=max_inactive)

        valid_users = models.User.get_all_users(email_only=True, keys_only=True)
        incomplete_games = models.Game.get_all_games(game_over=False, completed=False)
        filtered_games = gl.filter_games_by_time(incomplete_games, min_time, max_time)

        for game in filtered_games:
            logging.debug('Game! ' + str(game.last_modified))
            if game.user in valid_users:
                valid_users.remove(game.user)
                user = game.user.get()
                print user.name
                print gl.get_last_move_time(game)
                logging.debug('Valid game! ' + user.name)

                subject = 'Make a move!  Guess the location city!'

                body = """
                Hey {user_name}, you\'ve got moves left on your guess the location game!  You can find your open games by searching your username in \'Get Active Games\'

                Thanks for playing!
                """.format(user_name=user.name)

                html = 'Hey {user_name},'.format(user_name=user.name)
                html += '<br><br>You\'ve got moves left on your guess the location game!  (You can find your open games by searching your username in \'Get Active Games.\')'
                html += '<br><br>'
                html += 'Game key: ' + game.key.urlsafe()
                html += '<br>'

                if game.active_question:
                    html += 'Active question key: ' + game.active_question.urlsafe()
                    html += '<br>'
                html += 'Questions remaining: ' + str(game.cities_remaining)
                html += '<br><br>'
                html += 'Play the game!'

                taskqueue.add(
                    params={
                        'email': user.email,
                        'subject': subject,
                        'body': body,
                        'html': html
                    },
                    url='/jobs/send_email',
                    queue_name='mail-queue'
                )


# class PlayGroundHandler(webapp2.RequestHandler):
#     def get(self):
#         """General testing ground"""


app = webapp2.WSGIApplication([
    ('/jobs/build_city_data', BuildCityDataHandler),
    ('/jobs/cache_user_rankings', UpdateUserRankingsCache),
    ('/jobs/send_email', SendEmailHandler),
    ('/crons/build_monuments_data', BuildMonumentsDataHandler),
    ('/crons/email_reminder', EmailCronJob),
    # ('/jobs/playground', PlayGroundHandler)
], debug=False)
