# -*- coding: utf-8 -*-
{
    'name': "muti_treasury",

    'summary': """
        Treasury Module """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Your Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['board','muti_hrms','document'],

    # always loaded
    'data': [
        'views/templates.xml',   
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/request_configuration_view.xml',
        'views/branch_department_view.xml',
        'views/request_view.xml',
        'views/employee_view.xml',
        'views/menuitem.xml',
        'report/rep_request.xml',
        'views/dashboard_view.xml',
        'views/scheduler_view.xml'
          
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
    
#     'css': ['static/src/css/request.css'],
    
}