# -*- coding: utf-8 -*-
from datetime import timedelta,time,date,datetime
from dateutil import parser
from openerp import models, fields, api, exceptions

    
class config_department(models.Model):
    _inherit = 'hr.department'

    active = fields.Boolean(string="Active", default="True")
    name = fields.Char(string = 'Name')
#     branch_id = fields.Many2one('config.branch',string = 'Branch')
#     company_id = fields.Many2one('res.company',string = 'Company')
    old_dept_code = fields.Char(string = 'Code')
    emp_ids = fields.One2many('hr.employee','department_id',string = 'Employees')

class company(models.Model):
    _inherit = 'res.company'    
    
    bu_class_id = fields.Many2one('config.bu.classification', string="BU Classification")
    
        
class config_bu_classification(models.Model):
    _name = 'config.bu.classification'
    _order = 'name'
    
    name = fields.Char(string="Name")
    desc = fields.Text(string="Description")
    

    
    
    


    