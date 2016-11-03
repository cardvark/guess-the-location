# guess-the-location
Google app engine back end API city location guessing game with Google Maps API and Foursquare API for content.

[Play the game!](https://guess-the-location.appspot.com/)

## Setup
* Clone or [download](https://github.com/cardvark/guess-the-location/archive/master.zip) the repo: `https://github.com/cardvark/guess-the-location.git`
* Install (if necessary):
  * [Google App Engine SDK](https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python).

## Testing
* Navigate to directory, run `dev_appserver.py .`
* Open browser to [http://localhost:8080](http://localhost:8080) to view front end.
* Open browser to [http://localhost:8080/_ah/api/explorer](http://localhost:8080/_ah/api/explorer) to view API explorer.
  * Allow unsafe scripts - for chrome, click shield icon in far right of address bar, load unsafe scripts.
* Populate the City datastore with entities by opening browser to [http://localhost:8080/jobs/build_city_data](http://localhost:8080/jobs/build_city_data)
  * Note: this is a one time requirement to populate the City datastore.
* Next, populate Monument datastore:
  * Go to Local project dashboard, cron jobs at [http://localhost:8000/cron](http://localhost:8000/cron)
  * Find the /crons/build_monument_data job and hit Run Now.
  * This is a weekly recurring job designed to keep Monuments data from Foursquare up to date.


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
* Substantially modified and extended the [Udacity Design a Game skeleton](https://github.com/udacity/FSND-P4-Design-A-Game/tree/master/Skeleton%20Project%20Guess-a-Number)
* Base url for requests: https://guess-the-location.appspot.com/_ah/api/guess_the_location/v1/
* Link to [Google API Explorer](https://guess-the-location.appspot.com/_ah/api/explorer)

### Endpoints:
#### create_user
* Path: 'user'
* Method: 'POST'
* Request parameters:
  * user_name -- string, required.  Server will validate if the user_name is unique.
  * email -- string, optional.
* Response properties in UserForm:
  * user_name -- string.  Returns name from new User entity.
  * email -- string.  Returns email from new User entity.
* Description:
  * Generates new User entity.
  * Required to create new games.

#### new_game
* Path: 'game'
* Method: 'POST'
* Request parameters:
  * user_name -- string, required.  Must be a valid user_name with a User entity.
  * regions -- string, repeated.  Each must be a valid region.  ('North America', 'Europe', 'Asia' are currently accepted.)
  * cities_total -- integer, required.  0 < cities_total <= MAX_CITY_QUESTIONS (in game_logic module, set to 5 currently).
* Response properties in GameForm:
  * urlsafe_game_key -- string.  Game key in websafe format.  Required to get questions for the game.
  * cities_total -- integer.  Returns cities_total from new Game entity.
  * user_name -- string.  Returns name from User entity from Game entity.
  * cities_remaining -- integer.  Returns cities_total from new Game entity.  Represents # of questions the game has left.
  * regions -- list of strings.  Returns regions from Game entity.
  * game_over -- boolean.  Returns game_over status (default to FalsE) from Game entity.  Can be changed when final question is answered, or game is canceled.
* Description:
  * Creates new Game entity.

#### get_question
* Path: 'get_question'
* Method: 'PUT'
* Request parameters:
  *  urlsafe_game_key -- string, required.  Game key in websafe format.
* Response properties in QuestionResponseForm:
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
* Description:
  * Checks if game is valid and has questions remaining.
  * Obtains active question if it exists.
  * Otherwise creates and returns a new CityQuestion entity.

#### submit_question_guess
* Path: 'submit_question_guess'
* Method: 'PUT'
* Request parameters:
  * urlsafe_question_key -- string.  CityQuestion key in websafe format.
  * guess -- string.  User's guess on what city has been shown.
* Response properties in QuestionResponseForm:
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
* Description:
  * Checks if question is valid (not over, attempts remaining)
  * Evaluates whether guess is correct.
  * Determines if question is over (correct or no more attempts remaining)
    * Evaluates score based on # of attempts remaining
  * Determines if game is over (question over and no more questions remaining)

#### get_games_by_user
* Path: 'get_games_by_user'
* Method: 'GET'
* Request parameters:
  * user_name -- string, required.
  * game_over -- boolean, optional.  (Test client defaults to 'False')
* Response properties in GameForms:
  * message -- string.  Server generated message.
  * List of game forms:
    * Each form includes the same properties as the new_game endpoint.
* Description:
  * Finds all games based on user_name and game_over status.
  * game_over:
    * True - returns only inactive, game_over == True games.
    * False - returns only active, game_over == False games.
    * None - returns all games.

#### cancel_game
* Path: 'cancel_game'
* Method: 'PUT'
* Request parameters:
  * urlsafe_game_key -- string, required.  Game key in websafe format.
* Response properties in GameForm:
  * message -- string.  Server generated message, confirms game was canceled.
  * Same properties as new_game endpoint.
* Function:
  * Checks if game is still active, sets game_over to True if so.
  * Does not delete game in datastore.

#### get_high_scores
* Path: 'get_high_scores'
* Method: 'GET'
* Request parameters:
  * max_results -- integer, optional.  Total number of results requested.
* Response properties in ScoreForms:
  * message -- string.
  * List of score forms. Each contains:
    * date -- datetime.  Date score was last updated (should be end of game)
    * total_score -- integer.
    * bonus_modifier -- float.
    * bonus_score -- integer.
    * user_name -- string.
    * regions -- List of strings.  Game's selected regions.
* Description:
  * Retrieves (up to max_results, or all) score records for each game in descending order, by bonus_score value.

#### get_user_rankings
* Path: 'get_user_rankings'
* Method: 'GET'
* Request parameters:
  * max_results -- integer, optional.  Total number of results requested.
* Response properties in UserRankForms:
  * message -- string.
  * List of user rank forms.  Each contains:
    * user_name -- string.
    * guess_rate -- float.  Avg number of guesses per question completed.
    * questions_count -- integer.  Total number of questions completed.
* Description:
  * Retrieves users listed in order of the ranking metric.
  * Ranking metric is avg # of guesses (float) required to complete each question.
    * Perfect score would be 1, complete failure would be 3.
    * game_logic module contains 'MINIMUM_QUESTIONS_RANKING' constant, which indicates minimum number of questions a user must have completed in order to be ranked.  (Currently set to 5)
    * If no users satisfy above criteria or do not exist, message will be updated to indicate that no users were ranked.
  * Order is ascending.

#### get_game_history
* Path: 'get_game_history'
* Method: 'GET'
* Request parameters:
  * urlsafe_game_key -- string, required.  Game key in websafe format.
* Response properties in GameHistoryForm:
  * List of question forms.  Each contains:
    * city_name -- string.
    * monument_name -- string.
    * if question is over:
      * question_score -- integer.
    * List of guess response forms. Each contains:
      * user_guess -- string.  User's guess.
      * guessed_correct -- boolean.  Whether guess was correct.
* Description:
  * Retrieve a game's questions, and each question's guess, response, and score history.

## Additional expected functionality:
### Cron jobs:
* /crons/build_monuments_data
  * Calls Foursquare API to populate the Monument datastore with Foursquare data.  Should throw errors to the log in case any occur.  Scheduled to run once a week.  Foursquare API requests that devs keep such data relatively up to date.
* /crons/email_reminder
  * Hourly cron job.
  * Checks for games whose last game move was 24-24.99 hours prior
  * Sends emails to users with email addresses in the datastore (only once for all un-moved games w/in this time frame).
  * TODO: rethink this functionality.  Potentially have a better way to queue or flag games for email reminders.
    * Alternatively, may scrap this entirely.  App Engine's free email quota is extremely low (10 per day).

### Caching:
* /jobs/cache_user_rankings
  * Task is run after every completed game.
  * Caches user rankings to memcache.
  * Calculates avg # of guesses for each user for each question. (game_logic module, get_user_rankings)

## Forthcoming features:
* Facebook and Google+ login and sharing.
* Redesigned and rebuilt front end client
* Potential modifications to game content (cities list, monuments, images)

## Attributions:
* [Google Maps API](https://developers.google.com/maps/)
* [Foursquare API](https://developer.foursquare.com/)
