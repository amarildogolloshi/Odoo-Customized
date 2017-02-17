# -*- coding: utf-8 -*-
{
    'name': "muti_product_data",

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
    'depends': ['muti_product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
#         'csv_data/ir.sequence.csv',
        'csv_data/product.category.csv', 
#         'csv_data/product.make.csv',
#         'csv_data/product.color.csv',
#         'csv_data/product.body.csv',
#         'csv_data/product.wheel.csv',
#         'csv_data/product.type.csv',      
#         'csv_data/product.transmission.csv', 
#         'csv_data/product.mc.classification.csv',
#         'csv_data/product.partgroup.csv',
#         'csv_data/product.brand.csv',
#         'csv_data/product.model.csv',
#         'csv_data/product.template.csv'
#         'csv_data/product.major.class.csv',
#         'csv_data/product.make.csv',
#         'csv_data/product.group.csv',
#         'csv_data/product.partgroup.csv',
        'csv_data/product.template.csv',
                
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}