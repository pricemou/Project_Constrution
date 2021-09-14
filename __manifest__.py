# -*- encoding: utf-8 -*-

{
    'name': 'Construction',
    'category': 'Extras tool',
    'author': 'Pricemou Claude, Willof-God Bassanti',
    'version': '1.0',
    'depends': ['base','sale','mrp'],
    'data': [
        'security/ir.model.access.csv',
        # 'views/templates.xml',
        'views/views.xml',
        'menu/menu.xml',
        # 'static/src/views/dashboard.xml',
    ],
    'application': True,
    'installable': True,
}
