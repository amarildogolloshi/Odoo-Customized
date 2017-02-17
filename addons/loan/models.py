# -*- coding: utf-8 -*-

from openerp import models, fields, api

class config_wh_interest_promo(models.Model):
    # _inherit = 'config.wh.interest.promo'
    _name = 'config.wh.interest.promo'
    _description = __doc__

    name = fields.Char(string='Promo Description', size=100)
    #branch_ids = fields.One2many(comodel_name='config.branch', inverse_name='wh_promo_id', string='Branches')
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    brand_id = fields.Many2one(comodel_name='product.brand', string='Brand', help="Blank means for all brands")
    model_id = fields.Many2one(comodel_name='product.model', string='Model')
    cash_price = fields.Float(string='Cash Price', digits=(16, 2), required=True)
    loan_price = fields.Float(string='Loan Price', digits=(16, 2), required=True)
    min_dp = fields.Float(string='Min. Downpayment', digits=(16, 2), required=True)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
    ], string='State', default='draft')
    prod_min_dp_id = fields.One2many('product.minimum.dp','wh_interest_promo_id', string='Product Min. DP')
    branch_names = fields.Char(compute='_get_branch_names', string='Branches')
    branch_ids = fields.Many2many(
        comodel_name='config.branch', relation='branch_wh_interest_rel',
        column1='interest_id', column2='branch_id', string='Branches'
    )
    is_bnew = fields.Boolean(string='Brand New Units?')
    is_repo = fields.Boolean(string='Repo Units?')

    @api.model
    def create(self, values):
        if ('is_bnew' in values and not values['is_bnew']) and ('is_repo' in values and not values['is_repo']):
            raise Warning(_('Please select between brand new or repo units.'))

        if 'is_bnew' in values and values['is_bnew']:
            if (values['cash_price'] and values['loan_price'] and values['min_dp']) <= 0:
                raise Warning(_('Cash, Loan and Minimum Downpayment price should be greater than 0.'))

        if 'is_repo' in values and values['is_repo']:
            values['loan_price'] = 0
            values['cash_price'] = 0

        if not values['branch_ids'][0][2]:
            raise Warning(_('Please select a branch to apply the promo'))

        res_id = super(config_wh_interest_promo, self).create(values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        for check_field in ['cash_price', 'loan_price', 'min_dp']:
            if check_field in values and values[check_field] <= 0:
                raise Warning(_('Cash, Loan and Minimum Downpayment price should be greater than 0'))
        ids = super(config_wh_interest_promo, self)._write(cr, uid,  ids, values, context)
        return ids

    @api.multi
    def set_confirm(self):
        for r in self:
            brand_id = r.brand_id.id
            model_id = r.model_id.id
            min_dp = r.min_dp

            if r.is_bnew:
                loan_price = r.loan_price
                cash_price = r.cash_price
            elif r.is_repo:
                loan_price = 0
                cash_price = 0

            start_date = r.start_date
            end_date = r.end_date

        if self.is_bnew:
            search_args = [('brand_id', '=', brand_id),
                           ('model_id', '=', model_id),
                           ('is_repo', '=', False),
                           ('is_depo', '=', False)]
            bnew_state = True
            repo_state = False

        elif self.is_repo:
            search_args = [('is_repo', '=', True), ('is_sold_redeemed', '=', False)]
            bnew_state = False
            repo_state = True

        prod_ids = self.env['product.product'].search(search_args)
        if prod_ids:
            self.env.cr.execute("SELECT branch_id from branch_wh_interest_rel where interest_id = \'%s\'" % ids[0])
            branch_ids = [x[0] for x in self.env.cr.fetchall()]

            for branch_id in branch_ids:
                data = {'min_dp': min_dp, 'branch_id': branch_id,
                        'loan_price': loan_price, 'cash_price': cash_price,
                        'start_date': start_date, 'end_date': end_date }
                for prod_id in prod_ids:
                    self.env['product.product'].write(prod_id, {'mindp_ids': [(0, 0, data)]})

        self.state = 'confirm'
        self.is_bnew = bnew_state
        self.is_repo = repo_state

    @api.multi
    def set_draft(self):
        if not self.is_bnew and not self.is_repo:
            raise Warning(_('Please select between brand new or repo units.'))

        if self.is_bnew:
            search_args = [
                ('brand_id', '=', self.brand_id),
                ('model_id', '=', self.model_id),
                ('is_repo', '=', False),
                ('is_depo', '=', False)
            ]

        elif self.is_repo:
            search_args = [
                ('is_repo', '=', True),
                ('is_sold_redeemed', '=', False)
            ]

        prod_ids = self.env['product.product'].search(search_args)
        if prod_ids:
            rec_id = self.ids
            if isinstance(self.ids, list):
                rec_id = self.ids[0]

            self.env.cr.execute("SELECT branch_id from branch_wh_interest_rel where interest_id = \'%s\'" % rec_id)
            branch_ids = [x[0] for x in self.env.cr.fetchall()]

            min_dp_ids = self.env['product.minimum.dp'].search(
                [('product_id', 'in', prod_ids), ('branch_id', 'in', branch_ids)])
            if min_dp_ids:
                self.env['product.minimum.dp'].unlink(min_dp_ids)

        self.write(self.ids, {'state': 'draft'})

    @api.depends('branch_ids')
    def _get_branch_names(self):
        for r in self:
            self.env.cr.execute("SELECT branch_id from branch_wh_interest_rel where interest_id = \'%s\'" % r.id)
            branch_ids = [x[0] for x in self.env.cr.fetchall()]
            if branch_ids:
                tags = []
                for branch_id in branch_ids:
                    for rec in self.env['config.branch'].browse([branch_id]):
                        tags.append(rec.name)
                r.branch_names = ', '.join(tags)
