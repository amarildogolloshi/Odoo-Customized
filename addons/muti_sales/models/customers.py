# -*- coding: utf-8 -*-
from openerp import models, fields, api


class res_partner(models.Model):
    _inherit = 'res.partner'

    # Add a new column to the res.partner model, by default partners are not
    # instructors
    # rep_type = fields.Many2one(comodel_name='res.partner.rep.type', string='Sale representative type')
    employee = fields.Boolean(string='Is an Employee', help='Is partner an employee?')
    wholesaler = fields.Boolean(string='Is a Wholesaler', help='Is partner a wholesaler?')
    retailer = fields.Boolean(string='Is a Retailer', help='Is partner a retailer?')
    point_sale_barcode = fields.Char(string='Point of Sale Barcode')
    discount = fields.Float(string='Max Discount (%)', help='Discount in percent')
    active = fields.Boolean(string='Active')
    address = fields.Text(string='Address', compute='get_compute_address')

    @api.depends('street', 'street2', 'city', 'state_id', 'zip', 'country_id')
    def get_compute_address(self):
        for r in self:
            street = r.street if r.street else ''
            street2 = r.street2 if r.street2 else ''
            city = r.city if r.city else ''
            state_name = r.state_id.name if r.state_id.name else ''
            zip = r.zip if r.zip else ''
            country_name = r.country_id.name if r.country_id.name else ''
            r.address = '%s %s %s %s %s %s' % (street, street2, city, state_name, zip, country_name)

    @api.onchange('wholesaler')
    def onchange_wholesaler(self):
        if not self.wholesaler:
            self.discount = 0.0