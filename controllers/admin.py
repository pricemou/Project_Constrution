# -*- coding: utf-8 -*-
from odoo import http
import base64
import logging
_logger = logging.getLogger(__name__) 


class Admin(http.Controller):
    def userConnect():
        usersConnect =  http.request.session.uid
        resUsers = http.request.en['res.users'].browse([usersConnect])
        return resUsers

    @http.route('/admin', auth='public',website=True)
    def indexUser(self, **kw):
        # Teachers = http.request.env['academy.teachers']
        return http.request.render('webtemplate.indexUser')

    @http.route('/signe', auth='public')
    def signe(self, **kw):
        # Teachers = http.request.env['academy.teachers']
        return http.request.render('webtemplate.signe')

    @http.route('/consulter/<int:reservation_id>', auth='public')
    def consulter(self, reservation_id):
        ordonnance = http.request.env['medical.medicament']
        reservation_all = http.request.env['medical.patient'].browse([reservation_id])
        _logger.info('------------------------')
        _logger.info(reservation_all.patient_id.name)
        _logger.info('------------------------')

        return http.request.render('webtemplate.consulter', {
            "ordonnance": ordonnance.sudo().search([]),
            "reservation" : reservation_all,
        })

    
    @http.route('/table', auth='public')
    def table(self, **kw):
       
        return http.request.render('webtemplate.table')

    @http.route('/user_profile', auth='public')
    def user_profile(self, **kw):
       
        return http.request.render('webtemplate.user_profile')

    @http.route('/chart', auth='public')
    def chart(self, **kw):
       
        return http.request.render('webtemplate.chart')

    @http.route('/annonce', auth='public', website=True)
    def annonce(self, **kw):
       
        return http.request.render('webtemplate.annonce')

    @http.route('/message', auth='public', website=True)
    def message(self, **kw):
       
        return http.request.render('webtemplate.message')
    
    @http.route('/reservation', auth='public', website=True)
    def reservation(self, **kw):
        # partnerConnect = http.request.env['res.partner'].sudo().browse([partnerId])
        try:
            usersConnectId =  http.request.session.uid

            if usersConnectId == 2: 
                rendezVous = http.request.env['medical.appointment'].sudo().search([], order="id desc",limit=5)
            else:
                usersConnect = http.request.env['res.users'].sudo().browse([usersConnectId])
                partnerId = usersConnect.partner_id.id
                rendezVous = http.request.env['medical.appointment'].sudo().search([('doctor_id.partner_id.id','=', partnerId)], order="id desc",limit=5)
                _logger.info('------------------------')
                _logger.info(usersConnectId)
                _logger.info(rendezVous)
                _logger.info('------------------------')
                
            # add logging
            return http.request.render('webtemplate.reservation',
            {
                "rendezVous":rendezVous,
            })

        except:
            _logger.info('------------------------')
            _logger.info("")
            _logger.info("errru")
            _logger.info('------------------------')


    @http.route('/commantaire', auth='public', website=True)
    def commantaire(self, **kw):
       
        return http.request.render('webtemplate.commantaire')

    @http.route('/ordonance', auth='public',website=True)
    def ordonance(self, **kw):
        
        return http.request.render('webtemplate.ordonance')


    @http.route('/enregister/medicament', auth='public',website=True)
    def prescririon(self, **kw):
        mdc00 = kw['prescription'] 
        mdc01 = kw['prescription1']
        mdc02 = kw['prescription2']
        mdc03 = kw['prescription3']
        patient_id = kw['patient_id']

        list_medicaments = [int(mdc00), int(mdc01),int(mdc02),int(mdc03)]

        user_id = http.request.session.uid
        user_id = http.request.env['res.users'].browse([user_id])

        # Creation de l' Ordonance patient
        val = {
            "patient_id":int(patient_id),
            "doctors_id": 2,
            "prescription_date": "2021-05-28 08:00:00",
            "user_id":user_id.id,
        }
        prescrition = http.request.env['medical.prescription.order'].sudo().create(val)

        _logger.info('------------------------')
        _logger.info(prescrition.patient_id.patient_id.email)
        _logger.info('------------------------')
        number = prescrition.patient_id.patient_id.phone
        email = prescrition.patient_id.patient_id.email

        # Ajout des médicament
        for cpt in list_medicaments:
            medicament_id = {
                "name": prescrition.id,
                "medicament_id": cpt,
                
            }
            prescrition_line = http.request.env['medical.prescription.line'].sudo().create(medicament_id)
        
        # res = h prescription_report()

        

        rep = prescrition.generate_pdf_report(prescrition.id)
        return http.request.render(
            'webtemplate.confirmation_docteur',{
                "prescription_pdf": rep,
                "numero_telephone": number,
                "email": email,
        })


    # @http.route('/enregister/medicaments', auth='public',website=True)
    # def rapport(self, **kw):
