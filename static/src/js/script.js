odoo.define("pragmatic_odoo_delivery_boy.delivery_control_app_driver", function(require){
	"use strict";

	$(document).ready(function(){
		$("#hidden_box_btn").on('click', function () {
			alert('test')
			voice_command("Juste un test")
			// ajax_call_all_time()
			// $('#check_notif').modal('show');
			// setTimeout(function(){
			// 	$('#check_notif').modal('hide');
			// }, 3000);
		});

		let voice_command = function(txtInput){
            var tts = window.speechSynthesis;
            var voices = [];
            var toSpeak = new SpeechSynthesisUtterance(txtInput)
            var selectedVoiceName = "Google français";
            voices = tts.getVoices();
            voices.forEach((voice)=>{
                if(voice.name === selectedVoiceName){
                    toSpeak.voice = voice;
                    // toSpeak.pitch = 1.2;
                    // toSpeak.rate = 0.8;
                }
            });
            tts.speak(toSpeak)
        }

		var set_off_notif = function(check_id){
			var value = {
				'check_id': check_id,
			}
			$.ajax({
				url : "/tourniquets/check/notification/off",
				data : value,
				cache : "false",
				success : function(res) {
					if (res == 'error'){
						alert("Une erreur s'est produite")
					}
					else{
						$('#check_notif').modal('hide');
					}

				},Error : function(x, e) {
					alert("Some error");
				}
			});
		}

		var ajax_call_all_time = function(){
			console.log("AJAX Call......")
			$.ajax({
				url : "/tourniquets/check/notification/",
				cache : "false",
				success : function(res) {
					if (res == ''){}
					else if (res == 'error'){
						alert("Une erreur s'est produite")
					}
					else{
						let check_details = res.split("#")
						let check_type = check_details[0]
						let empl_id = check_details[1]
						let empl_name = check_details[2]
						let empl_date = check_details[3].split(' ')[0]
						let empl_time = check_details[3].split(' ')[1].split('.')[0]
						let check_id = check_details[4]
	
						$(".empl-image img").attr("src","/web/image/hr.employee/" + empl_id + "/image");
						$(".insert-name").text(empl_name)
						$(".insert-date").text(empl_date)
						$(".insert-time").text(empl_time)
						$(".modal-title").text(empl_time)
	
						$('#check_notif').modal('show');

						if (check_type == 'entrance'){
							voice_command("Bienvenue, " + empl_name + " !")
						}
						else if (check_type == 'departure') {
							voice_command("A bientôt, " + empl_name + " !")
						}
						setTimeout(function(){
							set_off_notif(check_id)
						}, 3000);
					}

				},Error : function(x, e) {
					alert("Some error");
				}
			});
		}


 		//Refresh delivery control panel
		var delivery_control_panel_loading = setInterval(ajax_call_all_time,5000);
		if (!location.pathname.includes('/tourniquets/dashboard')) {
			clearInterval(delivery_control_panel_loading);
		}
	});
});