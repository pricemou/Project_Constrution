# -*- encoding: utf-8 -*-

{
    'name': 'Gestion de stock',
    'category': 'Extras tool',
    'author': 'Pricemou Claude, Willof-God Bassanti',
    'version': '1.0',
    'depends': [
        'base',
        'account',
        'stock',
        'contacts',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir.rule.xml',
        'views/templates.xml',
        'views/views.xml',
        'menu/menu.xml',
        'reports/report.xml',
        'reports/technical_sheet.xml',
    ],
    'qweb': [
        'static/src/xml/templates.xml',
    ],
    'application': True,
    'installable': True,
}
