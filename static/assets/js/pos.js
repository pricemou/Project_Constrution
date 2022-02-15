// pos_cash_in_out_odoo js
$(document).ready(function () {
   

    $("#valider").click(function(){

        // get value input
        var agence = $("#agence").is(":checked")
        var individu = $("#individu").is(":checked")
        var porte = $("#porte").is(":checked")
        var bnt = $( "#valider")
        var btn = document.getElementById('valider')


        // redirection 
        if(agence === true){
            btn.setAttribute("data-toggle", 'modal')
            btn.setAttribute("data-target", '#exampleModal')
            btn.setAttribute("data-backdrop", 'static')
            btn.setAttribute("data-keyboard", 'false')
        }
        if(individu === true){
            window.location = "/cashout/retired";
        }
        if(porte === true){
            window.location = "/cashout/door_to_door_retired";
        }
    })

    // validation agence
    $("#validerloca").click(function(){
        window.location = "/cashout/agency/search/";
    })

    $("#validerTrager").click(function(){
        var idTransaction = $(".targerId").val();

        // email fuction 
        var value = {
            'cpt': idTransaction,
            }
    
            $.ajax({
                url : "/comfimation",
                data : value,
                cache : "false",
                success : function(res) {
            if (res == 'error'){
                alert("Une erreur s'est produite")
        		}
            	},Error : function(x, e) {
                    alert("Some error");
            	}
            });

            window.location = "/valider";
    })

    // choisir une methode de payement

    $("#commande").click(function(){
        $('.close-modal').hide();
        var numero = $('.numero').val();
        var opreteur = $('#operateur option:selected').val();
        data = {
            'operateur':opreteur,
            'numero':numero,
        }


        $.ajax({
            type: "POST",
            url: url,
            data: JSON.parse(data),
            success: success,
            dataType: dataType
          });
    })

    $( "#searchForm" ).submit(function(event) {
 
        // Stop form from submitting normally
        event.preventDefault();
       
        // Get some values from elements on the page:
        var $form = $( this ),
          term = $form.find( "input[name='numero']" ).val(),
          url = $form.attr( "action" );
          console.log(term);
       
        // Send the data using post
        var settings = {
            "url": "/cashout/request",
            "method": "POST",
            "timeout": 0,
            "headers": {
              "Content-Type": "application/json",
              "Cookie": "session_id=d5e1e1bab77e63b026dab6a6d0e6fdbc001e27d5"
            },
            "data": JSON.stringify({
              "paramas": {
                "hello": "claude",
                "place": "tesd"
              }
            }),
          };
          
          $.ajax(settings).done(function (response) {
            console.log(response);
          });

        // Put the results in a div
        // posting.done(function( data ) {
        //   var content = $( data ).find( "#content" );
        // //   $( "#result" ).empty().append( content );
        // });
      });

});


