# -*- coding: utf-8 -*-
from openerp import models, fields, api


class muti_ppe_log(models.Model):
    _name = 'muti.ppe.log'
    _rec_name = 'reference_code'

    doc_date = fields.Date(string='Doc. Date', required=True)
    supplier_id = fields.Many2one(comodel_name='res.partner', string='Supplier', required=True)
    reference_code = fields.Char(string='Ref. Code', required=True)
    reference_date = fields.Date(string='Ref. Date', required=True)
    attachment_ids = fields.One2many(
        comodel_name='muti.ppe.log.attachment', inverse_name='log_id', string='Supporting Documents')
    log_lines = fields.One2many(comodel_name='muti.ppe.log.lines', inverse_name='log_id', required=True)
    amount_total = fields.Float(
        string='Total', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('posted', 'Posted'),
    ], string='State', readonly=True, default='draft')
    reviewed_by = fields.Many2one(comodel_name='res.users', string='Reviewed by', readonly=True)
    approved_by = fields.Many2one(comodel_name='res.users', string='Approved by', readonly=True)

    @api.depends('log_lines.unit_cost')
    def _amount_all(self):
        """
        Compute the total amounts of the Log items.
        """
        for log in self:
            amount_total = 0.0
            for line in log.log_lines:
                amount_total += line.unit_cost
            log.update({
                'amount_total': amount_total,
            })

    @api.multi
    def button_dummy(self):
        """
        Trigger view update
        """
        return True

    @api.one
    def set_draft(self):
        self.write({'state': 'draft'})

    @api.one
    def set_review(self):
        self.write({'state': 'reviewed', 'reviewed_by': self._uid})


    @api.one
    def set_approve(self):
        self.write({'state': 'approved', 'approved_by': self._uid})

    @api.one
    def set_post(self):
        self.write({'state': 'posted'})


class muti_ppe_log_lines(models.Model):
    _name = 'muti.ppe.log.lines'
    _rec_name = 'item_code'

    item_code = fields.Char(string='Code', required=True)
    log_id = fields.Many2one(comodel_name='muti.ppe.log', readonly=True)
    item = fields.Char(string='Item', required=True)
    property_type_id = fields.Many2one(comodel_name='muti.ppe.type', required=True, string='Property Type')
    brand_id = fields.Many2one(comodel_name='muti.ppe.brand', required=True, string='Brand')
    description = fields.Text(string='Description')
    unit_cost = fields.Float(string='Unit Cost', default=0.0)


class muti_ppe_type(models.Model):
    _name = 'muti.ppe.type'

    name = fields.Char(string='PE Type', help='Property Equipment Type', required=True)
    description = fields.Text(string='Description')


class muti_ppe_brand(models.Model):
    _name = 'muti.ppe.brand'

    name = fields.Char(string='Brand', required=True)
    description = fields.Text(string='Description')


class muti_ppe_log_attachment(models.Model):
    _name = 'muti.ppe.log.attachment'

    name = fields.Char(string='Name', required=True)
    log_id = fields.Many2one(comodel_name='muti.ppe.log')
    description = fields.Text(string='Description')
    attachment = fields.Binary(string='File', required=True)