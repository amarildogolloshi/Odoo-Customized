# -*- coding: utf-8 -*-
{
    'name': "MUTI Warehouse",

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
    'depends': ['muti_base','stock_picking_wave', 'purchase','point_of_sale'],

    # always loaded
    'data': [
        #'configurations/config_warehouse_view.xml',
        'views/price_adjustment_view.xml',
        'views/menus.xml',
        'views/stock_quant_view.xml',
        'csv/ir.sequence.csv',
        
    ],
    # only loaded in demonstration mode
#     'demo': [
#         'demo.xml',
#     ],
}
