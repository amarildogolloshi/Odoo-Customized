# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions


class config_delivery_receipt_series(models.Model):
    _name = 'config.delivery.receipt.series'
    _description = """
    ###################### Developers Note ####################
    General Objective: Entry Control For DR Series
    Specific Objectives:
        1. Working entry for add, edit and void for Control
        2. Generate Series as detail/s
    ##########################################################
    """
    branch_id = fields.Many2one(comodel_name="config.branch", string="Branch", required=True, )
    name = fields.Char(string="Series", required=False, size=100, default=None)
    series_from = fields.Integer(string="Series Start", required=True, )
    series_to = fields.Integer(string="Series End", required=True, )
    leaves = fields.Integer(string="# of Pages", required=True, )
    cdr_ids = fields.One2many(comodel_name="config.delivery.receipt", inverse_name="cdr_id", string="Receipts",
                              required=False, readonly=True)
    state = fields.Selection(string="Status", selection=[('draft', 'Draft'),
                                                         ('fin', 'Finalized'),
                                                         ('init', ''), ], required=False, default='init')

    @api.model
    def create(self, vals):
        print 'create vals:'
        vals['state'] = 'draft'
        vals['name'] = 'DR' + str(vals['series_from']).zfill(8) + '-DR' + str(vals['series_to']).zfill(8)
        print 'create vals:', vals

        result = super(config_delivery_receipt_series, self).create(vals)
        return result

    # @api.multi
    # def write(self, vals):
    #     vals['name'] = str(vals['series_From'])+'-'+str(vals['series_to'])
    #     result = super(config_delivery_receipt_series, self).write(vals)
    #
    #     return result


    @api.onchange('leaves', 'series_from')
    def _onchange_series(self):
        print '_onchange_series', self.leaves, self.series_from

        if self.leaves and self.series_from:
            leaves = self.leaves
            series_from = self.series_from
            self.series_to = (series_from + leaves) - 1
        else:
            return None

    @api.multi
    def action_final(self):
        start = self.series_from
        for x in range(0, self.leaves):
            vals = {'branch_id': self.branch_id.id}
            vals['cdr_id'] = self.id
            vals['dr_number'] = 'DR' + str(self.series_from + x).zfill(8)
            print 'vals', vals
            self.env['config.delivery.receipt'].create(vals)

        self.state = 'fin'


class config_delivery_receipt(models.Model):
    _name = 'config.delivery.receipt'
    _description = """
    ###################### Developers Note ####################
    General Objective: Generated Control For DR #
    Specific Objectives:
        1. To be auto-generated from above
    ###########################################################
    """

    cdr_id = fields.Many2one(comodel_name="config.delivery.receipt.series", string="DR Series", required=False, )
    branch_id = fields.Many2one(comodel_name="config.branch", string="Branch", required=True, )
    dr_number = fields.Char(string="DR Number", required=True, size=50)
    dr_id = fields.Many2one(comodel_name="delivery.receipt", string="DR Service", required=False, default=None)
    state = fields.Selection(string="Status", selection=[('unused', 'Unused'),
                                                         ('used', 'Used'),
                                                         ('void', 'Void'), ], required=False, default='unused')
