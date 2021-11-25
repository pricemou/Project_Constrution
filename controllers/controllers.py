# -*- coding: utf-8 -*-
from email import message
from odoo import http
from odoo.http import request
import datetime
import json

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import logging
_logger = logging.getLogger(__name__)


class Academy(http.Controller):

    # API retrait
    #     @http.route('/retrait/', auth='user')
    #     def index(self, **kw):
    #           _logger.info('------------------------')
    #           _logger.info( kw )
    #           _logger.info('------------------------')
    #           return http.request.render('CashOutWeb.retrait')

    @http.route(['/odoo/send/mail'], type='json', auth='user', methods=['POST'], csrf=False)
    def send_mail_odoo(self, **kwargs):
        html = """\
          <html>
          <head></head>
          <body>
               <p>Bonjour!<br>
               VOulez Faire un Dépôt<br>
               Here is the <a href="http://127.0.0.1:8069/valider?rep=accepter">Accepter</a> you wanted.
               </p>
          </body>
          </html>
          """
        # The mail addresses and password
        sender_address = 'claude.pricemou@groupecerco.com'
        sender_pass = '07013614'
        #    receiver_address = kwargs['receive_mail']
        receiver_address = "pricemouclaude97@gmail.com"
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
#          return http.request.render('CashOutWeb.retrait')

    @http.route('/retrait/', auth='user')
    def retrait(self, **kw):
        return http.request.render('CashOutWeb.retrait', {})

    @http.route('/annuler/', auth='user')
    def annulerCashout(self, **kw):
        transaction_id = kw['id']
        _logger.info(transaction_id)
        transaction = http.request.env['models.cashouts'].sudo().search(
            [('id', '=', str(transaction_id))])
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
        return http.request.render('CashOutWeb.recherche', {'cpt': transaction_id})

     #     envoye de notification a utilisateur
    @http.route('/recherche/', auth='user')
    def recherche(self, **kw):
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
                "idCreation": creation.id
            }

            message = """
                         <h3>Demande de cash</h3>
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
                                                  code = {
                                                      'idCreation': """+str(tab['idCreation'])+""", 'lat': pos.lat, 'lng': pos.lng};
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
                        #  <h3>l'individu concerné est proche de vous <br>
                        #  Cliquer sur accepter pour passer au paiement </h3>
                        #  <button id="accepter" onclick="valider()">accepter</button>
                        #  <button>annuler</button>
                        #  <script type= "text/javascript">
                        #       var code ="""+str(tab)+"""

                        #       function valider(){
                        #            let test =""
                        #            $.ajax({
                        #                url:"/cartParPorte",
                        #                cache:"false",
                        #                data:code,
                        #                success: function (res){
                        #                     window.location.href = `http://127.0.0.1:8069/RecherherDoor?ps=${code}`;
                        #                },
                        #                Error: function (x,e){
                        #                     console.log('some error')
                        #                }
                        #           })
                        #       }
                        #  </script>
               """
            for partner in res_partners:
                rep = partner.user_id.notify_info(message)
            return http.request.render('CashOutWeb.recherche', {'cpt': creation.id})

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
        updateOdoo = http.request.env['models.cashouts'].sudo().browse([
            int(ps)])
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
    @http.route('/odooRecherher', auth='user', )
    def rechercheOdoo(self, **kw):
        ps = kw['ps']
        updateOdoo = http.request.env['models.cashouts'].sudo().browse([
            int(ps)])
        verification = updateOdoo.type

        _logger.info(verification)
        if verification == True:
            destinataire = {
                'id': updateOdoo.client['id'],
                'name': updateOdoo.client['name'],
                'address': str(updateOdoo.client['street']),
                'longitude': updateOdoo.client['partner_longitude'],
                'latitude': updateOdoo.client['partner_latitude'],
            }
            return http.request.render('CashOutWeb.Itineraire', {'agence': destinataire})
        else:
            _logger.info('VERIFICATION == FALSE +++++++ ' + str(ps))
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
                "idCreation": ps
            }

            message = """
                        <h3>Demande de cash</h3>
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
            for user in receivers:
                rep = user.notify_info(message)
            return http.request.render('CashOutWeb.recherche', {'cpt': ps})

#     Afficher le trajet de utilisateur
    @http.route('/trajet/', auth='user')
    def index(self, **kw):
        ps = kw['cpt']
        user_id = http.request.session.uid
        user_id = http.request.env['res.users'].browse([user_id])
        personnes_refusees = http.request.env['personnes.refusees'].sudo().search(
            [('user_who_refused', '=', user_id.partner_id.id)])
        if len(personnes_refusees) > 0:
            for personne_refusee in personnes_refusees:
                personne_refusee.unlink()
                _logger.info('Utilisateur supprimé')
        updateOdoo = http.request.env['models.cashouts'].sudo().browse([
            int(ps)])
        return http.request.render('CashOutWeb.trager', {'ps': updateOdoo})

    @http.route('/comfimation/', auth='user', type='http')
    def valider(self, **kw):
        ps = kw['cpt']

        updateOdoo = http.request.env['models.cashouts'].sudo().browse([
            int(ps)])
        res_users = http.request.env['res.users'].sudo().browse(
            [int(updateOdoo.id_client)])
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

    @http.route('/rechercherAgences/', auth='user')
    def rechercherAgencesUser(self, **kw):
        return http.request.render('CashOutWeb.rechercherAgences', {})

    @http.route('/ListeAgence/', auth='user', methods=['GET'], type='http')
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
                'address': agency.street,
                'longitude': agency.partner_longitude,
                'latitude': agency.partner_latitude,
                'image': '{}/web/image?model=res.partner&id={}&field=image_128'.format(base_url, agency.id)
            }
            agencies.append(one_agency)
        return http.request.render('CashOutWeb.ListeAgence', {'agencies': agencies})

    @http.route('/itineraire/', auth='user', methods=['GET', 'POST'], type='http')
    def Itineraire(self, **kwargs):
        agence = {
            'id': kwargs['agence_id'],
            'name': kwargs['agence_name'],
            'address': kwargs['agence_address'],
            'longitude': kwargs['agence_longitude'],
            'latitude': kwargs['agence_latitude'],
        }

     #     base_url = http.request.env['ir.config_parameter'].get_param('web.base.url')
     #     all_agencies = http.request.env['res.partner'].sudo().search([('cash_out_agency','=',True)])
     #     agencies = []
     #     for agency in all_agencies:
     #          one_agency = {
     #               'id': agency.id,
     #               'name': agency.name,
     #               'address': agency.street,
     #               'longitude': agency.partner_longitude,
     #               'latitude': agency.partner_latitude,
     #               'image': '{}/web/image?model=res.partner&id={}&field=image_128'.format(base_url, agency.id)
     #          }
     #          agencies.append(one_agency)
     #          _logger.info('+++++++++++++++'+str(one_agency))
        return http.request.render('CashOutWeb.Itineraire', {'agence': agence})

    @http.route('/valider/', auth='user')
    def validerUser(self, **kw):
        agent_id = http.request.session.uid
        user_id = http.request.env['res.users'].browse([agent_id])

        vals = {
            'nameUser': user_id.name,
            'client': kw['nom'],
            'montant': kw['numero_retrait'],
            'montant_deposer': kw['montant_deposer'],
            'Ftransfer': kw['Ftransfer'],
        }

        agence = http.request.env['models.cashouts'].sudo().create(vals)
        vals = {
            'id': kw['agence'],
        }
        agence = http.request.env['agence.cashouts'].sudo().update(vals)

        return http.request.render('CashOutWeb.valider', {})

     # Methode port a port

    @http.route('/retraitParDoor/', auth='user')
    def retraitParDoor(self, **kw):
        return http.request.render('CashOutWeb.retraitParDoor', {})

    @http.route('/rechercheParPort/', auth='user')
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
                "idCreation": creation.id
            }

            message = """
                         <h3>Demande de cash</h3>
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
            return http.request.render('CashOutWeb.rechercheParPor', {'cpt': creation.id})

    @http.route('/RecherherDoor', auth='user', )
    def rechercheParPortTow(self, **kw):
        ps = kw['ps']
        updateOdoo = http.request.env['models.cashouts'].sudo().browse([
            int(ps)])
        verification = updateOdoo.type
        if verification == True:
            return http.request.render('CashOutWeb.getAgent', {'updateOdoo': updateOdoo})
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
                "idCreation": ps
            }

            message = """
                         <h3>Demande de cash</h3>
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
            return http.request.render('CashOutWeb.rechercheParPor', {'cpt': ps})

    @http.route('/rechercherAgence/', auth='user')
    def rechercherAgence(self, **kw):
        return http.request.render('CashOutWeb.rechercherAgence', {
            'teachers': ["Diana Padilla", "Jody Caroll", "Lester Vaughn"],
        })

    @http.route('/authentification/', auth='user')
    def authentification(self, **kw):
        return http.request.render('CashOutWeb.authentification', {
            'teachers': ["Diana Padilla", "Jody Caroll", "Lester Vaughn"],
        })

    @http.route('/felicitation/', auth='user')
    def felicitation(self, **kw):
        return http.request.render('CashOutWeb.felicitation', {})

    @http.route('/retraitAgence/', auth='user')
    def retraitAgence(self, **kw):

        ps = kw['agence_id']
        agence = http.request.env['agence.cashouts'].sudo().browse([int(ps)])

        return http.request.render('CashOutWeb.retraitAgence', {'agence': agence})

    @http.route('/carteAgence/', auth='user')
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
                'image': '{}/web/image?model=res.partner&id={}&field=image_128'.format(base_url, agency.id),
            }
            agencies.append(one_agency)
            data['agencies'] = agencies
        return http.request.render('CashOutWeb.carteAgence', {'data': data})

    @http.route('/get_agencies/', auth='user', type="http", methods=['GET'])
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

    @http.route('/carte/', auth='user')
    def carte(self, **kw):
        transaction_id = kw['ps']
        updateOdoo = http.request.env['models.cashouts'].sudo().browse([
            int(transaction_id)])
        _logger.info("TRANSACTION DETECTEE: "+str(transaction_id))
        return http.request.render('CashOutWeb.carteDoor', {'updateOdoo': updateOdoo})
