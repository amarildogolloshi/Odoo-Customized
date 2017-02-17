from openerp import models, fields, api, tools
from datetime import *
from time import strptime
from time import mktime
import math
import calendar
from openerp.tools.translate import _

#
# class muti_job_order_type(model.Models):
#     _name = 'muti.job.order'
#     _order = 'name asc'
#
#     name = fields.Char(string='type', size=40)
class mrp_production(models.Model):
    _inherit = 'mrp.production'

    barcode = fields.Char(related='product_id.barcode', string='Product Barcode')
    total_cost = fields.Float(string='Total Cost', compute='_get_total_cost')
    amount_spent = fields.Float(string='Amount Spent', compute='_get_amount_spent')

    @api.depends('move_lines')
    def _get_total_cost(self):
        total_cost = 0.0
        for r in self:
            for m in r.move_lines:
                total_cost += (m.product_id.product_tmpl_id.standard_price * m.product_qty)
            r.total_cost = total_cost

    @api.depends('move_lines2')
    def _get_amount_spent(self):
        amount_spent = 0.0
        for r in self:
            for m in r.move_lines2:
                amount_spent += (m.product_id.product_tmpl_id.standard_price * m.product_qty)
            r.amount_spent = amount_spent


    # @api.onchange('state')
    # def onchange_state(self):
    #     print self.state, '<---------'
    #     if self.state == 'draft':
    #         # return self.env['report'].render('mrp.mrp_production_form_view')
    #         context = dict(self.env.context or {}, active_ids=[self.id], active_model=self._name)
    #         return {
    #             'type': 'ir.actions.report.xml',
    #             'report_name': 'mrp.mrp_production_form_view',
    #             'context': context,
    #         }
    @api.one
    def button_confirm(self):
        print self.state
        super(mrp_production, self).button_confirm(self)




