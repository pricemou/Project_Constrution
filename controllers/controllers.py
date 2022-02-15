# -*- coding: utf-8 -*-
from email import message
from odoo import http
from odoo.http import request
import datetime
import json

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from math import sin, cos, sqrt, atan2, radians

import logging
_logger = logging.getLogger(__name__)


class Academy(http.Controller):
    @http.route(['/odoo/send/mail'], type='json', auth='user', methods=['POST'], csrf=False, website=True)
    def send_mail_odoo(self, **kwargs):
        html = """\
          <html>
          <head></head>
          <body>
               <p>Bonjour!<br>
               VOulez Faire un Dépôt<br>
               Here is the <a href="/valider?rep=accepter">Accepter</a> you wanted.
               </p>
          </body>
          </html>
          """
        # The mail addresses and password
        sender_address = '@groupecerco.com'
        sender_pass = ''
        #    receiver_address = kwargs['receive_mail']
        receiver_address = "@gmail.com"
        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        # The subject line
        message['Subject'] = "Demande de Retrait d'Argent "
        # The body and the attachments for the mail
        message.attach(MIMEText(html, 'html'))
        # Create SMTP session for 'sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
        session.starttls()  # enable security
        # login with mail_id and password
        session.login(sender_address, sender_pass)
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
        _logger.error('Mail Send')
        data = {'message': "Mail SEND"}
        return data


