# -*- coding: utf-8 -*-
{
    'name': "muti_hrms_data",

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
        # 'security/ir.model.access.csv',
        'csv_data/employee.religion.csv',
        'csv_data/employee.education.level.csv',
        'csv_data/employee.education.course.csv',
        'csv_data/employee.medical.blood.csv',
        'csv_data/employee.medical.phydisorder.csv',
        'csv_data/employee.medical.allergy.csv',
        'csv_data/employee.medical.healthprob.csv',
        'csv_data/employee.skills.category.csv',
        'csv_data/employee.skills.csv',
        'csv_data/employee.conf.seminar.csv',
        'csv_data/employee.external.jobs.csv',
        'csv_data/config.job.level.csv',
        'csv_data/hr.job.csv',
        'csv_data/employee.conf.license.csv',
        'csv_data/hr.department.csv',
        'csv_data/hr.employee.csv',
#         'csv_data/employee.status.csv'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}