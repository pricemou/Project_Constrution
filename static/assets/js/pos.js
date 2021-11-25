// pos_cash_in_out_odoo js
$(document).ready(function () {
    // // clic function
    // $("#validert").click(function(){

    //     // get value input
    //     var agence = $("#agence").is(":checked")
    //     var individu = $("#individu").is(":checked")
    //     var porte = $("#porte").is(":checked")

    //     // requete de l'atat de la commande 
    //     function assignmt_action(individu, agence, porte ) {
    //         let value = {
    //             "individu_id": individu,
    //             "agence": agence,
    //             'porte': porte,
    //         }

    //         console.log(value)
    //         $.ajax({
    //             url: "/retrait",
    //             data: value,
    //             cache: "false",
    //             success: function (res) {
    //                 if (res == true) {
    //                     alert("hello");
    //                 };

    //                 if(( porte)||(individu)){
    //                     // window.location = "/retrait";
    //                 } else if(agence){
    //                     window.location = "/ListeAgence";
    //                 }else {
                        
    //                 }
                    
    //             },

    //             Error: function (x, e) {
    //                 alert("Some error");
    //             }
    //         });


    //     }

    //     assignmt_action(individu, agence, porte )
    // })


    // email fuction 
    // $('#valider').on('click', function(){
    //     console.log('Mail')
    //     var value = {}  
    //     $.ajax({
    //         url: '/odoo/send/mail',
    //         data: JSON.stringify(value),
    //         type: "POST",
    //         contentType: "application/json",
    //         dataType: "json",

    //         success: function (data) {
    //         console.log('Mail Send')
    //         }
    //     })

    // })


    // Validation pour le type de paye
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
            window.location = "/retrait";
        }
        if(porte === true){
            window.location = "/retraitParDoor";
        }
    })

    // validation agence
    $("#validerloca").click(function(){
        window.location = "/rechercherAgences";
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

});

