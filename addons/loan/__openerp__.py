# -*- coding: utf-8 -*-
{
    'name': "loan",

    'summary': """
        Loan Module""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Auberon Solutions, Inc",
    'website': "http://www.auberonsolutions.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'stock', 'muti_base','muti_product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'groups.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}