#     @http.route('/retrait/', auth='user')
#     def index(self):
#          return http.request.render('web_cash_out.retrait')

    @http.route('/cashout/', auth='user', website=True)
    def cashOuts(self, **kw):
        return http.request.render('web_cash_out.cashOuts', {})

    @http.route('/cashout/retired', auth='user')
    def retrait(self, **kw):
        return http.request.render('web_cash_out.retrait', {})

    @http.route('/annuler/', auth='user', website=True)
    def annulerCashout(self, **kw):
        transaction_id = kw['id']
        _logger.info(transaction_id)
        transaction = http.request.env['models.cashouts'].sudo().search([('id', '=', str(transaction_id))])
        vals = {
            'type': False,
            'client': None,
            'id_client': '',
        }

        vals_refuse = {
            'name': transaction.client.id,
            'user_who_refused': transaction.nameUser.id,
        }
        transaction.update(vals)
        personne_refusee = http.request.env['personnes.refusees'].sudo().create(
            vals_refuse)
        return http.request.render('web_cash_out.recherche', {'cpt': transaction_id})

     #     envoye de notification a utilisateur
    @http.route('/cashout/research/', auth='user', website=True)
    def recherche(self, **kw):
        lat_user = float(kw['lat'])
        long_user = float(kw['long'])
        user_id = http.request.session.uid

        result = {
            'cash_out_longitude' : str(long_user),
            'cash_out_latitude' : str(lat_user),
        }
        update_localisation = http.request.env['res.users'].browse([user_id])
        update_localisation.partner_id.update(result)

        if kw['montant']:
            date = datetime.datetime.strftime(datetime.datetime.utcnow(), "%Y-%m-%dT%H:%M:%SZ")
            user_id = http.request.session.uid
            user_id = http.request.env['res.users'].browse([user_id])

            vals = {
                'nameUser': user_id.partner_id.id,
                'date': date,
                'montant': kw['montant'],
                'rechercheTour': 0,
            }
            res_partners = http.request.env['res.partner'].sudo().search( [('authorized_to_cash_out', '=', True)])
            _logger.info("+++++++++localisation++++++: "+str(res_partners))
            
            creation = http.request.env['models.cashouts'].sudo().create(vals)
            tab = {
                "idCreation": creation.id,
                "montant": creation.montant,
                "nameUser": creation.nameUser.name,
            }

            message = """
                         <h3>Mr """+str(tab['nameUser'])+""" fait une demande de """+str(tab['montant'])+""" FCFA Cash</h3>
                         <button id="accepter" onclick="valider()">Accepter</button>
                         <button onclick="Refuser()>Refuser</button>
                         <script type= "text/javascript">

                              function valider(){
                                   let test =""
                                   var code = { };
                                   // Get user location
                                   if (navigator.geolocation) {
                                        navigator.geolocation.getCurrentPosition(
                                             (position) => {
                                                  const pos = {
                                                       lat: position.coords.latitude,
                                                       lng: position.coords.longitude,
                                                  };
                                                  console.log("+++++++++++++++++++++++"+pos.lng),

                                                  code = {
                                                       url:"/cartee",
                                                       cache:"false",
                                                       data:code,
                                                       success: function (res){
                                                            let test=res
                                                            console.log('*************')
                                                            console.log(test)
                                                       },
                                                       Error: function (x,e){
                                                            console.log(
                                                                'some error')
                                                       }
                                                  })
                                             },
                                             () => {
                                                  handleLocationError(
                                                      true, infoWindow, map.getCenter());
                                             },
                                             {
                                                  enableHighAccuracy: true,
                                                  timeout: 5000,
                                                  maximumAge: 0
                                             });
                                   } else {
                                        // Browser doesn't support Geolocation
                                        handleLocationError(
                                            false, infoWindow, map.getCenter());
                                   }
                              }
                         </script>
               """

            def geolocation(lat1,lon1,lat2,lon2):
                lat1 = radians(lat1)
                lon1 = radians(lon1)
                lat2 = radians(lat2)
                lon2 = radians(lon2)

                R = 6373.0
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
                c = 2 * atan2(sqrt(a), sqrt(1 - a))
                r = round(R * c, 3)
                return r
            
            for partner in res_partners:
                if (user_id.partner_id.id != partner.id) and (user_id.partner_id.authorized_to_cash_out == True):
                    lat_client = float(partner.cash_out_latitude)
                    log_client = float(partner.cash_out_longitude)
                    _logger.info("+++++++++localisation++++++: "+str(lat_client))
                    _logger.info("+++++++++localisation++++++: "+str(log_client))
                    result = geolocation(lat_user,long_user,lat_client,log_client)
                    if result <= 10:
                        partner.user_id.notify_info(message)
                    else:
                        pass
            return http.request.render('web_cash_out.recherche', {'cpt': creation.id})

    @http.route('/cartParPorte', type='http', auth='user', csrf=False, website=True)
    def cartParPorte(self, **kw):
        agent_id = http.request.session.uid
        longitude = kw['lng']
        latitude = kw['lat']
        user_id = http.request.env['res.users'].browse([agent_id])

        partner_val = {
            'partner_longitude': float(longitude),
            'partner_latitude': float(latitude),
        }
        user_id.partner_id.update(partner_val)
        _logger.info("TOUT EST OK" + str(partner_val))
        return "sauvegarde"

    # Verification de la validite de l'utilisateurs
    @http.route('/cartee', type='http', auth='user', csrf=False, website=True)
    def SaveData(self, **kw):
        ps = kw['idCreation']
        updateOdoo = http.request.env['models.cashouts'].sudo().browse([int(ps)])
        verification = updateOdoo.type
        if verification == True:
            user_id = http.request.session.uid
            user_id = http.request.env['res.users'].browse([user_id])
            message = """
                         <h3>Demande déja validée</h3>
                         <p>La demande de cash que vous essayez d'accepter a déjà été acceptée par quelqu'un.</p>
               """
            rep = user_id.notify_info(message)
        else:
            agent_id = http.request.session.uid
            idCreation = kw['idCreation']
            longitude = kw['lng']
            latitude = kw['lat']
            user_id = http.request.env['res.users'].browse([agent_id])
            updateOdoo = http.request.env['models.cashouts'].sudo().browse([
                idCreation])

            partner_val = {
                'partner_longitude': float(longitude),
                'partner_latitude': float(latitude),
            }
            user_id.partner_id.update(partner_val)

            val = {
                'id_client': agent_id,
                'client': user_id.partner_id.id,
                'type': 'True',
            }
            updateOdoo.update(val)
            return "sauvegarde"


