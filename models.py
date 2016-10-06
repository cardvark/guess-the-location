#!/usr/bin/env python

"""

models.py - class definitions for datastore entities, other game model data.

Guess the location game server-side Python App Engine

"""

from datetime import datetime
from google.appengine.ext import ndb
import endpoints
import forms
import game_logic as gl


# Manually built list of cities to populate City datastore.
CITIES_LIST = [
    ['Hong Kong', 'China', 'Asia'],
    ['Singapore', 'Singapore', 'Asia'],
    ['Bangkok', 'Thailand', 'Asia'],
    ['Shenzhen', 'China', 'Asia'],
    ['Seoul', 'South Korea', 'Asia'],
    ['Taipei', 'Taiwan', 'Asia'],
    ['Shanghai', 'China', 'Asia'],
    ['Tokyo', 'Japan', 'Asia'],
    ['Beijing', 'China', 'Asia'],
    ['London', 'United Kingdom', 'Europe'],
    ['Paris', 'France', 'Europe'],
    ['Rome', 'Italy', 'Europe'],
    ['Barcelona', 'Spain', 'Europe'],
    ['Amsterdam', 'Netherlands', 'Europe'],
    ['Venice', 'Italy', 'Europe'],
    ['New York City', 'United States', 'North America'],
    ['Miami', 'United States', 'North America'],
    ['Las Vegas', 'United States', 'North America'],
    ['Los Angeles', 'United States', 'North America'],
    ['Orlando', 'United States', 'North America'],
    ['San Francisco', 'United States', 'North America'],
    ['Vancouver', 'Canada', 'North America'],
    ['Boston', 'United States', 'North America'],
    ['Seattle', 'United States', 'North America'],
    ['Portland', 'United States', 'North America'],
    ['Washington, D.C.', 'United States', 'North America'],
    ['Austin', 'United States', 'North America'],
    ['Chicago', 'United States', 'North America']
]


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()

    @classmethod
    def add_user(cls, name, email):
        user = cls(
            name=name,
            email=email
        )
        user.put()
        return user


class City(ndb.Model):
    """City object """
    city_name = ndb.StringProperty(required=True)
    country = ndb.StringProperty()
    region = ndb.StringProperty()

    # classmethod - get list of cities, allow list of regions to filter by.

    @classmethod
    def get_city(cls, city_name, country, region):
        """Queries and returns city entity"""
        city = cls.query()
        city = city.filter(cls.city_name == city_name)
        city = city.filter(cls.country == country)
        city = city.filter(cls.region == region)

        return city.get()

    @classmethod
    def add_city(cls, city_name, country, region):
        """Adds new city entity, unless already exists"""
        city = cls.get_city(city_name, country, region)

        if not city:
            print 'New city!'
            city = cls(
                city_name=city_name,
                country=country,
                region=region
            )
            city.put()

        return city

    @classmethod
    def get_available_regions(cls):
        """Gets unique list of regions (name only)"""
        query = cls.query(projection=['region'], distinct=True)
        regions_list = [data.region for data in query]

        return regions_list

    @classmethod
    def get_cities_by_regions(cls, regions_list):
        """Gets all cities from regions requested, city_name only"""
        cities_query = cls.query(
            cls.region.IN(regions_list),
            projection=['city_name']
        )

        return cities_query.fetch()

    def get_monuments(self):
        """Gets monuments associated with a given city"""
        monuments = Monument.query(ancestor=self.key).fetch()

        return monuments


class Monument(ndb.Model):
    """Monument object
    - Always built with City parent

    """
    fsq_id = ndb.StringProperty()
    name = ndb.StringProperty()
    lat = ndb.FloatProperty()
    lng = ndb.FloatProperty()
    url = ndb.StringProperty()
    img_prefix = ndb.StringProperty()
    img_suffix = ndb.StringProperty()

    @classmethod
    def get_monument_by_fsq_id(cls, fsq_id):
        m_key = ndb.Key(cls, fsq_id)

        return m_key.get()

    @classmethod
    def add_monument(cls, monument_dict, parent_key):
        fsq_id = monument_dict.get('fsq_id')
        monument = cls.get_monument_by_fsq_id(fsq_id)

        if not monument:
            m_key = ndb.Key(cls, fsq_id, parent=parent_key)
            monument = cls(
                key=m_key,
                fsq_id=fsq_id,
                name=monument_dict.get('name'),
                lat=monument_dict.get('lat'),
                lng=monument_dict.get('lng'),
                url=monument_dict.get('url'),
                img_prefix=monument_dict.get('img_prefix'),
                img_suffix=monument_dict.get('img_suffix')
            )
        else:
            print monument.name + ' exists; updating...'
            for prop, val in monument_dict.iteritems():
                monument.prop = val

        monument.put()

        return monument


