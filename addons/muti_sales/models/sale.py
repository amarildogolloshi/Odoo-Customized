# -*- coding: utf-8 -*-
from openerp import models, api, fields
from datetime import datetime


class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.onchange('pricelist_id')
    def onchange_pricelist_id(self):
        for line in self.order_line:
            self.pool.get('sale.order.line').onchange_pricelist_id(line)


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id', 'order_id')
    def onchange_pricelist_id(self, external_call=None):
        this = external_call if external_call else self
        date_today = datetime.today().strftime('%Y-%m-%d')
        pricelist_discount = this.env['product.pricelist.item'].search([
            ('pricelist_id', '=', this.order_id.pricelist_id.id),
            ('product_tmpl_id', '=', this.product_id.product_tmpl_id.id),
            ('date_start', '<=', date_today),
            ('date_end', '>=', date_today)
        ])

        if pricelist_discount.compute_price == 'percentage' \
                and this.product_uom_qty >= pricelist_discount.min_quantity \
                and pricelist_discount.percent_price:

            partner_discount = this.order_id.partner_id.discount if this.order_id.partner_id.discount > 0 else pricelist_discount.percent_price
            discount = partner_discount \
                if partner_discount <= pricelist_discount.percent_price else pricelist_discount.percent_price
        else:
            discount = 0

        this.discount = discount


class pos_order(models.Model):
    _inherit = 'pos.order'

    currency_id = fields.Many2one(
        comodel_name='res.currency', related='pricelist_id.currency_id',
        string='Currency', readonly=True, required=True
    )
    @api.onchange('pricelist_id')
    def onchange_pricelist_id(self):
        for line in self.lines:
            self.pool.get('pos.order.line').onchange_pricelist_id(line)


class pos_order_line(models.Model):
    _inherit = 'pos.order.line'

    @api.onchange('product_id', 'order_id')
    def onchange_pricelist_id(self, external_call=None):
        this = external_call if external_call else self
        if not this.product_id.id:
            return
        if not this.order_id.pricelist_id.id:
            return {
                'warning': {
                    'title': 'No Pricelist',
                    'message': 'You have to select a pricelist in the sale form !\nPlease set one before choosing a product.'
                },
            }
        date_today = datetime.today().strftime('%Y-%m-%d')
        pricelist_discount = this.env['product.pricelist.item'].search([
            ('pricelist_id', '=', this.order_id.pricelist_id.id),
            ('product_tmpl_id', '=', this.product_id.product_tmpl_id.id),
            ('date_start', '<=', date_today),
            ('date_end', '>=', date_today)
        ])

        if pricelist_discount.compute_price == 'percentage' \
                and this.qty >= pricelist_discount.min_quantity \
                and pricelist_discount.percent_price:

            partner_discount = this.order_id.partner_id.discount if this.order_id.partner_id.discount > 0 else pricelist_discount.percent_price
            discount = partner_discount \
                if partner_discount <= pricelist_discount.percent_price else pricelist_discount.percent_price
        else:
            discount = 0

        price = this.pool.get('product.pricelist').price_get(this._cr, this._uid, [this.order_id.pricelist_id.id],
               this.product_id.id, this.qty or 1.0, this.order_id.partner_id.id)[this.order_id.pricelist_id.id]
        this.pool.get('pos.order.line').onchange_qty(this._cr, this._uid, this._ids, this.order_id.pricelist_id.id, this.product_id.id, 0.0, this.qty, this.price_unit)

        this.discount = discount
        this.price_unit = price
        this.tax_ids = this.product_id.taxes_id.ids