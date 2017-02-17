# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime
import calendar
from openerp.osv import osv


class pos_order(osv.osv):
    _inherit = 'pos.order'

    user_id = fields.Many2one(comodel_name='res.users', string='Salesman', index=True,
        help="Person who uses the cash register. It can be a reliever, a student or an interim employee."
    )


class muti_mechanic(models.Model):
    _name = 'muti.mechanic'
    _rec_name = 'user_id'
    _order = "id desc"

    user_id = fields.Many2one(
        comodel_name='res.users', string='Mechanic',
        domain='["|", ("groups_id", "=", "External Mechanic"), ("groups_id", "=", "Internal Mechanic")]'
    )
    type_id = fields.Many2one(
        comodel_name='res.groups', string='Type',
        compute='_get_mechanic_type', readonly=True
   )
    latest_commission = fields.Float(
        string='Latest commission', store=True,
        default=0, compute='_get_latest_commission'
    )
    total_commission = fields.Float(
        string='Total commission', store=True,
        default=0, compute='_get_total_commission'
    )
    commission_ids = fields.One2many(
        comodel_name='muti.commission.record',
        inverse_name='mechanic_id', string='Commissions',
        # readonly=True
    )

    _sql_constraints = [
        ('user_id', 'unique(user_id)', 'Mechanic record already exists!')
    ]

    @api.depends('user_id')
    def _get_mechanic_type(self):
        for r in self:
            group_id = self.env['res.groups'].search([
                '|',
                ('name', '=', 'External Mechanic'),
                ('name', '=', 'Internal Mechanic'),
                ('users', 'in', r.user_id.id)
            ])
            if group_id:
                r.type_id = group_id[0]

    @api.depends('commission_ids')
    def _get_latest_commission(self):
        for r in self:
            if r.commission_ids.ids:
                c_id = self.pool.get('muti.commission.record').\
                    search(self._cr, self._uid, [('id', 'in', r.commission_ids.ids)], 0, 1, 'date_to desc')
                if c_id:
                    r.latest_commission = self.pool.get('muti.commission.record').read(
                        self._cr, self._uid, c_id[0], ['commission']
                    )['commission']

    @api.depends('commission_ids')
    def _get_total_commission(self):
        for r in self:
            total_commission = 0.0
            if r.commission_ids.ids:
                commissions = self.pool.get('muti.commission.record').read(
                    self._cr, self._uid, r.commission_ids.ids, ['commission']
                )
                if commissions:
                    total_commission = sum([c['commission'] for c in commissions])
            r.total_commission = total_commission

    def _get_commission(self, total_sales, external_mechanic=False):
        commission = 0
        percentage = 0
        if external_mechanic:
            commission = total_sales * 0.03
            percentage = 3
        elif total_sales >= 30000.0 and total_sales <= 39999.99:
            commission = total_sales * 0.01
            percentage = 1
        elif total_sales >= 40000.0 and total_sales <= 49999.99:
            commission = total_sales * 0.02
            percentage = 2
        elif total_sales >= 50000.0 and total_sales <= 59999.99:
            commission = total_sales * 0.03
            percentage = 3
        elif total_sales >= 60000.0 and total_sales <= 79999.99:
            commission = total_sales * 0.04
            percentage = 4
        elif total_sales >= 80000.0:
            commission = total_sales * 0.05
            percentage = 5

        return {'amount': total_sales, 'commission': commission, 'percentage': percentage}

    @api.one
    def generate_commission_records(self):
        groups_name = self.type_id.name
        if groups_name == 'External Mechanic':
            self._external_mech_generate_commission_records()
            return False
        elif groups_name == 'Internal Mechanic':
            self._internal_mech_generate_commission_records()
            return True
        else:
            return False

    def _create_commission_record(self, str_current_date_from, str_current_date_to, external_mechanic=False):
        is_record_exist = self.env['muti.commission.record'].search(
                args=[
                    ('date_from', '=', str_current_date_from),
                    ('date_to', '=', str_current_date_to)
                ]
            )
        if not is_record_exist:
            pos_order_line = self.env['pos.order.line'].search(
                args=[
                    ('order_id.user_id', '=', self.user_id.id),
                    ('create_date', '>=', str_current_date_from),
                    ('create_date', '<=', str_current_date_to)
                ]
            )

            total_sales = sum([x['price_subtotal'] for x in pos_order_line])
            sales_amount_to_be_commissioned = 0.0
            service_commission = 0.0
            if external_mechanic:
                sales_amount_to_be_commissioned = total_sales
            else:
                for pos_order in pos_order_line:
                    # P100.00 for every cylinder block sleeve
                    # P50.00 for every cylinder block rebore
                    # P40.00 for crankshaft press.
                    product_name = pos_order.product_id.name
                    if product_name == 'Cylinder Block Sleeve':
                        service_commission += 100.00
                    elif product_name == 'Cylinder Block Rebore':
                        service_commission += 50.00
                    elif product_name == 'Crankshaft Press':
                        service_commission += 40.00
                    sales_amount_to_be_commissioned += pos_order.price_subtotal

            commissioned = self._get_commission(sales_amount_to_be_commissioned, external_mechanic)
            total_commission = commissioned['commission'] + service_commission
            self.env['muti.commission.record'].create({
                'mechanic_id': self.id,
                'date_from': str_current_date_from,
                'date_to': str_current_date_to,
                'total_sale': total_sales,
                'commission': total_commission,
                'percent_commissioned': commissioned['percentage'],
            })

    def _external_mech_generate_commission_records(self):
        # Date when the monthly computation should start by checking where it ended.
        current_date_to = datetime.datetime.strptime(
            str(datetime.datetime.today())[0:10],
            '%Y-%m-%d'
        )
        latest_comm_rec = self.env['muti.commission.record'].search(
            args=[
                ('mechanic_id', '=', self.id)
            ], offset=0, limit=1, order='date_to desc'
        )
        if latest_comm_rec:
            latest_rec_data = datetime.datetime.strptime(
                latest_comm_rec.date_to + ' 23:59:59', '%Y-%m-%d %H:%M:%S')

            record_start_date = datetime.datetime(latest_rec_data.year, latest_rec_data.month, latest_rec_data.day)
            record_start_date += datetime.timedelta(days=1)
            record_start_date = str(record_start_date) if record_start_date < current_date_to else False
        else:
            record_start_date = self.env['pos.order'].search(
                args=[('user_id', '=', self.user_id.id)], offset=0, limit=1, order='create_date asc'
            )
            record_start_date = record_start_date.create_date if record_start_date else None

        # There's record
        if record_start_date:
            current_date_to = str(current_date_to)[0:10] + ' 23:59:59'
            self._create_commission_record(
                str_current_date_from=record_start_date,
                str_current_date_to=current_date_to,
                external_mechanic=True
            )

    def _internal_mech_generate_commission_records(self):
        # Date when the monthly computation should start by checking where it ended.
        latest_comm_rec = self.env['muti.commission.record'].search(
            args=[('mechanic_id', '=', self.id)], offset=0, limit=1, order='date_to desc'
        )
        if latest_comm_rec:
            latest_rec_data = datetime.datetime.strptime(
                latest_comm_rec.date_to + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
            record_start_date = datetime.datetime(latest_rec_data.year, latest_rec_data.month, latest_rec_data.day)
            record_start_date += datetime.timedelta(days=1)
            record_start_date = str(record_start_date)
        else:
            record_start_date = self.env['pos.order'].search(
                args=[('user_id', '=', self.user_id.id)], offset=0, limit=1, order='create_date asc'
            )
            record_start_date = record_start_date.create_date if record_start_date else None

        # There's record
        if record_start_date:
            current_date = datetime.datetime.strptime(record_start_date, '%Y-%m-%d %H:%M:%S')
            current_date_from = datetime.datetime(current_date.year, current_date.month, current_date.day)

            # Date when the program should end
            this_day = datetime.date.today()
            last_month = (this_day.month - 1)
            this_year = this_day.year
            if last_month is 0:
                last_month = 12
                this_year = (this_year - 1)
            last_month_last_day = calendar.monthrange(this_year, last_month)[1]
            last_month = '%s-%s-%s' % (this_year, last_month, last_month_last_day)
            # Uncommnent this for testing
            # last_month = '2017-11-01'
            end_date = datetime.datetime.strptime(last_month, '%Y-%m-%d')
            end_date = datetime.datetime(end_date.year, end_date.month, end_date.day, end_date.hour, end_date.second)

            # monthly computation
            while end_date > current_date_from:
                current_month_last_day = calendar.monthrange(current_date_from.year, current_date_from.month)[1]
                current_date_to = '%s-%s-%s' % (
                    current_date_from.year, current_date_from.month, current_month_last_day)
                current_date_to = datetime.datetime.strptime(current_date_to, '%Y-%m-%d')
                str_current_date_from = str(current_date_from)[0:10] + ' 00:00:00'
                str_current_date_to = str(current_date_to)[0:10] + ' 23:59:59'
                self._create_commission_record(
                    str_current_date_from=str_current_date_from,
                    str_current_date_to=str_current_date_to,
                    external_mechanic=False
                )
                current_date_from = current_date_to
                current_date_from += datetime.timedelta(days=1)

class muti_pos_order(models.Model):
    _inherit = 'pos.order'
    mechanic_sales_id = fields.Many2one(
        comodel_name='muti.commission.record', string='Mechanic', readonly=True
    )


class muti_commission_record(models.Model):
    _name = 'muti.commission.record'
    _order = 'id desc'

    mechanic_id = fields.Many2one(
        comodel_name='muti.mechanic', ondelete='cascade', string='Mechanic',
        index=True, required=True, auto_join=True, readonly=True
    )
    date_from = fields.Date(string='Date from')
    date_to = fields.Date(string='Date to')
    total_sale = fields.Float(string='Total sales', default=0, readonly=True)
    commission = fields.Float(store=True, default=0, string='Service and sales commission')
    percent_commissioned = fields.Integer(string='Percent commissioned')
    sales_ids = fields.One2many(
        comodel_name='pos.order', inverse_name='mechanic_sales_id', string='Sales', readonly=True, index=True,
        compute='_get_sales_ids', store=True
    )
    state = fields.Selection(
        string='Status',
        selection=[('draft', 'Draft'), ('released', 'Released'), ('pending', 'Pending')],
        default='draft'
    )

    @api.depends('date_from', 'date_to', 'mechanic_id')
    def _get_sales_ids(self):
        for r in self:
            sales_ids = self.env['pos.order'].search(
                args=[
                    ('user_id', '=', r.mechanic_id.user_id.id),
                    ('create_date', '>=', r.date_from),
                    ('create_date', '<=', r.date_to)
                ],
                order='create_date desc'
            )
            self.sales_ids = sales_ids

    @api.one
    def release(self):
        return self.write({'state': 'released'})

    @api.one
    def set_draft(self):
        return self.write({'state': 'draft'})
