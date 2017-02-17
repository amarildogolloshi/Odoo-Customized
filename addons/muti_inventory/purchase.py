from openerp import models, fields, api, exceptions
import openerp
from datetime import timedelta,time,date,datetime
from dateutil import parser
from openerp.osv import osv
from openerp.exceptions import ValidationError

class purchase_order(models.Model):
    _inherit = 'purchase.order'
                 
class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'
    
    
    # priceunit = fields.Float(string='test',related = 'product_id.product_tmpl_id.standard_price')
    #
    # @api.onchange('priceunit')
    # def _get_price_unit(self):
    #     if self.priceunit:
    #         unitprice = self.priceunit
    #
    #         print 'price unit', unitprice
    #         self.price_unit = unitprice

class product_template(models.Model):
    _inherit = 'product.template'