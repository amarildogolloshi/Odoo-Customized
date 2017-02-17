import openerp
from datetime import timedelta,time,date,datetime
from dateutil import parser
from openerp import models, fields, api, exceptions
from openerp.osv import osv

class details(models.Model):
    _name = 'mc.details'
    
    name=fields.Char(string='Client')
    engine_no=fields.Char(string='Engine Number')
    brand=fields.Char(string='Make/Brand')
    is_repo=fields.Boolean(string='Is Repo?')
    batch_id=fields.Many2one(string='Batch')
    chassis_no=fields.Char(string='Chassis Number')
    model=fields.Char(string='Model')
    or_cr=fields.Char()
    plate_no=fields.Char()
    claimed_date=fields.Date()
    or_cr_date=fields.Date()
    claimed_by=fields.Date()
    

    

    
    
    