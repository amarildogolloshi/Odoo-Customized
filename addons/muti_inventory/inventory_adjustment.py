# -*- coding: utf-8 -*-
from datetime import timedelta,time,date,datetime
from dateutil import parser
from openerp import models, fields, api, exceptions

class stock_inventory(models.Model):
    _inherit = 'stock.inventory'
    
    remark = fields.Text(string="Remarks")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('done', 'Validated'),
    ]
    ,string = 'Status')