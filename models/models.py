from odoo import models, fields, api

class ConstructionProjects(models.Model):
    _name = "construction.projects"
    _description = 'Consructions'

    photo = fields.Binary(
        string='Image',
        attachment=True,
        help=
        "Ce champ va contenir l'image de la recette limitée à 1024x1024px.")
    clientConstruction_Id = fields.Many2one('res.partner',string="Nom", required= True)
    name = fields.Char(string='ID', readonly=True)
    last_name = fields.Char('Last Name')
    date = fields.Date(string="Date")
    sex = fields.Selection([('m', 'Homme'),('f', 'Femme')], string ="Sex")
    type_de_construction = fields.Selection([('s','maison base'),('m','maison base'),('w','maison base'),('d','maison base'),('x','maison base')],string='Type de Construction')
    entrepot = fields.Many2one('stock.warehouse',string="Entrepot Client")
    patient_id = fields.Many2one('stock.warehouse',string="Stocke")

    @api.depends('date_of_birth')
    def onchange_age(self):
        if self.date_of_birth:
            d1 = self.date_of_birth
            d2 = datetime.today().date()
            rd = relativedelta(d2, d1)
            self.age = str(rd.years) + "y" +" "+ str(rd.months) + "m" +" "+ str(rd.days) + "d"
        else:
            self.age = "No Date Of Birth!!"