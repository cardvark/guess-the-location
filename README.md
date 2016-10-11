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
Please note that the front end was built as a proof of concept for the game, not as a final polished product.

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
### Overview
Took parts of the FSND design a game skeleton and rewrote, heavily modified, and substantially extended the project.
### Endpoints:
#### create_user
* Request parameters:
  * user_name -- string, required.  Server will validate if the user_name is unique.
  * email -- string, optional.
* Function:
  * Generates new User entity.
  * Required to create new games.
* Response properties:
  * user_name -- string.  Returns name from new User entity.
  * email -- string.  Returns email from new User entity.

#### new_game
* Request parameters:
  * user_name -- string, required.  Must be a valid user_name with a User entity.
  * regions -- string, repeated.  Each must be a valid region.  ('North America', 'Europe', 'Asia' are currently accepted.)
  * cities_total -- integer, required.  0 < cities_total <= MAX_CITY_QUESTIONS (in game_logic module, set to 5 currently).
* Function:
  * Creates new Game entity.
* Response properties:
  * urlsafe_game_key -- string.  Game key in websafe format.  Required to get questions for the game.
  * cities_total -- integer.  Returns cities_total from new Game entity.
  * user_name -- string.  Returns name from User entity from Game entity.
  * cities_remaining -- integer.  Returns cities_total from new Game entity.  Represents # of questions the game has left.
  * regions -- list of strings.  Returns regions from Game entity.
  * game_over -- boolean.  Returns game_over status (default to FalsE) from Game entity.  Can be changed when final question is answered, or game is canceled.

#### get_question
* Request parameters:
  *  urlsafe_game_key -- string, required.  Game key in websafe format.
* Function:
  * Checks if game is valid and has questions remaining.
  * Obtains active question if it exists.
  * Otherwise creates and returns a new CityQuestion entity.
* Response properties:
  * Full list of properties depends on question status.  Attempts remaining on a question dictates how much information is passed.
  * Note: Monument information is generated via Foursquare API.
  * message -- string.  Server generated message based on whether question is new or active.
  * Default (new question):
    * urlsafe_city_key -- string.  CityQuestion key in websafe format.
    * min_zoom -- integer.  # of questions remaining determines how far a user may zoom out.
    * attempts_remaining -- integer. # of guess attempts left to answer the question.
    * message -- string.  server generated message.
    * lat -- float.  Location latitude
    * lng -- float.  Location longitude
  * 2 attempts remaining.  Above items, plus:
    * img_prefix -- string.  Monument image url prefix.
    * img_suffix -- string.  Monument image url suffix.
      * Note: these two items can be tied together by the client by adding image dimensions between img_prefix and img_suffix.f
      * E.g., img_prefix + '200x200' + img_suffix generates a link to the 200x200 image of the monument.
  * 1 attempt remaining.  Above items, plus:
    * name -- string.  Monument name.
  * 0 attempts remaining.  Above items, plus:
    * url -- string.  link to Foursquare page.

#### submit_question_guess
* Request parameters:
  * urlsafe_question_key -- string.  CityQuestion key in websafe format.
  * guess -- string.  User's guess on what city has been shown.
* Function:
  * Checks if question is valid (not over, attempts remaining)
  * Evaluates whether guess is correct.
  * Determines if question is over (correct or no more attempts remaining)
    * Evaluates score based on # of attempts remaining
  * Determines if game is over (question over and no more questions remaining)
* Response:
  * message -- string.  Server generated message based on whether user guessed correctly, and question / game status.
  * Includes all response properties of 'get_question', based on same criteria.
  * Additionally:
  * If question is over (guessed correct or out of attempts):
    * question_score -- integer.  points earned for this question, based on # of attempts remaining.
    * cities_remaining -- integer.  # of cities remaining from the parent Game entity.
    * guessed_correct -- boolean.  True/False whether player guessed correctly.
    * city_name -- string.  Correct answer city name of the question.
  * If game is over (question over and game has no questions remaining):
    * total_score -- integer.  base score for game (sum of all question scores)
    * bonus_modifier -- float.  Score modifier based on # of cities possible in this Game entity (based on regions selected on game creation).
    * bonus_score -- integer.  Rounded down scoreore based of total_score * bonus_modifier.
    * game_over -- boolean.  (True.)  Indicates game is over.

#### get_games_by_user
* Request parameters:
  * user_name -- string, required.
  * game_over -- boolean, optional.  (Test client defaults to 'False')
* Function:
  * Finds all games based on user_name and game_over status.
  * game_over:
    * True - returns only inactive, game_over == True games.
    * False - returns only active, game_over == False games.
    * None - returns all games.
* Response:
  * message -- string.  Server generated message.
  * List of game forms:
    * Each form includes the same properties as the new_game endpoint.

#### cancel_game
* Request parameters:
  * urlsafe_game_key -- string, required.  Game key in websafe format.
* Function:
  * Checks if game is still active, ends game if so.
* Response:
  * message -- string.  Server generated message, confirms game was canceled.
  * Same properties as new_game endpoint.

#### get_high_scores
* Request parameters:
  * max_results -- integer, optional.  Total number of results requested.
* Function:
  * Retrieves (up to max_results, or all) score records for each game in descending order, by bonus_score value.
* Response:
  * message -- string.
  * List of score forms. Each contains:
    * date -- datetime.  Date score was last updated (should be end of game)
    * total_score -- integer.
    * bonus_modifier -- float.
    * bonus_score -- integer.
    * user_name -- string.
    * regions -- List of strings.  Game's selected regions.

#### get_user_rankings
* Request parameters:
  * max_results -- integer, optional.  Total number of results requested.
* Function:
  * Retrieves users listed in order of the ranking metric.
  * Ranking metric is avg # of guesses (float) required to complete each question.
    * Perfect score would be 1, complete failure would be 3.
    * game_logic module contains 'MINIMUM_QUESTIONS_RANKING' constant, which indicates minimum number of questions a user must have completed in order to be ranked.  (Currently set to 5)
  * Order is ascending.
* Response:
  * message -- string.
  * List of user rank forms.  Each contains:
    * user_name -- string.
    * guess_rate -- float.  Avg number of guesses per question completed.
    * questions_count -- integer.  Total number of questions completed.

#### get_game_history
* Request parameters:
  * urlsafe_game_key -- string, required.  Game key in websafe format.
* Function:
  * Retrieve a game's questions, and each question's guess, response, and score history.
* Response:
  * List of question forms.  Each contains:
    * city_name -- string.
    * monument_name -- string.
    * if question is over:
      * question_score -- integer.
    * List of guess response forms. Each contains:
      * user_guess -- string.  User's guess.
      * guessed_correct -- boolean.  Whether guess was correct.

## Additional expected functionality:


## Forthcoming features:
* Facebook and Google+ login and sharing.
* Redesigned and rebuilt front end client
* Potential modifications to game content (cities list, monuments, images)

## Attributions:
* [Google Maps API](https://developers.google.com/maps/)
* [Foursquare API](https://developer.foursquare.com/)
