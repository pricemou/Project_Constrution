from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class ConstructionProgram(models.Model):
    _name = "construction.program"
    _rec_name = "name"

    name = fields.Char(string='Libellé', required=True)
    city = fields.Char(string='Ville')
    commune = fields.Char(string='Commune')
    district = fields.Char(string='Quartier')
    description = fields.Text(string='Description')
    house_ids = fields.One2many(
        comodel_name='construction.house', inverse_name='program_id',
        string='Les maisons du programme')
    # client_ids = fields.Many2many(
    #     comodel_name='construction.client', string='Clients liés')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Ce nom de programme est déjà utilisé !"),
    ]

    # @api.constrains('name')
    # def _check_name_unicity(self):
    #     if self.search_count([
    #         ('name', '=', self.name),
    #     ]) > 1:
    #         raise ValidationError(
    #             _(f"Le nom {self.name} ! Veuillez choisir un autre nom."))


class ConstructionClient(models.Model):
    _name = "construction.client"
    _inherits = {'res.partner': 'partner_id'}
    _description = "Clients"
    _rec_name = "full_name"

    firstname = fields.Char(string='Prénom', required=True)
    id_card_num = fields.Char(string='CNI ou Passeport')
    birth_date = fields.Date(string='Date de naissance')
    birth_place = fields.Char(string='Lieu de naissance')
    nationality = fields.Char(string='Nationalité')
    bank_id = fields.Char(string='Banque')
    bank_num = fields.Char(string='Numero de compte')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Contact',
                                 auto_join=True, index=True, ondelete="cascade", required=True)
    full_name = fields.Char(string='Nom complet')

    @api.model
    def create(self, vals):
        if vals['name'] and vals['firstname']:
            vals['full_name'] = vals['name'] + ' ' + vals['firstname']
        return super(ConstructionClient, self).create(vals)

    @api.multi
    def write(self, vals):
        name = self.name
        firstname = self.firstname
        if 'name' in vals:
            name = vals['name']
        if 'firstname' in vals:
            firstname = vals['firstname']
        vals['full_name'] = name + ' ' + firstname
        return super(ConstructionClient, self).write(vals)


class ConstructionHouse(models.Model):
    _name = "construction.house"
    _rec_name = "type_id"

    lot = fields.Char(string='Numero de lot', required=True)
    ilot = fields.Char(string='Ilot')
    type_id = fields.Many2one(
        comodel_name='construction.type', string='Type de maison', required=True)
    client_id = fields.Many2one(
        comodel_name='construction.client', string='Client', required=True)
    area = fields.Char(string='Superficie')
    price = fields.Char(string='Prix unitaire')
    program_id = fields.Many2one(
        comodel_name='construction.program', string='Programme', required=True)
    move_line_ids = fields.One2many(
        comodel_name="stock.move.line", inverse_name="house_id", string="Mouvements d'articles")

    @api.depends('type_id', 'client_id', 'move_line_ids', 'program_id')
    def _all_qtygen(self):
        for record in self:
            qtygen = record.env['construction.qty_generator'].search([
                ('construction_type_id', '=', record.type_id.id)
            ])
            _logger.info('*********************')
            _logger.info(qtygen)
            if len(qtygen):
                record.qty_gen_ids = [(6, 0, qtygen.ids)]

    qty_gen_ids = fields.Many2many(
        comodel_name='construction.qty_generator', string='Fiches Tech', compute="_all_qtygen")

    _sql_constraints = [
        ('lot_uniq', 'unique (lot)', "Ce numéro de lot est déjà utilisé !"),
        ('ilot_uniq', 'unique (ilot)', "Ce numéro ilot est déjà utilisé !"),
    ]

    @api.multi
    def print_stock_report(self):
        return self.env.ref('stock_management.report_house').report_action(self)

    @api.multi
    def open_stock_move(self):
        return {
            'name': _('Rapport de stock'),
            'domain': [('house_id', '=', self.id)],
            'context': {'group_by': ['work_id', 'product_id']},
            'view_type': 'form',
            'res_model': 'stock.move.line',
            'view_id': self.env.ref('stock_management.move_line_tree_custom').id,
            'view_mode': 'tree',
            'type': 'ir.actions.act_window',
        }


class ineritPrdTemplate(models.Model):
    _inherit = "product.template"

    _sql_constraints = [
        ('lot_uniq', 'unique (name)', "Un matériau du même nom existe déjà !"),
    ]


