#!/usr/bin/env python

"""

forms.py - message forms and resource containers for use by api.

Guess the location game server-side Python App Engine

"""

from protorpc import messages


class user_form(messages.Message):
    """user_form -- create new users"""
    user_name = messages.StringField(1)
    email = messages.StringField(2)
