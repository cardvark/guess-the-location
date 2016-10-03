#!/usr/bin/env python

"""

models.py - class definitions for datastore entities, other game model data.

Guess the location game server-side Python App Engine

"""

from datetime import date
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
        if cls.query(cls.name == name).get():
            raise endpoints.ConflictException('A user with that name already exists!')

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
        """Gets unique list of regions (name only)
        - Check against user/client request for what regions in new Game.
        """
        query = cls.query(projection=['region'], distinct=True)
        regions_list = [data.region for data in query]

        return regions_list

    @classmethod
    def get_cities_by_regions(cls, regions_list):
        """Gets all cities from regions requested, key and name
        - New Question generation requires knowing what cities are allowed.
        """
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
    cities_asked = ndb.IntegerProperty(default=0)
    active_question = ndb.KeyProperty(kind='CityQuestion')

    @classmethod
    def new_game(cls, user, regions_list, cities_total):
        """Creates and returns a new game"""
        user = User.query(User.name == user).get()
        if not user:
            raise endpoints.NotFoundException('A User with that name does not exist!')

        if cities_total > gl.MAX_CITY_QUESTIONS:
            raise endpoints.BadRequestException('Max number of cities is {}'.format(gl.MAX_CITY_QUESTIONS))

        if not set(regions_list).issubset(City.get_available_regions()):
            raise endpoints.BadRequestException('Region(s) requested are not available.')

        game = cls(
            user=user.key,
            regions=regions_list,
            cities_total=cities_total,
        )

        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = forms.GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.cities_total = self.cities_total
        form.user = self.user.get().name
        form.message = message

        return form


class CityQuestion(ndb.Model):
    """City question object
    - Always built w/ Game parent.

    """
    city_name = ndb.StringProperty()
    monument = ndb.KeyProperty(required=True, kind='Monument')
    attempts_allowed = ndb.IntegerProperty(required=True)
    attempts_remaining = ndb.IntegerProperty()
    question_over = ndb.BooleanProperty(default=False)

    @classmethod
    def new_city_question(cls, city_name, monumet_key, attempts_allowed):
        pass
