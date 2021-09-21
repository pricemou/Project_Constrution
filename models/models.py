from odoo import models, fields, api


class ConstructionProjects(models.Model):
    _name = "construction.projects"

    name = fields.Char(string='Intitulé', required=True)
    partner_id = fields.Many2one('res.partner', string="Client associé")
    start_date = fields.Date(string="Date de debut")
    construction_type = fields.Many2one(
        comodel_name='construction.type', string='Type de construction')
    warehouse = fields.Many2one('stock.warehouse', string="Entrepot")
    transaction_ids = fields.Many2many(
        'stock.picking', relation='transaction', column1='scheduled_date', column2='picking_type_id')


class ConstructionType(models.Model):
    _name = "construction.type"

    name = fields.Char(string='Intitulé')
    description = fields.Text(string='Description')
