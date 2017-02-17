# -*- coding: utf-8 -*-

from datetime import timedelta,time,date,datetime
from dateutil import parser
from openerp import models, fields, api, exceptions
class stock_quant(models.Model):
    _inherit = 'stock.quant'
    
    age = fields.Integer(string = 'Age', compute = '_get_age',store = True)
    
    @api.depends('in_date','age','qty')
    def _get_age(self):
        for r in self:
            print r.age
            if r.qty > 0:
                today = date.today()
                trans_date = datetime.strptime(r.in_date,'%Y-%m-%d %H:%M:%S')
                transdate = trans_date.date()
                age = today - transdate
                print today,transdate
                print age
                r.age = abs((today-transdate).days)
                