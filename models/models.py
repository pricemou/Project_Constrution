from odoo import models, fields, api


class ConstructionProjects(models.Model):
    _name = "construction.projects"

    name = fields.Char(string='Intitulé', required=True)
    partner_id = fields.Many2one('res.partner', string="Client associé")
    start_date = fields.Date(string="Date de debut")
    construction_type = fields.Many2one(
        comodel_name='construction.type', string='Type de construction')
    sequence_id = fields.Many2one(
        comodel_name='ir.sequence', string='Séquance de referencement')
    operation_type = fields.Many2one(
        'stock.picking.type', string="Emplacement")
    quotation_ids = fields.One2many(
        comodel_name='construction.quotation', inverse_name='construction_project_id', string='Dévis')

    @api.model
    def create(self, vals):
        result = ''
        wrd_list = vals['name'].split(' ')
        if len(wrd_list) >= 2:
            for word in wrd_list:
                result += str(word[0])
        else:
            result = str(vals['name'][:3])

        new_seqref = self.env['ir.sequence'].sudo().create(
            {
                'name': 'Séq. ' + vals['name'],
                'prefix': 'IC/TO/' + result.upper()
            })
        vals['sequence_id'] = new_seqref.id
        operation_type = self.env['ir.sequence'].sudo().create(
            {
                'name': 'Op. ' + vals['name'],
                'sequence_id': new_seqref.id,
                'code': 'outgoing'
            })
        vals['operation_type'] = operation_type.id
        return super(ConstructionProjects, self).create(vals)


class ConstructionType(models.Model):
    _name = "construction.type"

    name = fields.Char(string='Intitulé')
    description = fields.Text(string='Description')


class ConstructionQuotation(models.Model):
    _name = "construction.quotation"

    product_id = fields.Many2one(
        comodel_name='product.template', string='Article')
    estimated_quantity = fields.Char(string='Quantité prévue')
    used_quantity = fields.Char(string='Quantité utilisée')
    remaining_quantity = fields.Char(string='Quantité restante')
    construction_project_id = fields.Many2one(
        comodel_name='construction.projects', string='Projet de construction')


class StockPickInherit(models.Model):
    _inherit = "stock.picking"

    construction_project_id = fields.Many2one(
        comodel_name='construction.projects', string='Projet de construction')
