# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime
from openerp.exceptions import Warning, ValidationError # osv.osv_except replacement
from openerp.tools.translate import _
import re
from dateutil.relativedelta import relativedelta
import psycopg2

class config_payment_terms(models.Model):
    _name = 'config.payment.terms'
    _description = __doc__
    _order = 'term'

    name = fields.Char(string='Term', size=25)
    term=fields.Integer(string='No of Months')
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, values):
        res_id = super(config_payment_terms, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_payment_terms, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids

    @api.onchange('term')
    def onchange_term(self):
        if self.term:
            self.name = str(self.term) + '-month'

    _sql_constraints = [('unique_name', 'UNIQUE(name)', 'A record with the same name already exists.')]


class config_industry(models.Model):
    _name = 'config.industry'
    _description = __doc__

    name = fields.Char(string='Industry', size=64)
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, values):
        res_id = super(config_industry, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_industry, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids

    _sql_constraints = [('unique_name', 'unique(name)', 'A record with the same name already exists.')]


class config_religion(models.Model):
    _name = 'config.religion'
    _description = __doc__

    name = fields.Char(string='Religion', size=64)
    code = fields.Char(string='Codes', size=64)
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, values):
        res_id = super(config_religion, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_religion, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids

    @api.one
    @api.constrains('religion')
    def _check_unique_iname(self):
        existing_ids = self.search([])

        # lists all existing table values excluding blanks and
        # excluding the last record/record currently being entered in the form
        lst = [x.name.lower() for x in self.browse(existing_ids) if x.name and x.id not in ids]

        # compare the new value against the items in the list
        for self_obj in self.browse(existing_ids):
            if self_obj.name and self_obj.name.lower() in lst:
                raise Warning(_('Religion should be unique.'))


class config_rebates(models.Model):
    _name = 'config.rebates'
    _description = __doc__
    name = fields.Date(string='Effectivity Date')
    branch_id = fields.Many2one(comodel_name='config.branch', string='Branch', required=False)
    brandnewamount = fields.Float(string='Brand New', digits=(16, 2))
    repoamount = fields.Float(string='Repo', digits=(16, 2))
    active = fields.Boolean(string='Active', default=True)

    def check_record(self, ids, values, br_id):
        current_id = ids
        if not current_id:
            current_id = [0]
        
        rec_ids = self.search([('id', '!=', current_id[0]), ('branch_id', '=', br_id)])
        active_cnt = 0
        
        # check first the record that will be added
        if values.has_key('active') and values['active']:
            active_cnt += 1
        
        # check the remaining records
        for rec_id in rec_ids:
            rebate_rec=self.read(rec_id, ['active'])
            if rebate_rec['active']:
                active_cnt += 1
        
        if active_cnt > 1:
            raise Warning(_('ERROR 00089: An existing record is already set to active.'))

    @api.model
    def create(self, values):
        self.check_record(0, values, values['branch_id'])
        res_id = super(config_rebates, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        if values.has_key('branch_id'):
            br_id = values['branch_id']
        else:
            for rec in self.browse(cr, uid, ids, context=context):
                br_id = rec.branch_id.id

        self.check_record(ids, values, br_id, context)
        ids = super(config_rebates, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids



class config_collectors(models.Model):
    _name = 'config.collectors'
    _description = __doc__
    _rec_name = 'coll_name'
    name = fields.Many2one(comodel_name='res.users', string='Collector', ondelete='cascade')
    coll_name = fields.Char(related='name.name', string='Collector')
    branch = fields.Many2one(comodel_name='config.branch', string='Branch', required=False)
    barangay_list = fields.One2many(
        comodel_name='config.collectors.barangay', inverse_name='collector_id',
        string='Assigned Barangay', required=False
    )
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, values):
        values['branch'] = self.onchange_collector(values['name'])
        res_id = super(config_collectors, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_collectors, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids

    @api.onchange('coll_name')
    def onchange_collector(self, collector=None):
        if not collector:
            collector = self.name
        
        res = self.env['res.users'].browse(collector)

        cl_branch_id = res['branch_id'].id
        self.branch = cl_branch_id
        return cl_branch_id


class config_collectors_barangay(models.Model):
    _name = 'config.collectors.barangay'
    _description = __doc__

    collector_id = fields.Many2one(comodel_name='config.collectors', string='Collector')
    barangay_id = fields.Many2one(comodel_name='config.barangay', string='Barangay')
    city_id = fields.Many2one(comodel_name='config.city', related='barangay_id.city_id', string='City/Municipality', readonly='True')
    province_id = fields.Many2one(comodel_name='config.province', related='barangay_id.city_id.province_id', string='Province', readonly='True')
    branch_id = fields.Many2one(comodel_name='config.branch', related='collector_id.branch', string='Branch', readonly='True')
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_collectors_barangay, self)._write(cr, uid,  ids, values, context)
        return ids

    @api.onchange('barangay_id')
    def onchange_brgy(self):
        if self.barangay_id:
            res = self.env['config.barangay'].read(self.barangay_id, ['city_id', 'province_id'])
            city = res['city_id'][0]
            prov = res['province_id'][0]
        else:
            city = None
            prov = None

        self.city_id = city
        self.province_id = prov


class config_district(models.Model):
    _name = 'config.district'
    _description = __doc__

    name = fields.Char(string='District Name', size=64)
    code = fields.Char(string='District Code', size=64)
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, values):
        res_id = super(config_district, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_district, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids
    
    _sql_constraints = [('unique_name', 'UNIQUE(name)', 'A record with the same name already exists.')]


class config_brgy_assignment(models.Model):
    _name = 'config.brgy.assignment'
    _description = __doc__
    _rec_name = 'transaction_number'
    _order = 'transaction_date desc'

    def _user_id(self):
        return self.env.user.id

    transaction_number = fields.Char(string='Transaction Number', size=25)
    transaction_date = fields.Datetime('Date', default=datetime.now().strftime('%Y-%m-%d'))
    branch_id = fields.Many2one(comodel_name='config.branch', string='Branch', required=False)
    collector_prev_id = fields.Many2one(comodel_name='config.collectors', string='Previous Collector')
    collector_id = fields.Many2one(comodel_name='config.collectors', string='New Collector')
    encoder = fields.Many2one(comodel_name='res.users', string='Encoder', default=_user_id)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('void', 'Void'),
    ], string='State', default='draft')
    barangay_list = fields.One2many(
        comodel_name='config.brgy.assignment.det', inverse_name='cfa_id', string='Assigned Barangay', required=False)
    remarks = fields.Char(string='Remarks', size=200)
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_brgy_assignment, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids

    @api.model
    def create(self, values):
        with_details = False
        year = datetime.now().strftime('%Y-%m-%d')[:4]
        
        seq_number = self.env['sequence'].get_id('Branch Assignment', values['branch_id'], year)
        values['transaction_number'] = seq_number
        
        if 'collector_id' in values and 'collector_prev_id' in values:
            coll = values['collector_id']
            coll_prev = values['collector_prev_id']
            with_details = True

        res_id = super(config_brgy_assignment, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)

        if with_details:
            brgys = self.env['config.collectors.barangay'].search([('collector_id', '=', coll_prev)])
            for brgy in brgys:
                brg = self.env['config.collectors.barangay'].read(brgy, ['barangay_id'])
                
                self.env['config.brgy.assignment.det'].create({
                    'cfa_id': res_id,
                    'barangay_id': brg['barangay_id'][0],
                    'collector_id': coll_prev,
                })
        
        return res_id

    @api.multi
    def set_confirm(self):
        hdr = self.browse(self.ids)
        new_collector = hdr[0].collector_id.id
        branch_id = hdr[0].branch_id.id
        for det in hdr[0].barangay_list:
            brgy_id = det.barangay_id.id
            prev_collector = det.collector_id
            if prev_collector:
                get_rec = self.env['config.collectors.barangay'].search([
                    ('barangay_id', '=', brgy_id), ('collector_id.branch', '=', branch_id)])
                if get_rec:
                    self.env['config.collectors.barangay'].write(get_rec[0], {'collector_id': new_collector})
            else:
                self.env['config.collectors.barangay'].create({'collector_id': new_collector, 'barangay_id':  brgy_id})
        self.state = 'confirm'

    @api.multi
    def set_draft(self):
        hdr = self.browse(self.ids)
        branch_id = hdr[0].branch_id.id
        for det in hdr[0].barangay_list:
            brgy_id = det.barangay_id.id
            prev_collector = det.collector_id
            if prev_collector:
                get_rec = self.env['config.collectors.barangay'].search([
                    ('barangay_id', '=', brgy_id), ('collector_id.branch', '=', branch_id)])
                if get_rec:
                    self.env['config.collectors.barangay'].write(get_rec[0], {'collector_id': prev_collector.id})
            else:
                get_rec = self.env['config.collectors.barangay'].search([
                    ('barangay_id', '=', brgy_id), ('collector_id.branch', '=', branch_id)])
                if get_rec:
                    self.env['config.collectors.barangay'].unlink(get_rec[0])
        self.state = 'draft'

    @api.multi
    def set_void(self):
        hdr = self.browse(self.ids)
        curr_state = hdr[0].state
        if curr_state == 'confirm':
            branch_id = hdr[0].branch_id.id
            for det in hdr[0].barangay_list:
                brgy_id = det.barangay_id.id
                prev_collector = det.collector_id
                if prev_collector:
                    get_rec = self.env['config.collectors.barangay'].search([
                        ('barangay_id', '=', brgy_id), ('collector_id.branch', '=', branch_id)])
                    if get_rec:
                        self.env['config.collectors.barangay'].write(get_rec[0], {'collector_id':prev_collector.id})
                else:
                    get_rec = self.env['config.collectors.barangay'].search([
                        ('barangay_id', '=', brgy_id), ('collector_id.branch', '=', branch_id)])
                    if get_rec:
                        self.env['config.collectors.barangay'].unlink(get_rec[0])
        self.state = 'void'


