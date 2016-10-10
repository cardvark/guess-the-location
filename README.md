# guess-the-location
Google app engine back end API city location guessing game with Google Maps API and Foursquare API for content.

README WIP.

## Setup
* Clone or [download](https://github.com/cardvark/guess-the-location/archive/master.zip) the repo: `https://github.com/cardvark/guess-the-location.git`
* Install (if necessary):
  * [Google App Engine SDK](https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python).

## Testing
* Navigate to directory, run `dev_appserver.py .`
* Open browser to [http://localhost:8080](http://localhost:8080) to view front end.
* Open browser to [http://localhost:8080/_ah/api/explorer](http://localhost:8080/_ah/api/explorer) to view API explorer.
  * Allow unsafe scripts - for chrome, click shield icon in far right of address bar, load unsafe scripts.
* Live demonstration [hosted on appspot](https://guess-the-location.appspot.com/)


## Front End Game Client Instructions
### Setup and play
* Note: additional details on endpoints below.
* Create a new user (email optional)
* Create a new game (unique user required)
  * 'Regions' are a comma separated list of strings.  Currently accepted options:
    * North America, Europe, Asia
* Upon creating a new game, the Get Question 'Game key' field should auto-populate with the new game's key.
  * Click submit to have the client request a question from the server.
* The Submit Guess 'Question key' field should auto-populate.
  * Enter your guess for a city (case insensitive, but spelling counts)
  * List of possible cities located in [models](https://github.com/cardvark/guess-the-location/blob/master/models.py) module in 'CITIES_LIST'
* Once a question is complete, you must 'Get Question' to retrieve the next question.
* Manual population of the above fields can be done via copy/paste from the Information section at the top of the left pane.

### Rules
* Each question displays a (mostly unmarked) Google Map of a given location.
  * The locations are based on a random, popular Monument obtained via Foursquare
* The user is initially provided a zoomed in map with no additional information.
* Incorrect answers submitted to the server generate a response with more detail, including:
  * Zooming further out to see more of the map
  * Top image for the monument from Foursquare
  * The monument's name
* Score per question is based on # of attempts required to get the correct City answer.
  * 10, 5, 2 for each of 3 tries.  0 points if incorrect after 3 attempts.
* Total score for a game is comprised of base score and bonus modifier.
  * Base score is calculated by sum of each question's scores.
  * Bonus modifier is a 1% bonus for each possible city in a game.  Adding more regions to the game increases total city count.
  * Total score = base score * bonus modifier

## API

## Additional expected functionality:

## Attributions:
* [Google Maps API](https://developers.google.com/maps/)
* [Foursquare API](https://developer.foursquare.com/)