class muti_job_order(models.Model):
    _name = 'muti.job.order'
    _description = __doc__
    _rec_name = 'jo_number'
    _order = 'jo_number desc'

    def _get_branch_id(self, uid=None, context=None):
        res = self.env['res.users'].browse(self._uid)
        if res:
            return res['branch_id'].id
        return False

    def _get_user_id(self):
        return self._uid

    branch_id = fields.Many2one(
        comodel_name='config.branch',
        string='Branch',
        required=False,
        default=_get_branch_id,
        readonly=True
    )
    transaction_date = fields.Date(string='Transaction Date', default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    jo_number = fields.Char(string='JO Number', size=20, readonly=True)
    jo_date = fields.Date('Document Date', required=True, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    mc_unit = fields.Many2one(comodel_name='product.template', string='MC Repossessed Unit')
    engineno = fields.Char(related='mc_unit.engineno', string='Engine Number')
    chassisno = fields.Char(related='mc_unit.chassisno', string='Chassis Number')
    make = fields.Many2one(comodel_name='product.brand', related='mc_unit.brand_id', string='Make/Brand')
    model = fields.Many2one(comodel_name='product.model', related='mc_unit.model_id', string='Model')
    color = fields.Many2one(comodel_name='product.color', related='mc_unit.color_id', string='Color')
    body = fields.Many2one(comodel_name='product.body', related='mc_unit.body_id', string='Body')
    wheel = fields.Many2one(comodel_name='product.wheel', related='mc_unit.wheel_id', string='Wheel')
    transmission = fields.Many2one(comodel_name='product.transmission', related='mc_unit.transmission_id', string='Transmission')
    job_order_ids = fields.One2many(comodel_name='muti.job.order.detail', inverse_name='job_order_id', string='Job Order Detail')
    items_total_amount = fields.Float(compute='_get_items_total_amount', string='Total Amount', store=True)
    machining = fields.Text(string='Machining')
    job_desc = fields.Text(string='Job Description')
    recommended_by = fields.Many2one(comodel_name='res.users', string='Recommended By')
    prepared_by = fields.Many2one(comodel_name='res.users', string='Prepared By', default=_get_user_id)
    reviewed_by = fields.Many2one(comodel_name='res.users', string='Reviewed By')
    approved_by = fields.Many2one(comodel_name='res.users', string='Approved By')
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('cancel', 'Cancel'),
        ('confirm', 'Confirmed'),
        ('recommend', 'Recommend'),
        ('review', 'Reviewed'),
        ('approve', 'Approved'),
        ('disapprove', 'Disapproved'),
    ], string='State', readonly=True, default='draft')

    # @api.depends('state')
    # def _get_state(self):
    #     for r in self:
    #         print '---', r.state
    #         if not r.state:
    #             r.state = 'draft'

    @api.model
    def create(self, values):
        values['branch_id'] = self._get_branch_id([0])
        validate_mc = self.search([
            ('mc_unit', '=', values['mc_unit']),
            ('branch_id', '=', values['branch_id']),
            ('state', '!=', 'cancel')
        ])
        if validate_mc:
            raise Warning(_('Engine Number already exist in Job Order.'))

        # is_offline = tools.config.get('offline_mode')
        is_offline = tools.config.get('offline_mode')
        if not is_offline:
            year = datetime.now().strftime('%Y-%m-%d')[:4]
            seq_number = self.env['sequence'].get_id('Job Order', values['branch_id'], year)
            values['jo_number'] = seq_number
        # print 'values------->', values
        return super(muti_job_order, self).create(values)

    @api.model
    def write(self, values):
        draftstate = False
        if not values.has_key('state'):
            res = self.browse(self.ids)
            if res[0]['state'] in ('draft'):
                if values.has_key('mc_unit'):
                   draftstate = True
                if values.has_key('recommended_by'):
                   draftstate = True
                if values.has_key('approve_by'):
                   draftstate = True

        if draftstate:
            br_id = self._get_branch_id(self.ids)

            if not values.has_key('mc_unit'):
                # den = self.browse(self._cr, self._uid, self.ids)
                mc_id = ['mc_unit'].id
            else:
                mc_id = values['mc_unit']

            validate_search = self.search([
                ('id', '!=', self.ids[0]),
                ('mc_unit', '=', mc_id),
                ('branch_id', '=', br_id),
                ('state', '!=', 'cancel')
            ])
            if validate_search:
                uro = self.read(validate_search[0], ['jo_number'])
                uro_no = uro['jo_number']
                raise Warning(_('Engine Number already exist in Job Order: %s.' % (uro_no)))

        return super(muti_job_order, self).write(values)

    @api.one
    def set_recommend(self):
        self.write({'state': 'recommend', 'recommended_by': self._uid})

    @api.one
    def set_review(self):
        self.write({'state': 'review', 'reviewed_by': self._uid})

    @api.one
    def set_approve(self):
        self.write({'state': 'approve', 'approved_by': self._uid})

    @api.one
    def set_disapprove(self):
        self.write({'state': 'disapprove'})

    @api.one
    def set_cancel(self):
        self.write({'state': 'cancel'})

    @api.one
    def set_confirm(self):
        self.write({'state': 'confirm'})

    @api.one
    def set_draft(self):
        self.write({'state': 'draft'})

    @api.depends('job_order_ids')
    def _get_items_total_amount(self):
        """
        @comment Function that automatically computes for the Items Total Amount upon saving
        """
        items_total = 0.00

        for r in self:
            for n in r.job_order_ids:
                res = self.env['muti.job.order.detail'].browse(n.id)
                if res:
                    items_total += res['qty']*res['unit_cost']
            r.items_total_amount = items_total


class muti_job_order_detail(models.Model):
    _name = 'muti.job.order.detail'
    _description = __doc__

    job_order_id = fields.Many2one(comodel_name='muti.job.order', string='Job Order')
    spare_part = fields.Char(string='Spare Parts', size=50)
    qty = fields.Float(string='Quantity', digits=(16, 2))
    unit_cost = fields.Float(string='Unit Cost', digits=(16, 2))
    item_total = fields.Float(compute='_get_item_total', string='Item Total', store=True)
    is_part_available = fields.Boolean(string='(Deffective Parts) Available?')

    @api.depends('qty', 'unit_cost')
    def _get_item_total(self):
        """
        @comment Function that automatically computes for the Items Total Amount upon saving
        @return item_total
        """
        items_total = 0.00
        for r in self:
            items_total += r.qty*r.unit_cost
            r.item_total = items_total