# -*- coding: utf-8 -*-
{
    'name': "MUTI - Product",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Auberon Solutions, Inc.",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'templates.xml',
        'views/models_view.xml',
        'views/product_view.xml',
        'views/menuitem.xml',         
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}