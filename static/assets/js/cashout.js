// Initialize and add the map
function initMap() {
    var infoWindow = new google.maps.InfoWindow();
    $.ajax({
        type: 'GET',
        url: "/get_agencies",
        dataType: "json",
        success: function (response) {
            let data = response.agencies;

            // Try HTML5 geolocation.
            // The map, centered at customer
            const map = new google.maps.Map(document.getElementById("map"), {
                zoom: 16,
                mapTypeId: "roadmap",

            });
            // Get user location
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const pos = {
                            lat: position.coords.latitude,
                            lng: position.coords.longitude,
                        };
                        sessionStorage.setItem('latitude', pos.lat);
                        sessionStorage.setItem('longitude',  pos.lng);
                        infoWindow.setPosition(pos);
                        infoWindow.setContent("Vous êtes ici.");
                        infoWindow.open(map);
                        map.setCenter(pos);
                        // The marker, positioned at customer
                        // const marker = new google.maps.Marker({
                        //     position: pos,
                        //     map: map,
                        //     label: {
                        //         text: "Ma position",
                        //         color: "black",
                        //         fontSize: "10px",
                        //         fontWeight: 'bold',
                        //     },
                        // });
                    },
                    () => {
                        handleLocationError(true, infoWindow, map.getCenter());
                    }
                );
            } else {
                // Browser doesn't support Geolocation
                handleLocationError(false, infoWindow, map.getCenter());
            }

            // The location of customer
            // let customer = {
            //     lat: parseFloat(sessionStorage.getItem('latitude')),
            //     lng: parseFloat(sessionStorage.getItem('longitude'))
            // };

            var all_agencies = [];
            let agence = {};
            for (let i = 0; i < data.length; i++) {
                agence = {
                    name: data[i].name,
                    address: data[i].address,
                    image: data[i].image,
                    lat: data[i].latitude,
                    lng: data[i].longitude
                };
                all_agencies.push(agence);
            }

            const image = {
                url: '/web_cash_out/static/assets/img/Agence/localiser.png',
                scaledSize: new google.maps.Size(70, 70),
                origin: new google.maps.Point(0.0),
                anchor: new google.maps.Point(0.0)
            }
            const image1 = {
                url: '/web_cash_out/static/assets/img/Agence/position.png',
                scaledSize: new google.maps.Size(75, 90),
                origin: new google.maps.Point(0.0),
                anchor: new google.maps.Point(0.0)
            }


            for (let i = 0; i < all_agencies.length; i++) {
                const marker_agency = new google.maps.Marker({
                    position: all_agencies[i],
                    map: map,
                    label: {
                        text: String(all_agencies[i].name),
                        color: "black",
                        fontSize: "10px",
                        fontWeight: 'bold',
                    },

                });
                google.maps.event.addListener(marker_agency, 'click', function() {
                    $('#exampleModal').modal('show');
                    var agency_name = document.querySelector('#exampleModal h2');
                    var agency_address = document.querySelector('#exampleModal #address');
                    var agency_image = document.querySelector('#exampleModal img');
                    agency_name.innerText = all_agencies[i].name;
                    agency_address.innerText = all_agencies[i].address;
                    agency_image.src = `${all_agencies[i].image}`;

                    var agency_name_input = document.querySelector('.agence_name');
                    var agency_address_input = document.querySelector('.agence_address');
                    var agency_id_input = document.querySelector('.agence_id');
                    var agency_longitude_input = document.querySelector('.agence_longitude');
                    var agency_latitude_input = document.querySelector('.agence_latitude');


                    agency_name_input.value = all_agencies[i].name;
                    agency_address_input.value = all_agencies[i].address;
                    agency_id_input.value = all_agencies[i].id;
                    agency_longitude_input.value = all_agencies[i].lng;
                    agency_latitude_input.value = all_agencies[i].lat;

                });
            }

            function popup() {
                

            }



            // const inputText = document.createElement("input")
            // inputText.type = "text";
            // inputText.placeholder = "Commune,quartier,type d'agence"

            // map.controls[google.maps.ControlPosition.TOP_CENTER].push(inputText)

            var btn = document.createElement('div')
            btn.classList.add('ok');
            btn.id = 'list'

            btn.innerHTML =
                '<button type="button" class="btn btn-dark valider" onclick="window.history.go(-1); return false;" id="valider" >Afficher la liste  <span class="icon material-icons icone">format_list_bulleted</span></button>'
            map.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(btn);

            // btn.onclick = function quoi() {
            //     location.href = "/cashout/Agency_list"

            // }
        }
    });


}

// Get user location
function getUserLocation() {

    // function success(position) {
    //   sessionStorage.setItem('latitude', position.coords.latitude);
    //   sessionStorage.setItem('longitude', position.coords.longitude);
    // }

    // function error() {
    //   console.log('Unable to retrieve your location');
    // }

    // if(!navigator.geolocation) {
    //     console.log('Geolocation is not supported by your browser');
    // } else {
    //   console.log('Locating…');
    //   navigator.geolocation.getCurrentPosition(success, error);
    // }
}