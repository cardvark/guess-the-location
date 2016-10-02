var map = {};

function initMap() {
    var myLatLng = new google.maps.LatLng({lat: 37.769115, lng: -122.435745});
    var zoom = 16;

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
        minZoom: 12,
        maxZoom: 18
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
