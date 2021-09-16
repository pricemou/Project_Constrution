from odoo import models, fields, api

class ConstructionProjects(models.Model):
    _name = "construction.projects"
    _rec_name = 'clientConstruction_Id'

    image_medium = fields.Binary("Medium-sized photo", attachment=True)
    clientConstruction_Id = fields.Many2one('res.partner',string="Nom", required= True)
    # id = fields.Char(string='ID', readonly=True)
    date = fields.Date(string="Date")
    telephone = fields.Char(string="Téléphone")
    sex = fields.Selection([('m', 'Homme'),('f', 'Femme')], string ="Sex")
    type_de_construction = fields.Selection([('s','maison base'),('m','maison base'),('w','maison base'),('d','maison base'),('x','maison base')],string='Type de Construction')
    entrepot = fields.Many2one('stock.warehouse',string="Entrepot Client")
    transaction_ids = fields.Many2many('stock.picking', relation='transaction', column1='scheduled_date',column2='picking_type_id')
      