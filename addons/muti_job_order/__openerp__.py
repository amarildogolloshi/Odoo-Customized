# -*- coding: utf-8 -*-
{
    'name': "MUTI - Job Order",

    'summary': """
        Muti Group of Company's Job Order Module""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Auberon/MIS",
    'website': "http://www.auberonsolutions.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['muti_product', 'mrp', 'report'],

    # always loaded
    'data': [
        'security/groups.xml',
        'views/resources.xml',
        'views/job_order.xml',
        'views/manufacturing_order.xml',
        'views/product.xml'
    ],
    'installable': True,
    'application': True,
}