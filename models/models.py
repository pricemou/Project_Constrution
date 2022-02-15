from odoo import models, fields, api


class ModelA(models.Model):
    _name = 'models.cashouts'
    _rec_name = 'nameUser'

    # id_User = fields.Char(string="Identifiant de l'émetteur de la demande")
    nameUser = fields.Many2one('res.partner', string='Identifiant de l\'émetteur de la demande')
    date = fields.Char(string='Date de la transaction')
    type = fields.Boolean(string='Type')
    id_client = fields.Char(string="Identifiant du receveur")
    client = fields.Many2one('res.partner', string='Nom du receveur')
    montant = fields.Char(string="Montant de la transaction")
    nomOperation = fields.Char(string='Nom de l\'opération')
    rechercheTour = fields.Integer(string="Le nombre de tour de la rechercher")
    
    
    
class MyMixedInSaleOrder(models.Model):
    _inherit = ['models.cashouts']

    montant_deposer = fields.Char(string='Numéro de retrait')
    Ftransfer = fields.Char(string='Frais de transfert opérateur')


class AgencePartner(models.Model):
    _inherit = 'res.partner'

    cash_out_agency = fields.Boolean(string='Agence CASH OUT?')
    cash_out_longitude = fields.Char(string='Longitude')
    cash_out_latitude = fields.Char(string='Latitude')
    # authorized_to_cash_door_to_door = fields.Boolean(string='Agence CASH OUT?')



class PersonneRefusee(models.Model):
    _inherit = 'res.partner'

    liste_refuse = fields.One2many('personnes.refusees', 'user_who_refused', string='Liste des personnes refusées')
    authorized_to_cash_out = fields.Boolean(string='Autorisé à faire du CASHOUT ?')

class TransactionsCASHOUT(models.Model):
    _inherit = 'res.partner'

    transaction_list = fields.One2many('models.cashouts', 'nameUser', string='Liste')


class PersonnesRefuseesCASHOUT(models.Model):
    _name = 'personnes.refusees'

    name = fields.Many2one('res.partner', string='Nom de la personne refusée')
    user_who_refused = fields.Many2one('res.partner', string='Nom de la personne qui a refusé')

class demandeRechargementCASHOUT(models.Model):
    _name = 'recharger.cashouts'

    name = fields.Many2one('res.partner', string="Nom du client")
    operateur = fields.Char(string="Opérateur")
    date  = fields.Char(string='Date de la demande')



