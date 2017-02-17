# -*- coding: utf-8 -*-
{
    'name': "MUTI Base",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Auberon/MIS",
    'website': "http://www.mycompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

    # 'qweb': [
    #     "static/src/xml/base.xml",
    # ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/localization_view.xml',
        'data/document_number_data.xml',
        'data/config.area.csv',
        'data/res.partner.csv',
        'data/res.company.csv',
        'data/muti_base_data.xml',
        'data/config.province.csv',
        'data/config.city.csv',
        'data/config.barangay.csv',
        'data/config.branch.csv',
        'views/config_branch.xml',
        'views/config_receipts_series.xml',
        'data/ir.sequence.csv',
        # 'security/ir.model.access.csv'

    ],
    'installable': True,
    'auto_install': False,

}