#     Rechercher pour voir sir l'utiisateur a valider
    @http.route('/cashout/User_search', auth='user', website=True)
    def rechercheOdoo(self, **kw):
        ps = kw['ps']
        updateOdoo = http.request.env['models.cashouts'].sudo().browse([int(ps)])
        verification = updateOdoo.type
        _logger.info('updateOdoo.rechercheTour +++++++ ' + str(updateOdoo.rechercheTour))

        if updateOdoo.rechercheTour <= 1:
            val = {"rechercheTour": int(updateOdoo.rechercheTour)+ 1}
            updateOdoo.update(val)
        elif (updateOdoo.rechercheTour == 2) and(verification != True):
            return http.request.render('web_cash_out.operateur')        

        _logger.info(verification)
        if verification == True:
            return http.request.render('web_cash_out.carte', {'updateOdoo': updateOdoo})
        else:
            # Filtrer dans la base donnée
            user_id = http.request.session.uid
            user_id = http.request.env['res.users'].browse([user_id])
            long_user = float(user_id.partner_id.cash_out_longitude)
            lat_user = float(user_id.partner_id.cash_out_latitude)

            receivers = []
            personnes_refusees_list = []
            personnes_refusees = http.request.env['personnes.refusees'].sudo().search([]).mapped('name')
            res_partners = http.request.env['res.partner'].sudo().search( [('authorized_to_cash_out', '=', True), ('id', '!=', user_id.partner_id.id)])

            for personne_refusee in personnes_refusees:
                personnes_refusees_list.append(personne_refusee.name)

            for partner in res_partners:
                if (partner.name in personnes_refusees_list):
                    pass
                else:
                    user = http.request.env['res.users'].sudo().search( [('partner_id.id','=', partner.id)])
                    receivers.append(user)

            tab = {
                "idCreation": ps,
                "nameUser": updateOdoo.nameUser.name,
                "montant": updateOdoo.montant,
            }

            message = """
                        <h3>Mr """+str(tab['nameUser'])+""" fait une demande de """+str(tab['montant'])+""" FCFA Cash</h3>
                        <button id="accepter" onclick="valider()">Accepter</button>
                         <button onclick="Refuser()">Refuser</button>
                         <script type= "text/javascript">                         

                              function valider(){
                                   let test =""
                                   var code = { };
                                   // Get user location
                                   if (navigator.geolocation) {
                                        navigator.geolocation.getCurrentPosition(
                                             (position) => {
                                                  const pos = {
                                                       lat: position.coords.latitude,
                                                       lng: position.coords.longitude,
                                                  };
                                                  console.log("+++++++++++++++++++++++"+pos.lng),
                                                  code = {'idCreation': """+str(tab['idCreation'])+""", 'lat': pos.lat, 'lng': pos.lng};
                                                  console.log(code);
                                                  $.ajax({
                                                       url:"/cartee",
                                                       cache:"false",
                                                       data:code,
                                                       success: function (res){
                                                            let test=res
                                                            console.log('*************')
                                                            console.log(test)
                                                       },
                                                       Error: function (x,e){
                                                            console.log('some error')
                                                       }
                                                  })       
                                             },
                                             () => {
                                                  handleLocationError(true, infoWindow, map.getCenter());
                                             },
                                             {
                                                  enableHighAccuracy: true,
                                                  timeout: 5000,
                                                  maximumAge: 0
                                             });
                                   } else {
                                        // Browser doesn't support Geolocation
                                        handleLocationError(false, infoWindow, map.getCenter());
                                   } 
                              }
                         </script>
               """
            def geolocation(lat1,lon1,lat2,lon2):
                lat1 = radians(lat1)
                lon1 = radians(lon1)
                lat2 = radians(lat2)
                lon2 = radians(lon2)

                R = 6373.0
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
                c = 2 * atan2(sqrt(a), sqrt(1 - a))
                r = round(R * c, 3)
                return r

            for user in receivers:
                lat_client = float(user.cash_out_latitude)
                log_client = float(user.cash_out_longitude)
                result = geolocation(lat_user,long_user,lat_client,log_client)
                _logger.info('resulta +++++++ ' + str(result))
                if result <= 16:
                    user.user_ids.notify_info(message)

            return http.request.render('web_cash_out.recherche', {'cpt': ps})

    # Afficher le trajet de utilisateur
    @http.route('/door_to_door/trajet/', auth='user', website=True)
    def dortodor(self, **kw):
        ps = kw['cpt']
        updateOdoo = http.request.env['models.cashouts'].sudo().browse([ int(ps)])
        verification = updateOdoo.type
        if verification == True:
            agences = {
                'id':  updateOdoo.nameUser.id,
            }

            destinataire = {
                'id': updateOdoo.client['id'],
                'name': updateOdoo.client['name'],
                'address': str(updateOdoo.client['street']),
                'longitude': updateOdoo.client['partner_longitude'],
                'latitude': updateOdoo.client['partner_latitude'],
            }
        return http.request.render('web_cash_out.Itineraire', {'agence': destinataire,'agences':updateOdoo.nameUser})


    @http.route('/trajet/', auth='user', website=True)
    def index(self, **kw):
        ps = kw['cpt']
        updateOdoo = http.request.env['models.cashouts'].sudo().browse([ int(ps)])
        verification = updateOdoo.type
        _logger.info('updateOdoo.client.id == FALSE +++++++ ' + str(updateOdoo.client.id))


        _logger.info(verification)
        if verification == True:
            agences = {
                'id':  updateOdoo.client.id,
            }
            destinataire = {
                'id': updateOdoo.client['id'],
                'name': updateOdoo.client['name'],
                # 'image':'{}/web/image?model=res.partner&id={}&field=image_128'.format(base_url, updateOdoo.client.id),
                'address': str(updateOdoo.client['street']),
                'longitude': updateOdoo.client['partner_longitude'],
                'latitude': updateOdoo.client['partner_latitude'],
            }
        return http.request.render('web_cash_out.Itineraire', {'agence': destinataire,'agences':updateOdoo.client})

    @http.route('/comfimation/', auth='user', type='http', website=True)
    def valider(self, **kw):
        ps = kw['cpt']

        updateOdoo = http.request.env['models.cashouts'].sudo().browse([int(ps)])
        res_users = http.request.env['res.users'].sudo().browse([int(updateOdoo.id_client)])
        message = """
                        <h3>l'individu concerné est proche de vous <br>
                        Cliquer sur accepter pour passer au paiement </h3>
                    <button id="accepter" onclick="valider()">accepter</button>
                    <button>annuler</button>
                    <script type= "text/javascript">
                        function valider(){                                  
                               window.location.href = "https://moise.groupecerco.com/my";
                          }
                    </script>
               """

        rep = res_users.notify_info(message)

     # Rechercher agent

    @http.route('/cashout/agency/search/', auth='user', website=True)
    def rechercherAgencesUser(self, **kw):
        return http.request.render('web_cash_out.rechercherAgences', {})

    @http.route('/cashout/Agency_list/', auth='user', methods=['GET'], type='http')
    def ListeAgence(self):
        base_url = http.request.env['ir.config_parameter'].get_param(
            'web.base.url')
        all_agencies = http.request.env['res.partner'].sudo().search(
            [('cash_out_agency', '=', True)])
        agencies = []
        for agency in all_agencies:
            one_agency = {
                'id': agency.id,
                'name': agency.name,
                # 'address': agency.street,
                'longitude': agency.partner_longitude,
                'latitude': agency.partner_latitude,
                'image': '{}/web/image?model=res.partner&id={}&field=image_128'.format(base_url, agency.id)
            }
            agencies.append(one_agency)
        return http.request.render('web_cash_out.ListeAgence', {'agencies': agencies})

    @http.route('/cashout/itineraire/', auth='user', methods=['GET', 'POST'], type='http', website=True)
    def Itineraire(self, **kwargs):
        user_id = http.request.session.uid
        user_id = http.request.env['res.users'].browse([user_id])
        partner_id = http.request.env['res.partner'].browse([user_id.partner_id.id])

        destinataire = {
            'id': partner_id['id'],
            'name': kwargs['agence_name'],
            'address': kwargs['agence_address'],
            'longitude': kwargs['agence_longitude'],
            'latitude': kwargs['agence_latitude'],
        }
        # destinataire = {
        #         'id': partner_id['id'],
        #     }
        return http.request.render('web_cash_out.Itineraire', {'agence': destinataire ,'agences':partner_id})

    @http.route('/valider/', auth='user', website=True)
    def validerUser(self, **kw):
        return http.request.render('web_cash_out.valider', {})

     # Methode port a port

    @http.route('/cashout/door_to_door_retired', auth='user', website=True)
    def retraitParDoor(self, **kw):
        return http.request.render('web_cash_out.retraitParDoor', {})

    @http.route('/cashout/research/door_to_door_retired', auth='user', website=True)
    def rechercheParPortOne(self, **kw):

        if kw['montant']:
            date = datetime.datetime.strftime(
                datetime.datetime.utcnow(), "%Y-%m-%dT%H:%M:%SZ")
            user_id = http.request.session.uid
            user_id = http.request.env['res.users'].browse([user_id])

            vals = {
                'nameUser': user_id.partner_id.id,
                'date': date,
                'montant': kw['montant'],
            }
            res_partners = http.request.env['res.partner'].sudo().search(
                [('authorized_to_cash_out', '=', True)])
            creation = http.request.env['models.cashouts'].sudo().create(
                vals)

            tab = {
                "idCreation": creation.id,
                "montant": creation.montant,
                "nameUser": creation.nameUser.name,
            }

            message = """
                        <h3>Mr """+str(tab['nameUser'])+""" fait une demande de """+str(tab['montant'])+""" FCFA Cash</h3>
                         <button id="accepter" onclick="valider()">Accepter</button>
                         <button>Refuser</button>
                         <script type= "text/javascript">

                              function valider(){
                                   let test =""
                                   var code = { };
                                   // Get user location
                                   if (navigator.geolocation) {
                                        navigator.geolocation.getCurrentPosition(
                                             (position) => {
                                                  const pos = {
                                                       lat: position.coords.latitude,
                                                       lng: position.coords.longitude,
                                                  };

                                                  console.log(pos);
                    
                                                  $.ajax({
                                                       url:"/cartee",
                                                       cache:"false",
                                                       data:code,
                                                       success: function (res){
                                                            window.location.href = "/odooRecherher?ps="+ps+"";
                                                       },
                                                       Error: function (x,e){
                                                            console.log(
                                                                'some error')
                                                       }
                                                  })
                                             },
                                             () => {
                                                  handleLocationError(
                                                      true, infoWindow, map.getCenter());
                                             },
                                             {
                                                  enableHighAccuracy: true,
                                                  timeout: 5000,
                                                  maximumAge: 0
                                             });
                                   } else {
                                        // Browser doesn't support Geolocation
                                        handleLocationError(
                                            false, infoWindow, map.getCenter());
                                   }
                                   window.location.href = "https://moise.groupecerco.com/my";
                              }
                         </script>
               """
            for partner in res_partners:
                rep = partner.user_id.notify_info(message)
            return http.request.render('web_cash_out.rechercheParPor', {'cpt': creation.id})

    @http.route('/cashout/door_to_door_search', auth='user', website=True )
    def rechercheParPortTow(self, **kw):
        ps = kw['ps']
        updateOdoo = http.request.env['models.cashouts'].sudo().browse([
            int(ps)])
        verification = updateOdoo.type
        if verification == True:
            return http.request.render('web_cash_out.getAgent', {'updateOdoo': updateOdoo})
        else:
            receivers = []
            personnes_refusees_list = []
            personnes_refusees = http.request.env['personnes.refusees'].sudo().search([]).mapped(
                'name')
            res_partners = http.request.env['res.partner'].sudo().search(
                [('authorized_to_cash_out', '=', True)])

            for personne_refusee in personnes_refusees:
                personnes_refusees_list.append(personne_refusee.name)

            for partner in res_partners:
                if partner.name in personnes_refusees_list:
                    pass
                else:
                    user = http.request.env['res.users'].sudo().search(
                        [('partner_id', '=', partner.id)])
                    receivers.append(user)

            tab = {
                "idCreation": ps,
                "montant": updateOdoo.montant,
                "nameUser": updateOdoo.nameUser.name,
            }

            message = """
                        <h3>Mr """+str(tab['nameUser'])+""" fait une demande de """+str(tab['montant'])+""" FCFA Cash</h3>
                         <p>Une personne de votre région demande à faire du cashout</p>
                         <button id="accepter" onclick="valider()">Accepter</button>
                         <button>Refuser</button>
                         <script type= "text/javascript">
                              function valider(){
                                   let test =""
                                   var code = { };
                                   // Get user location
                                   if (navigator.geolocation) {
                                        navigator.geolocation.getCurrentPosition(
                                             (position) => {
                                                  const pos = {
                                                       lat: position.coords.latitude,
                                                       lng: position.coords.longitude,
                                                  };

                                                  console.log(pos);

                                                  code = {'idCreation': """+str(tab['idCreation'])+""", 'lat': pos.lat, 'lng': pos.lng};
                                                  console.log(code);
                                                  $.ajax({
                                                       url:"/cartee",
                                                       cache:"false",
                                                       data:code,
                                                       success: function (res){
                                                            window.location.href = '/carte?ps="""+str(tab['idCreation'])+"""'
                                                       },
                                                       Error: function (x,e){
                                                            console.log('some error')
                                                       }
                                                  })       
                                             },
                                             () => {
                                                  handleLocationError(true, infoWindow, map.getCenter());
                                             },
                                             {
                                                  enableHighAccuracy: true,
                                                  timeout: 5000,
                                                  maximumAge: 0
                                             });
                                   } else {
                                        // Browser doesn't support Geolocation
                                        handleLocationError(false, infoWindow, map.getCenter());
                                   }                   
                              }
                         </script>
               """
            for user in receivers:
                rep = user.notify_info(message)
            return http.request.render('web_cash_out.rechercheParPor', {'cpt': ps})

    @http.route('/rechercherAgence/', auth='user', website=True)
    def rechercherAgence(self, **kw):
        return http.request.render('web_cash_out.rechercherAgence', {
            'teachers': ["Diana Padilla", "Jody Caroll", "Lester Vaughn"],
        })

    @http.route('/authentification/', auth='user', website=True)
    def authentification(self, **kw):
        return http.request.render('web_cash_out.authentification', {
            'teachers': ["Diana Padilla", "Jody Caroll", "Lester Vaughn"],
        })

    @http.route('/felicitation/', auth='user', website=True)
    def felicitation(self, **kw):
        return http.request.render('web_cash_out.felicitation', {})

    @http.route('/retraitAgence/', auth='user', website=True)
    def retraitAgence(self, **kw):

        ps = kw['agence_id']
        agence = http.request.env['agence.cashouts'].sudo().browse([int(ps)])

        return http.request.render('web_cash_out.retraitAgence', {'agence': agence})

    @http.route('/carteAgence/', auth='user', website=True)
    def carteAgence(self, **kw):
        base_url = http.request.env['ir.config_parameter'].get_param(
            'web.base.url')
        all_agencies = http.request.env['res.partner'].sudo().search(
            [('cash_out_agency', '=', True)])
        data = {}
        agencies = []
        for agency in all_agencies:
            one_agency = {
                'name': agency.name,
                'address': agency.street,
                'longitude': agency.partner_longitude,
                'latitude': agency.partner_latitude,
                'image': '/web/image?model=res.partner&id={}&field=image_128'.format(agency.id),
            }
            agencies.append(one_agency)
            data['agencies'] = agencies
        return http.request.render('web_cash_out.carteAgence', {'data': data})

    @http.route('/get_agencies/', auth='user', type="http", methods=['GET'], website=True)
    def getAgencies(self):
        base_url = http.request.env['ir.config_parameter'].get_param(
            'web.base.url')
        all_agencies = http.request.env['res.partner'].sudo().search(
            [('cash_out_agency', '=', True)])
        data = {}
        agencies = []
        for agency in all_agencies:
            one_agency = {
                'name': agency.name,
                'address': agency.street,
                'image': '{}/web/image?model=res.partner&id={}&field=image_128'.format(base_url, agency.id),
                'longitude': agency.partner_longitude,
                'latitude': agency.partner_latitude
            }
            agencies.append(one_agency)
            data['agencies'] = agencies
        return json.dumps(data)

    @http.route('/carte/', auth='user', website=True)
    def carte(self, **kw):
        transaction_id = kw['ps']
        updateOdoo = http.request.env['models.cashouts'].sudo().browse([int(transaction_id)])
        _logger.info("TRANSACTION DETECTEE: "+str(transaction_id))
        return http.request.render('web_cash_out.carteDoor', {'updateOdoo': updateOdoo})

    @http.route('/cashout/operateur/', auth='user', website=True)
    def operateur(self, **kw):
        return http.request.render('web_cash_out.operateur')

    @http.route("/cashout/geolocation", methods=['POST'] ,type='json', auth='public', csrf=False)
    def geolocationGps(self, **kw):
        longitude = kw['long']
        latitude = kw['lat']
        id_partner = int(kw['id'])
        
        searchLocation = http.request.env['res.partner'].sudo().search([('id', '=', str(id_partner))])

        _logger.info("++++++++++++++++: "+str(searchLocation.id))


        vals = {
            'cash_out_longitude' : longitude,
            'cash_out_latitude' : latitude,
        }

        searchLocation.update(vals)
        _logger.info("++++++00000000+++++++++: "+str(searchLocation))
        
        if searchLocation:
            message = 'Succes' 
            return message
        else:
            message = 'erreur lors de la creation' 
            return message

    @http.route('/cashout/request', auth='user', website=True)
    def request(self, **kw):
        _logger.info("++++++00000000+++++++++: "+str(kw))

        operateur = kw['operateurs']
        user_id = http.request.session.uid
        user_id = http.request.env['res.users'].browse([user_id])
        var = "OO4O"
        if operateur =='1':
            var = "Orange"
        elif operateur =='2':
            var = "MTN"
        elif operateur =='3':
            var = "Moov"
        elif operateur =='4':
            var = "Wave"
        elif operateur == '5':
            var = "MasterCarte"
        
        val= {
            'name': user_id.partner_id.id,
            'operateur':var,
        }
        creation = http.request.env['recharger.cashouts'].sudo().create(val)
        
        return http.request.render('web_cash_out.felicitation')


