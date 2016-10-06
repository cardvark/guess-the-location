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
        scrollwheel: false,
        disableDoubleClickZoom: true,
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

    // var minZoom = 18;
    // var maxZoom = 12;

    // map.addListener('zoom_changed', function(){
    //     if (map.getZoom() < minZoom) {
    //         map.setZoom(minZoom);
    //     } else if (map.getZoom() > maxZoom){
    //         map.setZoom(maxZoom);
    //     }
    // });
}

var ViewModel = function() {
    var self = this;
    self.isLoading = ko.observable( false );

    // Setup map observables
    // self.zoom = ko.observable(16);
    // self.minZoom = ko.observable(16);
    // self.maxZoom = ko.observable(18);
    // self.lat = ko.observable(37.769115);
    // self.lng = ko.observable(-122.435745);

    // Monument feedback observables
    self.monumentImage = ko.observable();
    self.monumentName = ko.observable();

    // Feedback observables.
    var startingHtml = 'Create a new user and start a game!';
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
                // var errorMessage = response.error.message || '';
                feedback += self.errorResponse( response.error );
            } else {
                feedback += 'User created!';
                feedback += '<br>Name: ' + user_name;
                feedback += '<br>Email: ' + email;
                self.createEmailInput( '' );
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
                // self.newGameUsernameInput = ko.observable( '' );
                // self.newGameRegionsInput = ko.observable( '' );
                // self.newGameTotalCitiesInput = ko.observable( '' );

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
            infoWindow.close();
            feedback += '<br>Correct answer: ' + response.city_name;
            feedback += '<br>Points earned: ' + response.question_score;
        }
        if ( response.game_over ) {
            // feedback += '<br>Game over!';
            feedback += '<br>Final score: ' + response.total_score;
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
            websafe_game_key: game_key
        }).execute(function ( response ) {
            if ( response.error ) {
                feedback += self.errorResponse( response.error );
            } else {
                // self.getQuestionGameKeyInput( '' );
                feedback += manageQuestionResponse(response, feedback);

                // // map.minZoom(response.min_zoom);
                // // console.log( response );
                // map.setOptions( {minZoom: parseInt( response.min_zoom) } );
                // map.setZoom( parseInt( response.min_zoom ) );
                // var newLatLng = new google.maps.LatLng({
                //     lat: response.lat,
                //     lng: response.lng
                // });
                // map.setCenter( newLatLng );

                // // self.minZoom(response.min_zoom);
                // // self.lat(response.lat);
                // // self.lng(response.lng);

                // feedback += response.message;
                // feedback += '<br>Question key: ' + response.urlsafe_city_key;
                // feedback += '<br>Attempts remaining: ' + response.attempts_remaining;

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
            websafe_question_key: question_key,
            city_guess: city_guess
        }).execute(function (response) {
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

    // Fires anytime anything changes
    // ko.computed(function () {
    //     localStorage.setItem('guess-the-location', ko.toJSON( this ));
    //     console.log(localStorage.getItem('guess-the-location'));
    // }).bind(this).extend({
    //     rateLimit: {timeout: 500, method: 'notifyWhenChangesStop'}
    // });
};

// var existing = ko.utils.parseJson(localStorage.getItem('guess-the-location'));

// var ViewM = existing || new ViewModel();

var ViewM = new ViewModel();

ko.applyBindings( ViewM );
