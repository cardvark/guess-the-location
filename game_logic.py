#!/usr/bin/env python

"""

game_logic.py - game logic functions

Guess the location game server-side Python App Engine

Thoughts:
- Steps:
  -

- pseudo-randomization for cities to choose.  Keep a list of 3 most recent cities, don't allow a choice to be of one of those three.
-

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

SCORE_DICT = {
    3: 10,
    2: 5,
    1: 2,
    0: 0
}

