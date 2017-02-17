# -*- coding: utf-8 -*-
{
    'name': "muti_inventory",

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

    'depends': ['stock','muti_base', 'muti_hrms', 'muti_product', 'muti_sales', 'purchase'],


    # always loaded
    'data': [
        'views/muti_supplier.xml',
        'views/mc_registration.xml',
        'views/collector.xml',
#         'views/purchase.xml',
        'views/sequence.xml',
        'views/menuitem.xml',
        'views/inventory_adjustment_view.xml',
        
        
    ],
    # only loaded in demonstration mode
#     'demo': [
#         'demo.xml',
#     ],
}