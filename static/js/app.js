var map = {};
var marker = {};
var infoWindow = {};

function initMap() {
    var myLatLng = new google.maps.LatLng({lat: 37.769115, lng: -122.435745});
    var zoom = 12;

    map = new google.maps.Map(document.getElementById('map'), {
        zoom: zoom,
        center: myLatLng,
        mapTypeId: 'hybrid',
        styles: [
          {
            featureType: "all",
            stylers: [
              { visibility: "off" }
            ]
          },
          {
            featureType: "road",
            stylers: [
              { visibility: "on" }
            ]
          }
        ]
    });

    map.setOptions({
        draggable: false,
        // zoomControl: false,
        // scrollwheel: false,
        // disableDoubleClickZoom: true,
        streetViewControl: false,
        minZoom: 4,
        maxZoom: 18
    });

    marker = new google.maps.Marker({
        position: myLatLng,
    });

    infoWindow = new google.maps.InfoWindow();

    map.addListener('click', function(){
        infoWindow.close();
    });

}

var ViewModel = function() {
    var self = this;
    self.isLoading = ko.observable( false );

    // Monument feedback observables
    self.monumentImage = ko.observable();
    self.monumentName = ko.observable();

    // Feedback observables.
    var startingHtml = '<h4>Would you like to play game?<h4>';
    startingHtml += '<br>Create a new user and start a game!';
    startingHtml += '<br><br>Guess the city from the map and a random monument.';
    startingHtml += '<br><br>Three tries per city. A wrong answer provides more information but lowers the score.';
    self.genericFeedback = ko.observable(startingHtml);
    self.monumentInfoFeedback = ko.observable();

    // Create User input values
    self.createEmailInput = ko.observable();
    self.createUsernameInput = ko.observable();

    // Create New Game input values
    self.newGameUsernameInput = ko.observable();
    self.newGameRegionsInput = ko.observable();
    self.newGameTotalCitiesInput = ko.observable();

    // Get Question input values
    self.getQuestionGameKeyInput = ko.observable();

    // Submit Guess input values
    self.sendGuessQuestionKeyInput = ko.observable();
    self.sendGuessCityInput = ko.observable();

    // Get Games input values
    self.getGamesUsernameInput = ko.observable();
    self.getGamesGameOverInput = ko.observable( false );

    //
    self.formsList = ko.observableArray( [] );

    self.errorResponse = function( error ) {
        var outMessage = '';
        outMessage += 'Error!';
        outMessage += '<br><br>';
        outMessage += error.message || '';

        return outMessage;
    };

    self.createUser = function() {
        var email = self.createEmailInput();
        var user_name = self.createUsernameInput();
        var feedback = '';

        self.isLoading( true );
        marker.setMap( null );

        gapi.client.guess_the_location.create_user({
            email: email,
            user_name: user_name
        }).execute(function ( response ) {
            if (response.error) {
                feedback += self.errorResponse( response.error );
            } else {
                feedback += 'User created!';
                feedback += '<br>Name: ' + user_name;
                feedback += '<br>Email: ' + email;
                self.createEmailInput( '' );
                self.getGamesUsernameInput( user_name );
            }
            // self.createUsernameInput( '' );
            self.isLoading( false );
            self.genericFeedback( feedback );
        });
    };

    self.createNewGame = function() {
        var user_name = self.newGameUsernameInput();
        var regions = self.newGameRegionsInput();
        var cities_total = self.newGameTotalCitiesInput();
        var feedback = '';

        var regions_arr = regions.split( ',' ).map(function ( word ) {
            return $.trim(word);
        });

        // reset some fields:
        self.monumentImage( '' );
        self.monumentName( '' );
        self.getQuestionGameKeyInput( '' );
        self.sendGuessQuestionKeyInput( '' );

        marker.setMap( null );
        self.isLoading( true );

        gapi.client.guess_the_location.new_game({
            user_name: user_name,
            regions: regions_arr,
            cities_total: cities_total
        }).execute(function ( response ) {
            if ( response.error ) {
                feedback += self.errorResponse( response.error );
            } else {
                feedback += 'New game created!';
                feedback += '<br>Game ID: ' + response.urlsafe_game_key;
                feedback += '<br>Cities remaining: ' + response.cities_remaining;
                feedback += '<br>Created by: ' + response.user_name;

                self.getQuestionGameKeyInput(response.urlsafe_game_key);
            }
            self.isLoading( false );
            self.genericFeedback( feedback );
        });
    };

    function manageQuestionResponse(response, feedback) {
        var imageHtml = 'Monument Image: <br><img src="{{url}}" alt="monument image">';
        map.setOptions( {minZoom: parseInt( response.min_zoom) } );
        map.setZoom( parseInt( response.min_zoom ) );
        var newLatLng = new google.maps.LatLng({
            lat: response.lat,
            lng: response.lng
        });
        map.setCenter( newLatLng );

        if ( response.img_prefix && response.img_suffix ) {
            marker.setMap( map );
            marker.setPosition( newLatLng );
            marker.setAnimation( google.maps.Animation.DROP );
            var imgUrl = response.img_prefix + '200x200' + response.img_suffix;
            imageHtml = imageHtml.replace('{{url}}', imgUrl);
            self.monumentImage( imageHtml );

            infoWindow.setContent( self.monumentImage() );
            infoWindow.open(map, marker);

            marker.addListener('click', function(){
                infoWindow.open(map, marker);
            });
        }

        if ( response.name ) {
            self.monumentName( 'Monument name: ' + response.name );
            infoWindow.setContent( self.monumentName() + '<br>' + self.monumentImage() );
        }

        feedback += response.message;

        if ( response.question_score ){
            self.sendGuessQuestionKeyInput( '' );
            infoWindow.close();
            feedback += '<br>Correct answer: ' + response.city_name;
            feedback += '<br>Points earned: ' + response.question_score;
            feedback += '<br> Cities remaining: ' + response.cities_remaining;
        }
        if ( response.game_over ) {
            feedback += '<br>Base score: ' + response.total_score;
            feedback += '<br>Bonus modifier: ' + response.bonus_modifier;
            feedback += '<br>Total score: ' + response.bonus_score;
        } else {
            feedback += '<br>Attempts remaining: ' + response.attempts_remaining;
            feedback += '<br>Question key: ' + response.urlsafe_city_key;
        }

        return feedback;
    }

    self.getQuestion = function() {
        var game_key = self.getQuestionGameKeyInput();
        var feedback = '';

        self.isLoading( true );
        marker.setMap( null );

        // reset some fields:
        self.monumentImage( '' );
        self.monumentName( '' );
        self.sendGuessQuestionKeyInput( '' );

        gapi.client.guess_the_location.get_question({
            urlsafe_game_key: game_key
        }).execute(function ( response ) {
            if ( response.error ) {
                feedback += self.errorResponse( response.error );
            } else {
                // self.getQuestionGameKeyInput( '' );
                feedback += manageQuestionResponse(response, feedback);
                self.sendGuessQuestionKeyInput( response.urlsafe_city_key );
            }
            self.isLoading( false );
            self.genericFeedback( feedback );
        });
    };

    self.sendGuess = function() {
        var question_key = self.sendGuessQuestionKeyInput();
        var city_guess = self.sendGuessCityInput();
        var feedback = '';

        self.isLoading( true );
        marker.setMap( null );

        // reset some fields:
        self.monumentImage( '' );
        self.monumentName( '' );

        gapi.client.guess_the_location.submit_question_guess({
            urlsafe_question_key: question_key,
            city_guess: city_guess
        }).execute(function ( response ) {
            if ( response.error ) {
                feedback += self.errorResponse( response.error );
            } else {
                self.sendGuessCityInput( '' );
                feedback += manageQuestionResponse(response, feedback);
            }
            self.isLoading( false );
            self.genericFeedback( feedback );
        });
    };

    self.getGames = function() {
        var user_name = self.getGamesUsernameInput();
        var game_over = self.getGamesGameOverInput();
        var feedback = '';

        self.isLoading( true );

        // reset some fields:
        self.monumentImage( '' );
        self.monumentName( '' );

        gapi.client.guess_the_location.get_games_by_user({
            user_name: user_name,
            game_over: game_over
        }).execute(function ( response ) {
            if ( response.error ) {
                feedback += self.errorResponse( response.error );
            } else {
                feedback += 'Returning all active games!';
                var game_list = response.items;

                game_list.forEach(function ( game_resp ) {
                    feedback += '<br><br>Key: ' + game_resp.urlsafe_game_key;
                    feedback += '<br>Regions: ' + game_resp.regions.join(', ');
                    if ( game_resp.active_question ){
                        feedback += '<br>Active question key: ' + game_resp.active_question;
                    }
                    var remaining = game_resp.cities_remaining || 0;
                    feedback += '<br>Remaining questions: ' + remaining;
                });

            }
            self.genericFeedback( feedback );
            self.isLoading( false );
        });
    };

    self.getHighScores = function() {
        var maxResults = 10;
        var feedback = '';

        self.isLoading( true );

        // reset some fields:
        self.monumentImage( '' );
        self.monumentName( '' );

        gapi.client.guess_the_location.get_high_scores({
            max_results: maxResults,
        }).execute(function ( response ) {
            if ( response.error ) {
                feedback += self.errorResponse( response.error );
            } else {
                feedback += 'Top ' + maxResults + ' game scores:';
                var score_list = response.items;

                score_list.forEach(function ( score_response ) {
                    feedback += '<br><br>Date: ' + moment(score_response.date).format('LLL');
                    feedback += '<br>User: ' + score_response.user_name;
                    feedback += '<br>Regions: ' + score_response.regions.join(', ');
                    feedback += '<br>Bonus modifier: ' + score_response.bonus_modifier;
                    feedback += '<br>Bonus score: ' + score_response.bonus_score;
                });

            }
            self.genericFeedback( feedback );
            self.isLoading( false );
        });
    };

    self.getUserRanks = function() {
        var maxResults = 10;
        var feedback = '';

        self.isLoading( true );

        // reset some fields:
        self.monumentImage( '' );
        self.monumentName( '' );

        gapi.client.guess_the_location.get_user_rankings({
            max_results: maxResults,
        }).execute(function ( response ) {
            if ( response.error ) {
                feedback += self.errorResponse( response.error );
            } else {
                feedback += 'Top ' + maxResults + ' ranked users:';
                var rankings_list = response.items;

                rankings_list.forEach(function ( rank_response ) {
                    feedback += '<br><br>User: ' + rank_response.user_name;
                    feedback += '<br>Guess rate: ' + rank_response.guess_rate;
                    feedback += '<br>Questions count: ' + rank_response.questions_count;
                });

            }
            self.genericFeedback( feedback );
            self.isLoading( false );
        });
    };
};

var ViewM = new ViewModel();

ko.applyBindings( ViewM );