class config_brgy_assignment_det(models.Model):
    _name = 'config.brgy.assignment.det'
    _description = __doc__

    cfa_id = fields.Many2one('config.brgy.assignment', 'Barangay Assignment')
    barangay_id = fields.Many2one('config.barangay', 'Barangay')
    city_id = fields.Many2one(comodel_name='config.city', related='barangay_id.city_id', string='City/Municipality', readonly='True')
    province_id = fields.Many2one(comodel_name='config.province', related='barangay_id.city_id.province_id', string='Province', readonly='True')
    collector_id = fields.Many2one(comodel_name='config.collectors', string='Previous Collector')
    branch_id = fields.Many2one(comodel_name='config.branch', related='cfa_id.branch_id', string='Branch', readonly='True')
    new_collector_id = fields.Many2one(comodel_name='config.collectors', related='cfa_id.collector_id', string='New Collector', readonly='True')
    transaction_date = fields.Datetime(related='cfa_id.transaction_date', string='Date', readonly='True')
    active = fields.Boolean(string='Active', default=True)
    state = fields.Selection(related='cfa_id.state', string='State')

    @api.model
    def create(self, values):
        brgy_id = values['barangay_id']
        res_id = super(config_brgy_assignment_det, self).create(values)
        get_br = self.env['config.brgy.assignment.det'].browse(res_id)
        if get_br:
            branch_id = get_br.cfa_id.branch_id.id
            coll_id = self.get_prev_coll(brgy_id, branch_id)
            self._write([res_id], {'collector_id': coll_id})
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        x_info = self.browse(ids[0])
        br_id = x_info.cfa_id.branch_id.id
        if 'barangay_id' in values:
            brgy_id = values['barangay_id']
            values['collector_id'] = self.get_prev_coll(brgy_id,br_id)
        ids = super(config_brgy_assignment_det, self)._write(cr, uid, ids, values, context)
        return ids

    def get_prev_coll(self, brgy_id, branch_id):
        coll_id = None
        coll = self.env['config.collectors.barangay'].search([
            ('barangay_id', '=', brgy_id),
            ('collector_id.branch', '=', branch_id)
        ])
        if coll:
            cl_id = self.env['config.collectors.barangay'].read(coll[0], ['collector_id'])
            coll_id = cl_id['collector_id'][0]
        return coll_id

    @api.onchange('barangay_id', 'branch_id')
    def onchange_brgy(self):
        if self.barangay_id:
            res = self.env['config.barangay'].read(self.barangay_id, ['city_id','province_id'])
            city = res['city_id'][0]
            prov = res['province_id'][0]
        else:
            city = None
            prov = None

        self.city_id = city
        self.province_id = prov
        self.collector_id = self.get_prev_coll(self.barangay_id, self.branch_id)


