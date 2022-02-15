function calculateAndDisplayRoute(directionsService, directionsDisplay, driver_lat, driver_long, shipping_lat, shipping_lng) {
    var driver_lat = parseFloat(driver_lat);
    var driver_lng = parseFloat(driver_long);
    var shipping_lat = parseFloat(shipping_lat);
    var shipping_lng = parseFloat(shipping_lng);
    if (!driver_lat && !driver_lng) {
        driver_lat = shipping_lat;
        driver_lng = shipping_lng;
    }
    directionsService.route({
        origin: {
            lat: driver_lat,
            lng: driver_lng
        },
        destination: {
            lat: shipping_lat,
            lng: shipping_lng
        },
        travelMode: 'WALKING'
    }, function (response, status) {
        if (status === 'OK') {
            directionsDisplay.setDirections(response);
        } else {}
    });
}


function openModal(agence, distance) {
    if(distance < 100) {
        var agency_name = document.querySelector('#exampleModal h3');
        var agency_image = document.querySelector('#exampleModal img');
        agency_name.innerText = 'Vous êtes proche de '+String(agence.name);
        agency_image.src = `/web/image?model=res.partner&amp;id=${agence.id}&amp;field=image_128`;
        $('#exampleModal').modal('show');
    }
}