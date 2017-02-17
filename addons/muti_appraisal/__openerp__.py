# -*- coding: utf-8 -*-
{
    'name': "MUTI Appraisal",

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
    'depends': ['muti_hrms'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/config_appraisal_view.xml',
        'views/appraisal_views.xml',
        'views/hr_employee_views.xml',
        'views/menuitem.xml',
        'views/scheduler_view.xml',
        'templates/rank_file_template.xml',
        'templates/managerial_template.xml',
        'templates/email_template.xml',
        'report/templates/probationary_monitoring.xml',
        'data/config.appraisal.rating.csv',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}