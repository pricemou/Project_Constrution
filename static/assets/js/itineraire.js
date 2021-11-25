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
        travelMode: 'DRIVING'
    }, function (response, status) {
        if (status === 'OK') {
            directionsDisplay.setDirections(response);
        } else {}
    });
}