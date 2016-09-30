var map = {};

function initMap() {
    console.log('called!');
    var myLatLng = new google.maps.LatLng({lat: 37.769115, lng: -122.435745});
    var zoom = 2;

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

    // map.setOptions({
    //     draggable: false,
    //     zoomControl: false,
    //     scrollwheel: false,
    //     disableDoubleClickZoom: true
    // });
}