class config_relationship(models.Model):
    _name = 'config.relationship'
    _description = __doc__

    name = fields.Char(string='Relationship', size=64),
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, values):
        res_id = super(config_relationship, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_relationship, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids

    @api.one
    @api.constrains('relationship')
    def _check_unique_iname(self):
        existing_ids = self.search([])

        # lists all existing table values excluding blanks and
        # excluding the last record/record currently being entered in the form
        lst = [x.name.lower() for x in self.browse(existing_ids) if x.name and x.id not in ids]

        # compare the new value against the items in the list
        for self_obj in self.browse(existing_ids):
            if self_obj.name and self_obj.name.lower() in lst:
                raise Warning(_('Relationship should be unique.'))


class config_municipality(models.Model):
    _name = 'config.municipality'
    _description = __doc__

    name = fields.Char(string='Municipality Name', size=64)
    code = fields.Char(string='Municipality Code', size=64)
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, values):
        res_id = super(config_municipality, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_municipality, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class config_province(models.Model):
    _name = 'config.province'
    _description = __doc__

    def _getlast_code(self):
        for r in self:
            if not r.province_code:
                province_code = '001'
                sql_req= """
                select max(province_code) as last_province_code
                from config_province
                """

                self.env.cr.execute(sql_req)
                sql_res = self.env.cr.dictfetchone()
                if sql_res:
                    if sql_res['last_province_code']:
                        current_prov_code = int(sql_res['last_province_code']) + 1
                        return str(current_prov_code).zfill(3)

    name = fields.Char(string='Province Name', size=64)
    province_code = fields.Char(string='Province Code', size=64, default=_getlast_code)
    old_prov_code = fields.Char(string='Old Province Code', size=20, readonly=True)
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, values):
        values['name'] = values['name'].upper()
        res_id = super(config_province, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        values['name'] = values['name'].upper()
        ids = super(config_province, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids

    _sql_constraints = [('unique_name', 'UNIQUE(name)', 'A record with the same name already exists.')]


class config_city(models.Model):
    _name = 'config.city'
    _description = __doc__

    name = fields.Char(string='City Name', size=64)
    city_code = fields.Char(string='City Code', size=64)
    province_id = fields.Many2one(comodel_name='config.province', string='Province Name')
    old_municipal_code = fields.Char(string='Old Municipal Code', size=20, readonly=True)
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, values):
        values['city_code'] = self.onchange_province_id({}, values['province_id'])
        res_id = super(config_city, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        if values.has_key('province_id'):
            values['city_code'] = self.onchange_province_id(values['province_id'])
        ids = super(config_city, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids

    @api.model
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None):
        if context:
            if 'province' in context:
                prov_id = context['province'][0]
                if not prov_id:
                    raise Warning(_('ERROR 00090: No province selected'))

                args.append(('province_id', '=', prov_id))

        return super(config_city, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)

    @api.one
    @api.constrains('city', 'province')
    def check_unique_city_prov(self,):
        city_prov_list = []
        # Get the record currently being entered
        self_obj = self.read(self.ids)
        
        # List all existing table values excluding blanks and excluding the
        # last record/record currently being entered in the form
        # Search for the City record with the same City (name) and province_id
        res_city = self.search([
            ('active', 'in', ['t','f']),
            ('name', '!=', None),
            ('province_id', '!=', None),
            ('id','!=', self.ids),
            ('province_id', '=', self_obj[0]['province_id'][1]),
            ('name', 'ilike', self_obj[0]['name'])
        ])
        if res_city:
            for city_rec in res_city:
                city_fields = ['id', 'name', 'city_code', 'province_id']
                city = self.read(city_rec, city_fields)
                city_prov = city['name'] + ' ' + city['province_id'][1]
                city_prov = city_prov.lower()
                city_prov_list.append(city_prov)
        
        # compare the new value against the items in the list
        if self_obj:
            self_city_prov = self_obj[0]['name'] + " " + self_obj[0]['province_id'][1]
            if self_city_prov and self_city_prov.lower() in city_prov_list:
                raise Warning(_('A record with the same city and province already exists.'))

    @api.onchange('province_id')
    def onchange_province_id(self, province_id=None):
        if not province_id:
            province_id = self.province_id
        temp_city_code = ''
        city_code_series = '001'
        
        res = self.env['config.province'].browse(province_id)
        cl_province_code = res['province_code']
        
        sql_req= """
        select max(substring(city_code,4,6)) as last_city_code
        from config_city
        where substring(city_code,1,3) =
        """    
        
        sql_req = "%s'%s'" % (sql_req, cl_province_code)

        self.env.cr.execute(sql_req)
        sql_res = self.env.cr.dictfetchone()
        
        if sql_res:
            if sql_res['last_city_code']:
                current_city_code = int(sql_res['last_city_code']) + 1
                temp_city_code = cl_province_code + str(current_city_code).zfill(3)
            else:
                temp_city_code = cl_province_code + city_code_series

        self.city_code = temp_city_code
        return temp_city_code


class config_interest_rate(models.Model):
    _name = 'config.interest.rate'
    _description = __doc__

    name = fields.Date(string='Effectivity Date')
    branch_id = fields.Many2one(comodel_name='config.branch', string='Branch', required=False)
    rate_brandnew = fields.Float(string='Brand New Rate (%)', digits=(16, 2))
    rate_repo = fields.Float(string='Repo Rate (%)', digits=(16, 2))
    active = fields.Boolean(string='Active', default=True)

    def check_record(self, ids, values, branch_id):
        current_id = ids
        if not current_id:
            current_id = [0]
        
        rec_ids = self.search([('id', '!=', current_id[0]), ('branch_id', '=', branch_id)])
        active_cnt = 0
        
        # check first the record that will be added
        if values.has_key('active') and values['active']:
            active_cnt += 1
        
        # check the remaining records
        for rec_id in rec_ids:
            rebate_rec = self.read(rec_id, ['active'])
            if rebate_rec['active']:
                active_cnt += 1
        
        if active_cnt > 1:
            raise Warning(_('ERROR 00092: An existing record is already set to active.'))
        
        # check range of rate, must be between 0.01 and 100
        rate_min_val = 0.01
        rate_max_val = 100

        if (float(values['rate_brandnew']) < rate_min_val ) or (float(values['rate_brandnew']) > rate_max_val):
            raise Warning(_('ERROR 00093: Brand New rate must be between 0.01 to 100'))
        if (float(values['rate_repo']) < rate_min_val ) or (float(values['rate_repo']) > rate_max_val):
            raise Warning(_('ERROR 00094: Repo rate must be between 0.01 to 100'))

        return True

    @api.model
    def create(self, values):
        self.check_record(values, values['branch_id'])
        res_id = super(config_interest_rate, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        if values.has_key('branch_id'):
            br_id = values['branch_id']
        else:
            for rec in self.browse(ids):
                br_id = rec.branch_id.id
        self.check_record(ids, values, br_id, context)
        ids = super(config_interest_rate, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class config_interest_rate_promo(models.Model):
    _name = 'config.interest.rate.promo'
    _rec_name = 'description'
    _order = 'start_date desc'

    description = fields.Char(string='Promo Description')
    is_repo = fields.Boolean(string='Repo Promo?')
    branch_id = fields.Many2one(comodel_name='config.branch', string='Branch', help="Blank means for all branches")
    model_id = fields.Many2one(comodel_name='product.model', string='Model', help="Blank means for all models")
    brand_id = fields.Many2one(comodel_name='product.brand', string='Brand', help="Blank means for all brands")
    rate_brandnew = fields.Integer(string='Brand New Int. Rate')
    rate_repo = fields.Integer(string='Repo Int. Rate')
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    term_from = fields.Integer(string='Term [From]', required=True)
    term_to = fields.Integer(string='Term [To]', required=True)
    rebate_brandnew = fields.Float(string='Rebate [Brand New]', digits=(16, 2))
    rebate_repo = fields.Float(string='Rebate [Repo]', digits=(16, 2))
    finance_cost = fields.Float(string='Finance Cost >= to', digits=(16, 2), required=True)
    priority = fields.Integer(compute='_get_priority', string='Priority')
    active = fields.Boolean(string='Active', default=True)
    engine_ids = fields.One2many(comodel_name='config.interest.rate.promo.engine', inverse_name='promo_id', string='Engines')
    promo_for = fields.Selection([
        ('ALL', 'MC and CAB'),
        ('MC', 'MC Only'),
        ('CAB', 'CAB Only'),
    ], string='Promo For', default='ALL')

    @api.model
    def create(self, values):
        res_id = super(config_interest_rate_promo, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_interest_rate_promo, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids

    @api.depends('branch_id', 'brand_id', 'model_id')
    def _get_priority(self):
        for r in self:
            r.priority = None
            if not r['branch_id'] and not r['brand_id'] and not r['model_id']:
                r.priority = 6
            if not r['branch_id'] and r['brand_id'] and not r['model_id']:
                r.priority = 5
            if not r['branch_id'] and r['brand_id'] and r['model_id']:
                r.priority = 4
            if r['branch_id'] and not r['brand_id'] and not r['model_id']:
                r.priority = 3
            if r['branch_id'] and r['brand_id'] and not r['model_id']:
                r.priority = 2
            if r['branch_id'] and r['brand_id'] and r['model_id']:
                r.priority = 1


class config_interest_rate_promo_engine(models.Model):
    _name = 'config.interest.rate.promo.engine'
    _description = __doc__

    promo_id = fields.Many2one(comodel_name='config.interest.rate.promo', string='Promo', required=True)
    product_id = fields.Many2one(comodel_name='product.template', string='Product', required=True)
    engineno = fields.Char(related='product_id.engineno', string='Engine No.')
    chassisno = fields.Char(related='product_id.chassisno', string='Chassis No.')
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, values):
        res_id = super(config_interest_rate_promo_engine, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_interest_rate_promo_engine, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = self.env['product.template'].browse(self.product_id)
        self.engineno = res['engineno']
        self.chassisno = res['chassisno']


class config_education(models.Model):
    _name = 'config.education'
    _description = __doc__

    name = fields.Char(string='Educational Attainment', size=64)
    code = fields.Char(string='Education Code', size=64)
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, values):
        res_id = super(config_education, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_education, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids

    @api.one
    @api.constrains('education')
    def _check_unique_iname(self):
        # @comment checks the uniqueness (case insensitive) of name being entered
        #         gets all existing ids from the database table,
        # @return boolean True or False

        existing_ids = self.search([])
        # lists all existing table values excluding blanks and excluding the last record/record currently being entered
        # in the form
        lst = [x.name.lower() for x in self.browse(existing_ids) if x.name and x.id not in self.ids]

        # compare the new value against the items in the list
        for self_obj in self:
            if self_obj.name and self_obj.name.lower() in lst:
                raise Warning(_('Education should be unique.'))


class config_tribe(models.Model):
    _name = 'config.tribe'
    _description = __doc__

    name = fields.Char(string='Tribe Name', size=64)
    code = fields.Char(string='Tribe Code', size=64)
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, values):
        res_id = super(config_tribe, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_tribe, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids

    @api.one
    @api.constrains('tribe')
    def _check_unique_iname(self):
        # @comment checks the uniqueness (case insensitive) of name being entered
        #         gets all existing ids from the database table,
        # @return boolean True or False

        existing_ids = self.search([])
        # lists all existing table values excluding blanks and excluding the last record/record currently being entered
        # in the form
        lst = [x.name.lower() for x in self.browse(existing_ids) if x.name and x.id not in self.ids]

        # compare the new value against the items in the list
        for self_obj in self:
            if self_obj.name and self_obj.name.lower() in lst:
                raise Warning(_('Error: Tribe should be unique.'))


class config_processing_fee(models.Model):
    _name = 'config.processing.fee'
    _description = __doc__

    date_of_effectivity = fields.Date(string='Effectivity Date')
    branch_id = fields.Many2one(comodel_name='config.branch', string='Branch', required=True)
    particular = fields.Selection(selection=[
        ('preterm','Pre-Termination'),
        ('changeterm','Change Term')
    ], string='Particulars')
    range_from = fields.Integer(string='Range From (mos)')
    range_to = fields.Integer(string='Range To (mos)')
    amount = fields.Float(string='Amount')
    active = fields.Boolean(string='Is Active', default=True)

    @api.model
    def create(self, values):
        res_id = super(config_processing_fee, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_processing_fee, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids

    @api.one
    @api.constrains('processing_fee')
    def _check_range_overlap(self):
        # @comment validation for month range 2 - Check Ovelapping Ranges
        # @return boolean True or False

        for r in self:

            if r.range_from > r.range_to:
                return Warning(_('Error: Range From is greater than Range To.'))
            else:
                # Algorithm to check overlapping ranges/mos:
                # (StartMonth1 <= EndMonth2) and (StartMonth2 <= EndMonth1)
                start_month = r.range_from
                end_month = r.range_to
                br_id = r.branch_id.id
                res = self.env['config.processing.fee'].search([
                    ('range_from', '<=', end_month),
                    ('range_to', '>=', start_month),
                    ('active', '=', True),
                    ('branch_id', '=', br_id)
                ])

                if len(res) > 1:
                    return Warning(_('Range From and Range To(Start and End Months) should not overlap with Existing'))

        return True


class config_payment_type(models.Model):
    _name = 'config.payment.type'
    _description = __doc__
    _rec_name = 'description'

    description = fields.Char(string='Description')
    account_code = fields.Many2one(comodel_name='account.account', string='Account Code')
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, values):
        res_id = super(config_payment_type, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_payment_type, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids

    @api.one
    @api.constrains('payment_type')
    def _check_unique_idescription(self):
        # @comment Function that checks the uniqueness (case insensitive) of description being entered.
        #         gets all existing ids from the database table,
        # @return boolean True or False
        existing_ids = self.search([])

        # list all existing descriptions excluding blanks and the last record/record currently being entered in the form
        lst = [x.description.lower() for x in self.browse(existing_ids) if x.description and x.id not in self.ids]
        
        # compare the new value against the items in the list"
        for r in self:
            if r.description and r.description.lower() in lst:
                raise Warning(_('Description should be unique.'))

        return True


class config_surcharge_rate(models.Model):
    _name = 'config.surcharge.rate'
    _description = __doc__

    effectivity_date = fields.Date(string='Effectivity Date')
    branch_id = fields.Many2one(comodel_name='config.branch', string='Branch', required=True)
    surcharge_rate = fields.Float(string='Surcharge Rate', digits=(16, 2))
    active = fields.Boolean(string='Active', default=True)

    def check_record(self, ids, values, branch_id):
        current_id = ids
        if not current_id:
            current_id = [0]
        
        rec_ids = self.search([('id', '!=', current_id[0]), ('branch_id', '=', branch_id)])
        active_cnt = 0
        
        # check first the record that will be added
        if values.has_key('active') and values['active']:
            active_cnt += 1
        
        # check the remaining records
        for rec_id in rec_ids:
            rebate_rec=self.read(rec_id, ['active'])
            if rebate_rec['active']:
                active_cnt += 1
        
        if active_cnt > 1:
            raise Warning('ERROR 00095: An existing record is already set to active.')

        return True

    @api.model
    def create(self, values):
        self.check_record(values, values, values['branch_id'])
        res_id = super(config_surcharge_rate, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        if values.has_key('branch_id'):
            br_id = values['branch_id']
        else:
            for rec in self.browse(ids):
                br_id = rec.branch_id.id

        self.check_record(ids, values, br_id)
        ids = super(config_surcharge_rate, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids

    @api.one
    @api.constrains('surcharge_rate')
    def _check_isurcharge_rate(self):
        # @comment Function that checks if encoded surcharge rate is valid (between 1-100)
        # @return boolean True or False
        for r in self:
            # check if encoded surcharge rate is between 1-100
            surcharge_rate = r.surcharge_rate
            if surcharge_rate < 1 or surcharge_rate > 100:
                raise Warning(_('Surcharge Rate should be between 1-100.'))


class config_maturity_surcharge_rate(models.Model):
    _name = 'config.maturity.surcharge.rate'
    _description = __doc__

    effectivity_date = fields.Date(string='Effectivity Date')
    branch_id = fields.Many2one(comodel_name='config.branch', string='Branch', required=True)
    maturity_surcharge_rate = fields.Float(string='Maturity Surcharge Rate', digits=(16, 2))
    active = fields.Boolean(string='Active', default=True)

    def check_record(self, ids, values, branch_id):
        current_id = ids
        if not current_id:
            current_id = [0]
        
        rec_ids = self.search([('id', '!=', current_id[0]), ('branch_id', '=', branch_id)])
        active_cnt = 0
        
        # check first the record that will be added
        if values.has_key('active') and values['active']:
            active_cnt += 1
        
        # check the remaining records
        for rec_id in rec_ids:
            rebate_rec = self.read(rec_id, ['active'])
            if rebate_rec['active']:
                active_cnt += 1
        
        if active_cnt > 1:
            raise Warning(_('ERROR 00096: An existing record is already set to active.'))

    @api.model
    def create(self, values):
        self.check_record(values, values, values['branch_id'])
        res_id = super(config_maturity_surcharge_rate, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        if values.has_key('branch_id'):
            br_id = values['branch_id']
        else:
            for rec in self.browse(ids):
                br_id = rec.branch_id.id

        self.check_record(ids, values, br_id)
        ids = super(config_maturity_surcharge_rate, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids

    @api.one
    @api.constrains('surcharge_rate')
    def _check_isurcharge_rate(self):
        # @comment Function that checks if encoded surcharge rate is valid (between 1-100)
        # @return boolean True or False
        #
        for r in self:
            # check if encoded surcharge rate is between 1-100
            maturity_surcharge_rate = r.maturity_surcharge_rate
            if maturity_surcharge_rate < 1 or maturity_surcharge_rate > 100:
                raise Warning(_('Maturity Surcharge Rate should be between 1-100.'))


class config_grace_period(models.Model):
    _name = 'config.grace.period'
    _description = __doc__

    effectivity_date = fields.Date(string='Effectivity Date')
    grace_period = fields.Integer(string='Grace Period')
    active = fields.Boolean(string='Active', default=True)
    
    def check_record(self, ids, values):
        current_id = ids
        if not current_id:
            current_id = [0]
        
        rec_ids = self.search([('id', '!=', current_id[0])])
        active_cnt = 0
        
        # check first the record that will be added
        if values.has_key('active') and values['active']:
            active_cnt += 1
        
        # check the remaining records
        for rec_id in rec_ids:
            rebate_rec=self.read(rec_id,['active'])
            if rebate_rec['active']:
                active_cnt += 1
        
        if active_cnt > 1:
            raise Warning(_('ERROR 00097: An existing record is already set to active.'))
        
        return True

    @api.model
    def create(self, values):
        self.check_record(0, values)
        res_id = super(config_grace_period, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        self.check_record(ids, values)
        ids = super(config_grace_period, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class config_financing_duedate(models.Model):
    _name = 'config.financing.duedate'
    _description = __doc__

    forward_duedate = fields.Boolean(
            string='Loan Release that fall from 26th to 31st of the month, forward to 1st day of succeeding month?',
            required=False
    )

    # TODO : import time required to get currect date
    effectivity_date = fields.Date(string='Date of Effectivity')
    active = fields.Boolean('Active', default=True)

    @api.model
    def create(self, values):
        res_id = super(config_financing_duedate, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_financing_duedate, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class config_default_payment_timing(models.Model):
    _name = 'config.default.payment.timing'
    _description = __doc__

    first_notice_updated = fields.Integer(
        string='Number of days to generate 2nd Notice after receipt', required=False)
    first_notice_not_updated = fields.Integer(
        string='Number of days to generate 2nd Notice if FN not updated', required=False)
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, values):
        res_id = super(config_default_payment_timing, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_default_payment_timing, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class config_document_number_format(models.Model):
    _inherit = 'config.document.number.format'

    @api.model
    def create(self, values):
        res_id = super(config_document_number_format, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_document_number_format, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class config_mc_registration_allocation(models.Model):
    _name = 'config.mc.registration.allocation'
    _description = __doc__

    active = fields.Boolean(string='Active', default=True)
    branch_id = fields.Many2one(comodel_name='config.branch', string='Branch', required=True)
    release_1st = fields.Float(string='1st Release (per unit)', digits=(16, 2))
    release_2nd = fields.Float(string='2nd Release (per unit)', digits=(16, 2))
    release_3rd = fields.Float(string='3rd Release (per unit)', digits=(16, 2))

    @api.model
    def create(self, values):
        res_id = super(config_mc_registration_allocation, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_mc_registration_allocation, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class config_sched_logs(models.Model):
    _name = 'config.sched.logs'
    _description = __doc__

    message = fields.Text(string='Message')
    process = fields.Char(string='Scheduled Process', size=100)
    datetime = fields.Datetime(string='Date/Time', default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    process_date = fields.Date(string='Process Date')


class config_denomination(models.Model):
    _name = 'config.denomination'
    _order = 'denomination desc'
    _description = __doc__

    active = fields.Boolean('Active', default=True)
    denomination = fields.Float(string='Denomination', digits=(16, 2))

    @api.model
    def create(self, values):
        res_id = super(config_denomination, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_denomination, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids



class stock_location(models.Model):
    _inherit = 'stock.location'

    branch_id = fields.Many2one(comodel_name='config.branch', string='Branch Assignment', ondelete="cascade")


class config_reports_limit(models.Model):
    _name = 'config.reports.limit'
    _description = __doc__

    object_id = fields.Many2one(comodel_name='ir.model', string='Object Name', required=True)
    print_cntr = fields.Integer(string='Print Limit', required=True)
    records = fields.One2many(comodel_name='config.reports.limit.records', inverse_name='limit_id', string='Labels')
    active = fields.Boolean(string='Active', default=True)


class config_reports_limit_records(models.Model):
    _name = 'config.reports.limit.records'
    _description = __doc__
    
    record_id = fields.Integer(string='Record No.')
    rec_print_cnt = fields.Integer(string='Number of Prints')
    limit_id = fields.Many2one(comodel_name='config.reports.limit', string='Report Limit')
    active = fields.Boolean(string='Active', default=True)


class apv_emails(models.Model):
    _name = 'apv.emails'
    _description = __doc__

    email_to = fields.Char(string='Recipient', size=200)
    email_msg = fields.Text (string='Message')
    
    def send_apv_emails(self, cr, uid, context={}):
        rec_ids = self.search([])
        if rec_ids:
            # for id in rec_ids:
            #     rec_details = self.read(cr, uid, id, ['email_to', 'email_msg'])
            #     send_email('EPFC OpenERP',
            #         [str(rec_details['email_to'])],
            #         'Journal Voucher of APV from Other Branch/Home Office',
            #         rec_details['email_msg'],
            #         )
            #
            self.env.cr.execute('delete from apv_emails where id in %s', (tuple(rec_ids),))