# -*- coding: utf-8 -*-
{
    'name': "CashOutWeb",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Theme',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/carte.xml',
        'views/retrait.xml',
        'views/recherche.xml',
        'views/carteAgence.xml',
        'views/retraitAgence.xml',
        'views/felicitation.xml',
        'views/ListeAgence.xml',
        'views/authentification.xml',
        'views/rechercherAgence.xml',
        'views/rechercherAgences.xml',
        'views/Itineraire.xml',
        'views/valider.xml',
        'views/retraitParPort.xml',
        'views/rechercheParPor.xml',
        'views/trager.xml',
        'views/getAgent.xml',
        'views/carteDoor.xml',
        'views/views.xml',
        'menu/transaction.xml',
        'menu/agence.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
