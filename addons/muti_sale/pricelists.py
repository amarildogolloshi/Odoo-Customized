# -*- coding: utf-8 -*-

from openerp import models, fields, api


class price_list(models.Model):
    _inherit = 'product.pricelist'


    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('reviewed', 'Reviewed'),
        ('confirmed','Confirmed')
        ], string='Status', readonly=True,default='draft')
    
    
    @api.multi
    def action_reviewed(self):
        self.state = 'reviewed'
        
    @api.multi
    def action_confirmed(self):
        self.state = 'confirmed'
        
    @api.multi
    def action_draft(self):
        self.state = 'draft'
        
class sale_order(models.Model):
    _inherit = 'sale.order'
    
    pricelist_id = fields.Many2one('product.pricelist',domain=[('state','=','confirmed')], string='Pricelist', required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Pricelist for current sales order.")
    
class pos_config(models.Model):
    _inherit = 'pos.config'
    
    pricelist_id = fields.Many2one('product.pricelist', string = 'Pricelist', required=True,domain=[('state','=','confirmed')],default = '')