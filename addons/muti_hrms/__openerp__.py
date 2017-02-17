# -*- coding: utf-8 -*-
{
    'name': "muti_hrms",

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
    'depends': ['muti_base','hr','hr_contract'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/partner_view.xml',
        'views/employee.xml',
        'views/hrms_configuration_view.xml',        
        'views/monthly_reports.xml',
        'views/menuitem.xml',
        
        
       
        
    ],
    # only loaded in demonstration mode
#     'demo': [
#         'demo.xml',
#     ],
}