# -*- coding: utf-8 -*-
{
    'name': "MUTI - Dealership",

    'summary': """
        Integrated Inventory, POS and Accounting System
        """,

    'description': """
        An integrated Inventory, POS and Accounting System fpr MUTI, Design to cater products in Motorcycle (MC) units and MC spareparts, accessories and services.
    """,

    'author': "Auberon & MUTI-MIS",
    'website': "http://www.auberonsolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'point_of_sale',
                'account',
                'hr',
                'purchase',
                'point_of_sale',
                ],

    # always loaded
    'data': [
        # 'views/menus.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}