class ConstructionMaterial(models.Model):
    _name = "construction.material"
    _description = "Matériaux"
    _inherits = {'product.product': 'product_prdt_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'default_code, name, id'

    sale_ok = fields.Boolean(default=False)
    purchase_ok = fields.Boolean(default=False)
    product_prdt_id = fields.Many2one(
        'product.product', 'Produit associé',
        auto_join=True, index=True, ondelete="cascade", required=True)

    @api.onchange('name')
    def set_default_values(self):
        self.type = 'product'


class ConstructionType(models.Model):
    _name = "construction.type"
    _rec_name = "name"

    @api.model
    def _all_work_ids(self):
        work_ids = self.env['construction.work'].search([])
        return [(6, 0, work_ids.ids)]

    name = fields.Char(string='Intitulé', required=True)
    work_ids = fields.Many2many(
        comodel_name='construction.work', required=True, default=_all_work_ids, string='Ouvrages à exécuter')

    _sql_constraints = [
        ('lot_uniq', 'unique (name)', "Ce type de maison existe déjà !"),
    ]


class ConstructionWork(models.Model):
    _name = "construction.work"
    _rec_name = "name"

    name = fields.Char(string="Nom de l'ouvrage", required=True)

    _sql_constraints = [
        ('lot_uniq', 'unique (name)', "Ce ouvrage a déjà été créé !"),
    ]


class ConstructioQtyGenerator(models.Model):
    _name = "construction.qty_generator"
    _rec_name = "display_text"

    construction_type_id = fields.Many2one(
        comodel_name='construction.type',
        string='Type de maison',
        required=True
    )
    quantity = fields.Integer(string="Quantité numérique", required=True)
    work_generator_id = fields.Many2one(
        comodel_name='construction.work_generator', string="Generateur d'ouvrages")
    display_text = fields.Char(
        string='Quantité')

    @api.model
    def create(self, vals):
        if vals['construction_type_id'] and vals['quantity']:
            quantity = vals['quantity']
            qty_name = self.env['construction.type'].browse(
                vals['construction_type_id'])
            vals['display_text'] = str(qty_name.name) + ' : ' + str(quantity)
        return super(ConstructioQtyGenerator, self).create(vals)

    @api.multi
    def write(self, vals):
        const_type = self.construction_type_id
        qty = self.quantity
        if 'construction_type_id' in vals:
            const_type = self.env['construction.type'].browse(
                vals['construction_type_id'])
        if 'quantity' in vals:
            qty = vals['quantity']

        vals['display_text'] = const_type.name + ' : ' + str(qty)

        return super(ConstructioQtyGenerator, self).write(vals)


class ConstructionWorkGenerator(models.Model):
    _name = "construction.work_generator"
    _rec_name = "work_id"

    work_id = fields.Many2one(
        comodel_name='construction.work', string='Ouvrage', required=True)
    material_qty_ids = fields.One2many(
        comodel_name='construction.qty_generator', inverse_name='work_generator_id',
        string='Quantités')
    techsheet_id = fields.Many2one(
        comodel_name='construction.tech_sheet', string='Fiche Technique')


class ConstructionTechSheet(models.Model):
    _name = "construction.tech_sheet"
    _rec_name = "material_id"

    material_id = fields.Many2one(
        comodel_name='construction.material', string='Matérau', required=True)
    work_generator_ids = fields.One2many(
        comodel_name='construction.work_generator', inverse_name='techsheet_id',
        string='Ouvrages à exécuter', required=True)
    all_constr_types = fields.Many2many(
        comodel_name='construction.type', string='Tous les types de maisons')

    _sql_constraints = [
        ('lot_uniq', 'unique (material_id)',
         "Il existe déjà une fiche technique pour cet article !"),
    ]

    @api.multi
    def print_technical_sheet(self):
        return self.env.ref('stock_management.report_techsheet').report_action(self)

    @api.model
    def create(self, vals):
        constr_type_ids = self.env['construction.type'].search([])
        vals['all_constr_types'] = [(6, 0, constr_type_ids.ids)]
        return super(ConstructionTechSheet, self).create(vals)

    @api.multi
    def write(self, vals):
        constr_type_ids = self.env['construction.type'].search([])
        vals['all_constr_types'] = [(6, 0, constr_type_ids.ids)]
        return super(ConstructionTechSheet, self).write(vals)


class StockPickInherit(models.Model):
    _inherit = "stock.picking"

    client_id = fields.Many2one(
        comodel_name='construction.client', string='Client', required=True)
    program_id = fields.Many2one(
        comodel_name='construction.program', string='Programme', domain="[]", required=True)
    house_id = fields.Many2one(
        comodel_name='construction.house', string='Maison',
        domain="[('program_id', '=', program_id),('client_id', '=', client_id)]", required=True
    )
    work_id = fields.Many2one(
        comodel_name='construction.work', string='Ouvrage', domain="[]", required=True
    )

    @api.onchange('client_id')
    def compute_program_domain(self):
        prg_domain = []
        if self.client_id:
            house_ids = self.env['construction.house'].search(
                [('client_id', '=', self.client_id.id)])
            for house in house_ids:
                id = house.program_id.id
                if not id in prg_domain:
                    prg_domain.append(id)
        return {'domain': {'program_id': [('id', 'in', prg_domain)]}}

    @api.onchange('client_id', 'program_id', 'house_id')
    def compute_work_domain(self):
        wrk_domain = []
        if self.house_id:
            wrk_domain = self.house_id.type_id.work_ids.ids
        return {'domain': {'work_id': [('id', 'in', wrk_domain)]}}

    def action_generate_backorder_wizard(self):
        raise ValidationError(
            _("La quantité que vous avez demandé n'est pas disponible dans l'entrepôt.\nVeuillez mettre à jour le stock ou annuler la réservation."))

    # @api.multi
    # def write(self, vals):
    #     for line in self.move_line_ids_without_package:
    #         quotation = self.env['construction.quotation_line'].sudo().search([
    #             ('construction_project_id', '=', self.construction_project_id.id),
    #             ('product_id', '=', line.product_id.product_tmpl_id.id)
    #         ])
    #         total_used = int(quotation.used_quantity) + int(line.qty_done)
    #         total_remaining = int(quotation.estimated_quantity) - total_used
    #         quotation.write({
    #             'used_quantity': total_used,
    #             'remaining_quantity': total_remaining
    #         })
    #     return super(StockPickInherit, self).write(vals)


class StockInventoryInherit(models.Model):
    _inherit = "stock.inventory.line"

    supplier = fields.Many2one(
        comodel_name='res.partner', string='Fournisseur')


class StockMoveInherit(models.Model):
    _inherit = "stock.move"

    house_id = fields.Many2one(
        comodel_name='construction.house', string='Maison', related="picking_id.house_id")
    work_id = fields.Many2one(
        comodel_name='construction.work', string='Ouvrage', related="picking_id.work_id")

    @api.multi
    def action_assign(self):
        """ Check availability of picking moves.
        This has the effect of changing the state and reserve quants on available moves, and may
        also impact the state of the picking as it is computed based on move's states.
        @return: True
        """
        self.filtered(lambda picking: picking.state ==
                      'draft').action_confirm()
        moves = self.mapped('move_lines').filtered(
            lambda move: move.state not in ('draft', 'cancel', 'done'))
        moves._action_assign()

        return super(StockMoveInherit, self).action_assign()


class StockMoveLineInherit(models.Model):
    _inherit = "stock.move.line"

    house_id = fields.Many2one(
        comodel_name='construction.house', string='Maison', related="move_id.house_id")
    work_id = fields.Many2one(
        comodel_name='construction.work', string='Ouvrage', related="move_id.work_id", store=True)
    qty_remaining = fields.Integer(string='Quantité restante')

    @api.multi
    def write(self, vals):
        if 'qty_done' in vals and self.house_id and self.work_id:
            qty_generator = self.env['construction.qty_generator'].search([
                ('construction_type_id', '=', self.house_id.type_id.id),
                ('work_generator_id.work_id', '=', self.work_id.id),
                ('work_generator_id.techsheet_id.material_id.product_prdt_id',
                 '=', self.product_id.id)
            ], limit=1)
            mtrl_moveline_ids = self.search([
                ('house_id', '=', self.house_id.id),
                ('work_id', '=', self.work_id.id),
                ('product_id', '=', self.product_id.id)
            ])
            line_qty_sum = 0
            for line in mtrl_moveline_ids:
                line_qty_sum += line.qty_done
                line.write({'qty_remaining': 0})
            qty = qty_generator.quantity - line_qty_sum - vals['qty_done']

            product = self.product_id.name
            unity = self.product_uom_id.name
            work = self.work_id.name
            title = self.house_id.client_id.partner_id.title.name
            client = self.house_id.client_id.partner_id.name
            htype = self.house_id.type_id.name
            qty_available = qty_generator.quantity - line_qty_sum
            if qty_available < 0:
                qty_available = 0

            if qty < 0:
                text = f"Il reste {qty_available} {unity} de {product} sur {qty_generator.quantity} pour l'ouvrage {work} de la maison {htype} de {title} {client}. Veuillez consulter la fiche technique du matériau."
                raise UserError(_(text))
            vals['qty_remaining'] = qty

        return super(StockMoveLineInherit, self).write(vals)

class StockMoveLineInherit(models.Model):
    _inherit = "account.invoice"


    @api.multi
    def send_email_payment_account(self):
        html = """
          <html>
          <head></head>
          <body>
               <p>Bonjour!<br>
               Voulez Faire un Dépôt<br>
               Here is the <a href="/valider?rep=accepter">Accepter</a> you wanted.
               </p>
          </body>
          </html>
          """
        sender_address = 'scameleons3@gmail.com'
        sender_pass = ''
        receiver_address = "@gmail.com"
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = "Demande de Retrait d'Argent "
        message.attach(MIMEText(html, 'html'))
        session = smtplib.SMTP('smtp.gmail.com', 587) 
        session.starttls() 
        session.login(sender_address, sender_pass)
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
        
        data = {'message': "Mail SEND"}
        return super(AccountInvoice, self).send_email_payment_account()




