# -*- coding: utf-8 -*-

from openerp import models, fields, api,SUPERUSER_ID

class price_adjustment(models.Model):
    _name = 'price.adjustment'
    name = fields.Char(string = 'Name')
    price_type = fields.Selection([('regular','Regular'),('promo','Promo')],string = 'Type')
    reference_invoice = fields.Char(string = 'Reference Invoice')
    date_from = fields.Date(string = 'Effective Date From')
    date_to = fields.Date(string = 'Effective Date To')
    pricelist_id = fields.Many2many('product.pricelist',string = 'Location/Pricelist')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('reviewed', 'Reviewed'),
        ('confirmed','Confirmed')
        ], string='Status', readonly=True,default='')
    price_adjustment_id = fields.One2many('price.adjustment.item','price_adjustment_id', string = 'Product')
    is_all = fields.Boolean(string = "All Location/Pricelist?")
    
    @api.model
    def create(self, vals):
        vals['price_type'] = 'regular'
        sequence_code = self.env(user = SUPERUSER_ID)['ir.sequence'].get('price_adjustment_seq')
        vals['name'] = sequence_code
        vals['state'] = 'draft'
        if vals['date_to']:
            vals['price_type'] = 'promo'
        res_id = super(price_adjustment,self).create(vals)
        return res_id
    
    @api.multi
    def action_reviewed(self):
        self.state = 'reviewed'
        
    @api.multi
    def action_confirmed(self):
        self.state = 'confirmed'
        date_start = self.date_from
        date_end = self.date_to
        if self.is_all == True:
            all_id = self.env['product.pricelist'].search([('active','=',True)])
            for rec in all_id:
                pricelist_ids = rec.id
                rec_id = self.id                 
                rec_det = self.env['price.adjustment.item'].search([('price_adjustment_id','=',rec_id)])
                for rec in rec_det:
                    brwse_id = self.env['price.adjustment.item'].browse(rec.id)
                
                    to_create = {
                                'pricelist_id':pricelist_ids,
                                'applied_on':'0_product_variant',
                                'date_start':date_start,
                                'date_end':date_end,
                                'compute_price':'fixed',
                                'product_id':brwse_id.product_ids.id,
                                'fixed_price':brwse_id.price
                                 
                                }
                    print to_create
        #             brwse_id.write(to_write)
                    self.env['product.pricelist.item'].create(to_create)
        else:
            
            pricelist_ids = self.pricelist_id.id
            rec_id = self.id                 
            rec_det = self.env['price.adjustment.item'].search([('price_adjustment_id','=',rec_id)])
            for rec in rec_det:
                brwse_id = self.env['price.adjustment.item'].browse(rec.id)
            
                to_create = {
                            'pricelist_id':pricelist_ids,
                            'applied_on':'0_product_variant',
                            'date_start':date_start,
                            'date_end':date_end,
                            'compute_price':'fixed',
                            'product_id':brwse_id.product_ids.id,
                            'fixed_price':brwse_id.price
                             
                            }
                print to_create
    #             brwse_id.write(to_write)
                self.env['product.pricelist.item'].create(to_create)
        
    @api.multi
    def action_draft(self):
        self.state = 'draft'
    
class price_adjustment_item(models.Model):
    _name = 'price.adjustment.item'
    
    price_adjustment_id = fields.Many2one('price.adjustment', string  = 'Price Adjustment', ondelete="cascade", onwrite="cascade", required = True)
    product_ids = fields.Many2one('product.product',string = 'Product List' )
    price = fields.Float(string = 'Price',digits =(16,2))
# 
# class price_list(models.Model):
#     _inherit = 'product.pricelist'
# 
# 
#     
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('reviewed', 'Reviewed'),
#         ('confirmed','Confirmed')
#         ], string='Status', readonly=True,default='draft')
#     
#     
#     @api.multi
#     def action_reviewed(self):
#         self.state = 'reviewed'
#         
#     @api.multi
#     def action_confirmed(self):
#         self.state = 'confirmed'
#         
#     @api.multi
#     def action_draft(self):
#         self.state = 'draft'
#         
# class product_pricelist_item(models.Model):
#     _inherit = "product.pricelist.item"
#     
#     applied_on = fields.Selection([('3_global', 'Global'),('2_product_category', ' Product Category'), ('1_product', 'Product'), ('0_product_variant', 'Product Variant'),('4_selected','Selected Product')], string="Apply On", required=True,
#                                   help='Pricelist Item applicable on selected option')
#     product_ids = fields.Many2many('product.template',string = 'Product List')
        
# class sale_order(models.Model):
#     _inherit = 'sale.order'
#     
#     pricelist_id = fields.Many2one('product.pricelist',domain=[('state','=','confirmed')], string='Pricelist', required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Pricelist for current sales order.")
#     
# class pos_config(models.Model):
#     _inherit = 'pos.config'
#     
#     pricelist_id = fields.Many2one('product.pricelist', string = 'Pricelist', required=True,domain=[('state','=','confirmed')],default = '')