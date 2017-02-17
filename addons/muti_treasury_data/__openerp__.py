# -*- coding: utf-8 -*-
{
    'name': "muti_treasury_data",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['muti_hrms_data'],

    # always loaded
    'data': [
        'csv/hr.job.csv',
        'csv/res.users.csv',
#         'csv/res.partner.csv',        
        'csv/hr.employee.csv',
        'csv/config.department.approver.csv',
        'csv/config.authority.user.csv',
        'csv/config.request.categ.csv',
        'csv/config.request.type.csv',
        'csv/config.request.source.csv',
        'csv/config.approval.rule.csv',
        'csv/config.assigned.code.csv',
        'csv/config.department.level.csv',
        'csv/config.approval.csv',
        'csv/config.approval.chain.csv',
        'data/res_users.xml',
#         'csv/ir.sequence.csv',
#         'csv_v6/config.request.categ.csv',
#         'csv_v6/config.request.type.csv',
#         'csv_v6/config.request.source.csv',
#         'csv_v6/config.approval.rule.csv',
#         'csv_v6/config.department.level.csv',
#         'csv_v6/config.approval.csv',
#         'csv_v6/config.approval.chain.csv',
#         'csv_v6/request.request.csv',
        


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}