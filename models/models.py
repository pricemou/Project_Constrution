from odoo import models, fields, api


class ConstructionProjects(models.Model):
    _name = "construction.projects"

    name = fields.Char(string='Intitulé', required=True)
    partner_id = fields.Many2one('res.partner', string="Client associé")
    start_date = fields.Date(string="Date de debut")
    construction_type = fields.Many2one(
        comodel_name='construction.type', string='Type de construction')
    warehouse_id = fields.Many2one('stock.warehouse', string="Entrepot")
    transaction_ids = fields.One2many(
        comodel_name='stock.picking', inverse_name='construction_project_id', string='Opération')

    @api.model
    def create(self, vals):
        result = ''
        wrd_list = vals['name'].split(' ')
        if len(wrd_list) >= 2:
            for word in wrd_list:
                result += str(word[0])
        else:
            result = str(vals['name'][:3])

        new_warehouse = self.env['stock.warehouse'].sudo().create(
            {
                'name': vals['name'],
                'code': result.upper()
            })
        vals['warehouse_id'] = new_warehouse.id
        return super(ConstructionProjects, self).create(vals)


class ConstructionType(models.Model):
    _name = "construction.type"

    name = fields.Char(string='Intitulé')
    description = fields.Text(string='Description')


class StockPickInherit(models.Model):
    _inherit = "stock.picking"

    construction_project_id = fields.Many2one(
        comodel_name='construction.projects', string='Projet de construction')
