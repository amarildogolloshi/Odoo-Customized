# # -*- coding: utf-8 -*-
#
# from openerp import models, fields, api
#
#
# class Barcode(models.Model):
#     _name = 'product.barcode'
#     _barcode_type = 'code128'
#     name = fields.Char(string='Barcode', required=True)
#     product_id = fields.Many2one('product.product', string='Product', required=True)
#     parent_product_id = fields.Many2one('product.barcode', string='Parent Product', ondelete='set null')
#
#
