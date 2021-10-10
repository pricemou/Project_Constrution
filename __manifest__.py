# -*- encoding: utf-8 -*-

{
    'name': 'Construction',
    'category': 'Extras tool',
    'author': 'Pricemou Claude, Willof-God Bassanti',
    'version': '1.0',
    'depends': [
        'base',
        'sale',
        'purchase',
        'account',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/views.xml',
        'menu/menu.xml',
    ],
    'application': True,
    'installable': True,
}
