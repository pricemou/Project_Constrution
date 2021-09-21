# -- coding: utf-8 --

from odoo import http, _
from odoo.http import request
import logging
from datetime import datetime, timedelta
from datetime import start_date
import json
import base64

_logger = logging.getLogger(__name__)


class CartController(http.Controller):
    @http.route("/tourniquets/check/entrance", auth="none", type="json", csrf=False, methods=['POST'])
    def tourniquets_entrance(self, **kwargs):
        # requete = http.request.env['tourniquets.checks'].sudo().search([('id_card_number','=',kwargs['number_cart'])])
        _logger.info("********************")
        _logger.info(kwargs['id_card'])

        try:
            barcode = http.request.env['hr.employee'].sudo().search(
                [('barcode', '=', kwargs['id_card'])])

            dic = {
                'employee_id': barcode.id,
                'barcode': barcode.barcode,
                'type': 'entrance',
                'date_time': datetime.now()
            }
            http.request.env['tourniquets.checks'].sudo().create(dic)
            _logger.info("########## Check effectué ##########" + str(dic))
            return "success"

        except:
            _logger.info("**** Erreurrrrr ****" + str(dic))
            return "error"

    @http.route("/tourniquets/check/departure", auth="none", type="json", csrf=False, methods=['POST'])
    def tourniquets_departure(self, **kwargs):
        # requete = http.request.env['tourniquets.checks'].sudo().search([('id_card_number','=',kwargs['number_cart'])])
        _logger.info("********************")
        _logger.info(kwargs['id_card'])
        try:
            barcode = http.request.env['hr.employee'].sudo().search(
                [('barcode', '=', kwargs['id_card'])])

            dic = {
                'employee_id': barcode.id,
                'barcode': barcode.barcode,
                'type': 'departure',
                'date_time': datetime.now()
            }
            http.request.env['tourniquets.checks'].sudo().create(dic)
            _logger.info("########## Check effectué ##########" + str(dic))
            return "success"

        except:
            _logger.info("**** Erreurrrrr ****" + str(dic))
            return "error"

    @http.route('/tourniquets/dashboard', type='http', auth='public', website=True, csrf=False)
    def tourniquets_dashboard(self, order=None, **kwargs):
        return request.render('tourniquets.dashboard', {})

    @http.route("/tourniquets/check/notification/", type="http", auth='public', website=True, csrf=False)
    def tourniquets_notification(self, **kwargs):
        try:
            checks = http.request.env['tourniquets.checks'].sudo().search([
                ('notified', '!=', True),
                ('date_time', '>=', datetime.now() - timedelta(seconds=60))
            ], order="id desc", limit=1)
            response = ''
            for check in checks:
                response = str(check.type) + '#' + str(check.employee_id.id) + '#' + str(
                    check.employee_id.name) + '#' + str(check.date_time) + '#' + str(check.id)
            return response
        except:
            return "error"

    @http.route("/tourniquets/check/notification/off", type="http", auth='public', website=True, csrf=False)
    def tourniquets_notification_off(self, **kwargs):
        try:
            check = http.request.env['tourniquets.checks'].sudo().search(
                [('id', '=', int(kwargs['check_id']))])
            check.update({'notified': True})
            return "notified"
        except:
            return "error"