class Game(ndb.Model):
    """Game object"""
    user = ndb.KeyProperty(required=True, kind='User')
    game_over = ndb.BooleanProperty(default=False)
    regions = ndb.StringProperty(repeated=True)
    last_cities = ndb.StringProperty(repeated=True)
    monuments_list = ndb.StringProperty(repeated=True)
    cities_total = ndb.IntegerProperty(required=True, default=5)
    cities_remaining = ndb.IntegerProperty()
    active_question = ndb.KeyProperty(kind='CityQuestion')

    @classmethod
    def new_game(cls, user, regions_list, cities_total):
        """Creates and returns a new game"""
        game = cls(
            user=user.key,
            regions=regions_list,
            cities_total=cities_total,
            cities_remaining=cities_total
        )
        game.put()

        return game

    @classmethod
    def get_games_by_user(cls, user, all_games):
        filters = [{'field': 'user', 'operator': '=', 'value': user.key}]
        if not all_games:
            active_filter = {
                'field': 'game_over',
                'operator': '=',
                'value': False
            }
            filters.append(active_filter)

        games_query = cls.query()
        for fltr in filters:
            formatted_filter = ndb.query.FilterNode(
                fltr['field'],
                fltr['operator'],
                fltr['value']
                )
            games_query = games_query.filter(formatted_filter)

        return games_query.fetch()

    def to_form(self, message=None):
        """Returns a GameForm representation of the Game"""
        form = forms.GameForm()
        form.urlsafe_game_key = self.key.urlsafe()
        form.cities_total = self.cities_total
        form.user_name = self.user.get().name
        form.cities_remaining = self.cities_remaining
        if message:
            form.message = message

        if self.active_question:
            form.active_question = self.active_question.urlsafe()

        return form

    # May deprecate, not sure yet.
    def new_question_update(self, recent_cities, new_monument_key, active_question_key):
        """Updates Game entity based on new question"""
        self.last_cities = recent_cities
        self.cities_remaining -= 1
        self.monuments_list.append(new_monument_key.urlsafe())
        self.active_question = active_question_key
        self.put()

        return self

    def end_question_update(self):
        """Updates Game entity based on finished question"""
        self.active_question = None
        self.put()

        return self.cities_remaining <= 0

    def end_game(self):
        """Ends game upon completion or cancel"""
        self.game_over = True
        self.put()


class CityQuestion(ndb.Model):
    """City question object
    - Always built w/ Game parent.

    """
    city_name = ndb.StringProperty()
    monument = ndb.KeyProperty(required=True, kind='Monument')
    attempts_allowed = ndb.IntegerProperty(required=True)
    attempts_remaining = ndb.IntegerProperty()
    question_over = ndb.BooleanProperty(default=False)
    guessed_correct = ndb.BooleanProperty()
    guess_history = ndb.StringProperty(repeated=True)

    @classmethod
    def new_city_question(cls, game_parent_key, city_name, monument_key, attempts_allowed):
        new_question = cls(
            city_name=city_name,
            monument=monument_key,
            attempts_allowed=attempts_allowed,
            attempts_remaining=attempts_allowed,
            parent=game_parent_key
        )
        new_question.put()
        return new_question

    def to_form(self, message):
        """Returns a CityQuestionForm representation of the CityQuestion"""
        form = forms.CityQuestionForm()
        # Obtains allowed monument properties based on attempts remaining + minzoom
        form = gl.evaluate_question_response(self, form)

        # Adds own properties + message.
        form.urlsafe_city_key = self.key.urlsafe()
        form.attempts_remaining = self.attempts_remaining
        form.message = message

        return form

    def guess_update(self, guess):
        self.guess_history.append(guess)
        self.attempts_remaining -= 1
        self.put()

        return self.attempts_remaining

    def end_question(self, correct=False):
        """Ends the question. Updates score if correct, based on attempts_remaining"""
        self.question_over = True
        self.guessed_correct = correct
        self.put()


# TODO: Score model
class Score(ndb.Model):
    """ Score object
    - date (for end of game, including cancel)
    - parent is game?
    - score for the game.  (will be an updated total)
    - has user
    """
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateTimeProperty(auto_now=True)
    total_score = ndb.IntegerProperty(default=0)

    @classmethod
    def new_score(cls, user_key, game_key):
        score_object = Score(
            user=user_key,
            parent=game_key
        )
        score_object.put()

        return score_object

    @classmethod
    def get_from_parent(cls, parent_game_key):
        score_object = cls.query(ancestor=parent_game_key).get()

        return score_object

    def update_score(self, question_score):
        self.total_score += question_score
        self.put()

        return self.total_score
