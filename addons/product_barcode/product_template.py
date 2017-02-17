# -*- coding: utf-8 -*-

from openerp import models, fields, api


class product_template(models.Model):
    _inherit = 'product.template'

    child_product_ids = fields.Many2many('product.product', string='Product Content')
