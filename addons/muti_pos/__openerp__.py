# -*- coding: utf-8 -*-
{
    'name': "MUTI POS",

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
    'depends': ['point_of_sale','account_accountant','muti_hrms_data','muti_warehouse_data'],

    # always loaded
    'data': [
             'views/pos_order_view.xml',
             'views/point_of_sale1.xml',
             'views/pos_config_view.xml',
             'views/pos_config_data.xml',
             'csv/pos.config.csv',
    ],
    "qweb" : [
        'static/src/xml/pos.xml',
    ],
    # only loaded in demonstration mode
}