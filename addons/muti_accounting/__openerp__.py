# -*- coding: utf-8 -*-
{
    'name': "muti_accounting",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Auberon/MIS",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['muti_base','account','account_accountant', 'muti_sale', 'muti_product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'csv/account.account.csv',
        'views/pdc_acknowledgment.xml',
    ],
#     # only loaded in demonstration mode
#     'demo': [
#         'demo/demo.xml',
#     ],
}