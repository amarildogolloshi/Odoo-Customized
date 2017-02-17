# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime
from openerp.exceptions import Warning, ValidationError # osv.osv_except replacement
from openerp.tools.translate import _
import re
from dateutil.relativedelta import relativedelta
import psycopg2


class loan_db_config(models.Model):
    _name = 'loan.db.config'
    _description = __doc__

    db_name = fields.Char(string='Database Name', help="Name of the EPFC Loan database", size=50),
    username = fields.Char(string='Username', help="The authorized user to connect to the Postgresql database", size=50),
    password = fields.Char(string='Password', help="Password for the given user", size=50),
    db_address = fields.Char(string='Host', help="Server IPv4 IP where Posgresql server with EPFC Loan database is running", size=50),
    db_port = fields.Integer(string='Database Port', help="Postgresql server port"),
    enable = fields.Boolean(string="Enable", help="Set if this connection record will be used as default", default=True)

    def _check_ip_add(self, ip_add):
        if not (ip_add.count('.') == 3 and  all(0 <= int(num) < 256 for num in ip_add.rstrip().split('.'))):
            raise Warning(_("Invalid IPv4 IP address format!"))

    @api.model
    def create(self, values):
        # check ip address format
        if 'db_address' in values and values['db_address']:
            self._check_ip_add(values['db_address'])

        if 'enable' in values and values['enable']:
            # check other record that is in active state
            rec_id = self.env['loan.db.config'].search([('enable','=','t')])
            if rec_id:
                self.cr.env.execute("update loan_db_config set enable=\'False\' where id = %s", rec_id)

        res_id = super(loan_db_config, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        # check ip address format
        if 'db_address' in values and values['db_address']:
            self._check_ip_add(values['db_address'])

        if 'enable' in values and values['enable']:
            # check other record that is in active state
            rec_id = self.env['loan.db.config'].search([('enable', '=', 't')])
            if rec_id:
                self.env.cr.execute("update loan_db_config set enable=\'False\' where id = %s", rec_id)

        ids = super(loan_db_config, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids

    def test_epfc_connection(self, cr, uid):
        res = self.search(cr, uid, [('enable', '=', 't')])
        if not res:
            raise Warning(_('No active EPFC database connection was found. Please \
                configured it under Administration->Configuration->Database Configuration.'))

        db_config = self.read(res[0], ['db_name', 'db_address', 'db_port', 'username', 'password'])

        conn_string = "dbname='%s' user='%s' password='%s' host='%s'" % (db_config['db_name'],
                                        db_config['username'], db_config['password'],
                                        db_config['db_address'])

        try:
            epfc_conn = psycopg2.connect (conn_string)
        except:
            raise Warning(_('Cannot connect to EPFC database. Please check your settings.'))

        raise Warning(_('Connection to EPFC database successful.'))


class config_license_restriction(models.Model):
    _name = 'config.license.restriction'
    _description = __doc__

    restriction_code = fields.Integer(string='Restriction Code')
    name = fields.Char(string='Description', size=50)
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, values):
        res_id = super(config_license_restriction, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_license_restriction, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class config_license_type(models.Model):
    _name = 'config.license.type'
    _description = __doc__

    type_code = fields.Integer(string='Type Code')
    name = fields.Char(string='Description', size=50)
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, values):
        res_id = super(config_license_type, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_license_type, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class config_province(models.Model):
    _name = 'config.province'
    _description = __doc__

    name = fields.Char(string='Province Name', size=64),
    province_code = fields.Char(string='Province Code', size=64, default=lambda self: self._get_last_code())
    old_prov_code = fields.Char(string='Old Province Code', size=20, readonly=True)
    active = fields.Boolean('Active', default=True)

    @api.model
    def create(self, values):
        values['name'] = values['name'].upper()
        res_id = super(config_province, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        if 'name' in values:
            values['name'] = values['name'].upper()
        ids = super(config_province, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids

    def _get_last_code(self):
        province_code = "001"

        sql_req= "select max(province_code) as last_province_code from config_province"
        self.env.cr.execute(sql_req)
        sql_res = self.env.cr.dictfetchone()

        if 'last_province_code' in sql_res and sql_res['last_province_code']:
            current_prov_code = int(sql_res['last_province_code']) + 1
            province_code = str(current_prov_code).zfill(3)
        return province_code

    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'A record with the same name already exists.')
    ]


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
        values['city_code'] = self._onchange_province_id(values['province_id'])
        res_id = super(config_city, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        if 'province_id' in values and values['province_id']:
            values['city_code'] = self._onchange_province_id(values['province_id'])
        ids = super(config_city, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids

    @api.model
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context={}, count=False, access_rights_uid=None):
        if context:
            if 'province' in context:
                prov_id = context['province'][0]
                if not prov_id:
                    raise Warning(_('ERROR 00090: No province selected'))

                args.append(('province_id', '=', prov_id))

        return super(config_city, self).search(cr, uid, args, offset=offset, limit=limit, order=order,
        context=context, count=count)

    @api.one
    @api.constrains('province', 'city')
    def _check_unique_brgy_city(self):
        # @comment checks the uniqueness (case insensitive) of city (name) and province being entered
        #         gets all existing similar records from the database table
        # @return boolean True or False
        ids = self.ids
        city_prov_list = []
        self_obj = self.read(ids)

        # List all existing table values excluding blanks and excluding the last record/record currently
        # being entered in the form
        # Search for the City record with the same City (name) and province_id
        res_city = self.search([
            ('active', 'in', ['t', 'f']),
            ('name', '!=', None),
            ('province_id', '!=', None),
            ('id', '!=', ids),
            ('province_id', '=', self_obj[0]['province_id'][1]),
            ('name', 'ilike', self_obj[0]['name']),
        ])
        if res_city:
            for city_rec in res_city:
                city_fields = ['id', 'name', 'city_code', 'province_id']
                city = self.read(city_rec, city_fields)
                city_prov = city['name'] + " " + city['province_id'][1]
                city_prov = city_prov.lower()
                city_prov_list.append(city_prov)

        # compare the new value against the items in the list
        if self_obj:
            self_city_prov = self_obj[0]['name'] + " " + self_obj[0]['province_id'][1]
            # compare the new value against the items in the list
            if (self_city_prov and self_city_prov.lower() in city_prov_list):
                raise ValidationError('Error: A record with the same city and province already exists.')

    @api.onchange('province_id')
    def _onchange_province_id(self, province_id=None):
        if not province_id:
            province_id = self.province_id
        temp_city_code = ''
        city_code_series = '001'

        res = self.env['config.province'].browse(province_id)
        cl_province_code = res['province_code']

        sql_req = """
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


class config_barangay(models.Model):
    _name = 'config.barangay'
    _description = __doc__

    name = fields.Char(string='Barangay Name', size=64)
    barangay_name = fields.Many2one(comodel_name='config.collectors', string='Barangay Name', ondelete="cascade")
    brgy_code = fields.Char(string='Barangay Code', size=64)
    city_id = fields.Many2one(comodel_name='config.city', string='City/Municipality')
    province_id = fields.Many2one(
        comodel_name='config.province', related='city_id.province_id', string='Province', required=False
    )
    old_brgy_code = fields.Char(string='Old Barangay Code', size=20, readonly=True)
    active = fields.Boolean(string='Active', default=True)
    zip_code = fields.Char(string='Zip Code', size=4)

    @api.model
    def create(self, values):
        if 'city_id' not in values or not values['city_id']:
            raise Warning(_('Please select a city for the specified barangay name.'))
        values['brgy_code'] = self._onchange_city_id(values['city_id'])
        res_id = super(config_barangay, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        if 'city_id' in values and values['city_id']:
            values['brgy_code'] = self._onchange_city_id(values['city_id'])
        ids = super(config_barangay, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids

    @api.model
    def search(
            self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None):
        if context:
            if 'city' in context:
                city_id = context['city'][0]
                if not city_id:
                    raise Warning(_('ERROR 00091: No municipality/city selected'))
                args.append(('city_id', '=', city_id))

        return super(config_barangay, self).search(
            args, offset=offset, limit=limit, order=order, context=context, count=count
        )

    @api.model
    def _search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None):
        if context:
            if 'forcity' in context:
                city = context['forcity'][0]
                args.append(('city_id', '=', city))

        return super(config_barangay, self)._search(
            args, offset=offset, limit=limit, order=order, context=context,
            count=count, access_rights_uid=access_rights_uid
        )

    @api.onchange('city_id')
    def _onchange_city_id(self, city_id=None):
        if not city_id:
            city_id = self.city_id
        temp_brgy_code = ''
        brgy_code_series = '001'

        res = self.env['config.city'].browse(city_id)
        cl_city_code = res['city_code']

        sql_req = """
            select max(substring(brgy_code,7,9)) as last_brgy_code
            from config_barangay
            where substring(brgy_code,1,6) =
        """

        sql_req = "%s'%s'" % (sql_req, cl_city_code)

        self.env.cr.execute(sql_req)
        sql_res = self.env.cr.dictfetchone()

        if sql_res:
            if sql_res['last_brgy_code']:
                current_brgy_code = int(sql_res['last_brgy_code']) + 1
                temp_brgy_code = cl_city_code + str(current_brgy_code).zfill(3)
            else:
                temp_brgy_code = cl_city_code + brgy_code_series

        self.brgy_code = temp_brgy_code
        return temp_brgy_code

    @api.one
    @api.constrains('barangay', 'city')
    def _check_unique_brgy_city(self):

        # @comment checks the uniqueness (case insensitive) of barangay (name) and city_id being entered
        #         gets all existing similar records from the database table
        # @return boolean True or False

        ids = self.ids
        brgy_city_list = []

        # Get the record currently being entered
        self_obj = self.read(ids)

        # List all existing table values excluding blanks and excluding the last record
        # Search for the City record with the same City (name) and province_id
        res_brgy = self.search([
            ('active', 'in', ['t', 'f']),
            ('name', '!=', None),
            ('city_id', '!=', None),
            ('id', '!=', ids),
            ('city_id', '=', self_obj[0]['city_id'][1]),
            ('name', 'ilike', self_obj[0]['name']),
        ])

        if res_brgy:
            for brgy_rec in res_brgy:
                brgy_fields = ['id', 'name', 'brgy_code', 'city_id']
                brgy = self.read(brgy_rec, brgy_fields)
                brgy_city = brgy['name'] + " " + brgy['city_id'][1]
                brgy_city = brgy_city.lower()
                brgy_city_list.append(brgy_city)

        # compare the new value against the items in the list
        if self_obj:
            self_brgy_city = self_obj[0]['name'] + " " + self_obj[0]['city_id'][1]
            # compare the new value against the items in the list
            if (self_brgy_city and self_brgy_city.lower() in brgy_city_list):
                raise ValidationError('Error: A record with the same barangay and city already exists')


class config_claim_type(models.Model):
    _name = 'config.claim.type'
    _description = __doc__

    name = fields.Char(string='Name', size=64)
    claim_type_code = fields.Char(string='Claim Code', size=64)
    old_claim_type_code = fields.Char(string='Old Claim Code', size=64)
    insurance_type_id = fields.Many2one(comodel_name='product.category', string='Coverage')
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, values):
        values['claim_type_code'] = self.env['ir.sequence'].get('claim.type.seq')
        res_id = super(config_claim_type, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_claim_type, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class config_insurance_type(models.Model):
    _name = 'config.insurance.type'
    _description = __doc__

    name = fields.Char(string='Insurance Type', size=64)
    active = fields.Boolean(string='Active', default=True)
    insurance_type_code = fields.Char(string='Type Code', size=64)

    @api.model
    def create(self, values):
        res_id = super(config_insurance_type, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_insurance_type, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class config_sub_agent(models.Model):

    _name = 'config.sub.agent'
    _description = __doc__
    _rec_name = 'sub_agent_name'
    _order = 'sub_agent_name'

    namerec = fields.Char(compute='_get_subagent_name_code')
    sub_agent_code = fields.Char(string='Sub-Agent Code', size=64)
    sub_agent_name = fields.Char(string='Sub-Agent Name', size=64)
    address = fields.Char(string='Sub-Agent Address', size=250)
    telno = fields.Char(string='Sub-Agent Tel. No.', size=64)
    mailing_list = fields.Char(string='Mailing List', size=64)
    manager = fields.Many2one(comodel_name='res.users', string='Manager', ondelete='cascade'),
    old_sub_agent_code = fields.Char(string='Old Sub-Agent Code', size=20, readonly=True)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner ID [Dealer]')
    partner_id2 = fields.Many2one(comodel_name='res.partner', string='Partner ID [Financing]')
    active = fields.Boolean(string='Active', default=True)
    main_office = fields.Boolean(string='Main Office?')
    area = fields.Char(string='Area', size=64)
    # for MC Policy Service Unit
    city_id = fields.Many2one(comodel_name='config.city', string='Sub-Agent City')

    _sql_constraints = [('unique_name', 'UNIQUE(sub_agent_name)', 'A record with the same name already exists.')]

    def _check_email_format(self, mailing_list):
        result = {}
        compiled_regex = re.compile("(^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$)")
        if mailing_list:
            matched = compiled_regex.match(mailing_list)
            if matched:
                return result
            else:
                raise Warning(_('Please correct the format of the email address (it must be name@domain.com)'))

    @api.model
    def create(self, values):
        if 'mailing_list' in values:
            self._check_email_format(values['mailing_list'])
        values['sub_agent_code'] = self.env['ir.sequence'].get('subagent.seq')
        res_id = super(config_sub_agent, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        if 'mailing_list' in values:
            self._check_email_format(values['mailing_list'])
        ids = super(config_sub_agent, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids

    @api.depends('sub_agent_name', 'sub_agent_code')
    def _get_subagent_name_code(self):
        for r in self:
            r.namerec = r.sub_agent_code + " - " + r.sub_agent_name


class config_rebate(models.Model):
    _name = 'config.rebate'
    _description = __doc__

    name = fields.Char(compute='_get_name', string='Name')
    active = fields.Boolean(string='Active')
    product_category_id = fields.Many2one(comodel_name='product.category', string='Insurance Type')
    insured_product_type_id = fields.Many2one(comodel_name='config.insured.product.type', string='Insurance Product Type')
    valid_from = fields.Date(string='Valid From')
    valid_to = fields.Date(string='Valid To')
    amount = fields.Float(string='Amount', digits=(16, 2))

    @api.depends('product_category_id', 'insured_product_type', 'valid_from', 'valid_to', 'amount')
    def _get_name(self):
        for r in self:
            if 'product_category_id' in r and 'insured_product_type' in r and 'valid_from' in r and 'valid_to' in r:
                r.name = r['product_category_id'][1] + ' ' + \
                                    r['insured_product_type'][1] + ' (' + \
                                    r['valid_from'] + ' to ' + \
                                    r['valid_to'] + ') ' + \
                                    str(r['amount'])
            else:
                r.name = str(r['amount'])

    def _check_validity_period(self, values):
        if 'valid_from' in values:
            sql_stmt = """SELECT id
                        FROM config_rebate
                        WHERE active = True AND
                            product_category_id = %s AND
                            insured_product_type_id = %s AND
                            (valid_from <= TO_DATE('%s', 'YYYY-MM-DD') AND
                            valid_to is NULL) OR
                            (valid_from <= TO_DATE('%s', 'YYYY-MM-DD') AND
                            valid_to >= TO_DATE('%s', 'YYYY-MM-DD'))
                        """ % (
                values['product_category_id'], values['insured_product_type_id'],
                values['valid_from'], values['valid_from'], values['valid_from']
            )
            print sql_stmt
            self.env.cr.execute(sql_stmt)

            if self.env.cr.fetchall():
                raise Warning(_('ERROR 000103: New validity period should be later then the current active rebate.'))
        return True

    @api.model
    def create(self, values):
        res_id = super(config_rebate, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        self._check_validity_period(values)
        ids = super(config_rebate, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class config_mri_max_coverage(models.Model):
    _name = 'config.mri.max.coverage'
    _description = __doc__

    _rec_name = 'amount'
    active = fields.Boolean(string='Active', default=True)
    valid_from = fields.Date(string='Valid From')
    valid_to = fields.Date(string='Valid To')
    amount = fields.Float(string='Amount', digits=(16, 2))

    @api.model
    def create(self, values):
        active_ids = self.search([('active', '=', True)])
        if active_ids:
            if values and 'valid_from' in values and values['valid_from']:
                prev_valid_to = \
                    (datetime.strptime(values['valid_from'], '%Y-%m-%d') - relativedelta(days=1)).strftime('%Y-%m-%d')
                self._write(active_ids, {'active': False, 'valid_to': prev_valid_to})
        res_id = super(config_mri_max_coverage, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_mri_max_coverage, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class config_remittance_rate(models.Model):
    _name = 'config.remittance.rate'
    _description = __doc__

    _rec_name = 'amount'
    categ_id = fields.Many2one(comodel_name='product.category', string='Insurance Type')
    active = fields.Boolean(string='Active', default=True)
    valid_from = fields.Date(string='Valid From')
    valid_to = fields.Date(string='Valid To')
    remittance_rate = fields.Float(string='Remittance Rate - New [%]', digits=(16, 2))
    remittance_rate_renewal = fields.Float(string='Remittance Rate - Renewal [%]', digits=(16, 2))
    remittance_discount = fields.Float(string='Remittance Discount [%]', digits=(16, 2))

    def _check_validity_period(self, values):
        if 'valid_from' in values:
            active_ids = self.search([
                ('active', '=', True),
                ('valid_from', '>', values['valid_from'])
            ])
            if active_ids:
                raise Warning(_('ERROR 000103: New validity period should be later then the current active rebate.'))
        return True

    @api.model
    def create(self, values):
        self._check_validity_period(values)
        active_ids = self.search([('active', '=', True)])
        if active_ids:
            if values and 'valid_from' in values and values['valid_from']:
                prev_valid_to = \
                    (datetime.strptime(values['valid_from'], '%Y-%m-%d') - relativedelta(days=1)).strftime('%Y-%m-%d')
                self._write(active_ids, {'active': False, 'valid_to': prev_valid_to})

        res_id = super(config_remittance_rate, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        self._check_validity_period(values)
        ids = super(config_remittance_rate, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class config_authentication_fee(models.Model):
    _name = 'config.authentication.fee'
    _description = __doc__

    name = fields.Char(compute='_get_name', string='Name')
    active = fields.Boolean(string='Active', default=True)
    valid_from = fields.Date('Valid From')
    valid_to = fields.Date('Valid To')
    amount = fields.Float(string='Amount', digits=(16, 2))

    @api.depends('product_category_id', 'insured_product_type', 'valid_from', 'valid_to', 'amount')
    def _get_name(self):
        for r in self:
            if 'product_category_id' in r and \
                'insured_product_type' in r and \
                'valid_from' in r and \
                'valid_to' in r:
                r.name = r['product_category_id'][1] + ' ' + r['insured_product_type'][1] + \
                         ' (' + r['valid_from'] + ' to ' + r['valid_to'] + ') ' + str(r[''])
            else:
                r.name = str(r['amount'])

    def _check_validity_period(self, values):
        if 'valid_from' in values:
            sql_stmt = """
                SELECT id
                FROM config_authentication_fee
                WHERE active = True AND
                    (valid_from <= TO_DATE('%s', 'YYYY-MM-DD') AND
                    valid_to is NULL) OR
                    (valid_from <= TO_DATE('%s', 'YYYY-MM-DD') AND
                    valid_to >= TO_DATE('%s', 'YYYY-MM-DD'))
                """ % (values['valid_from'], values['valid_from'], values['valid_from'])
            self.env.cr.execute(sql_stmt)

            if self.env.cr.fetchall():
                raise Warning(_('ERROR 000103: New validity period should be later then the current active authentication fee.'))
        return True

    @api.model
    def create(self, values):
        self._check_validity_period(values)
        active_ids = self.search([('active', '=', True)])
        if active_ids:
            if values and 'valid_from' in values and values['valid_from']:
                prev_valid_to = \
                    (datetime.strptime(values['valid_from'], '%Y-%m-%d') - relativedelta(days=1)).strftime('%Y-%m-%d')
                self._write(active_ids, {'active': False, 'valid_to': prev_valid_to})
        res_id = super(config_authentication_fee, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        self._check_validity_period(values)
        ids = super(config_authentication_fee, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class config_endorsement_info(models.Model):
    _name = 'config.endorsement.info'
    _description = __doc__
    _rec_name = 'type'

    old_endorsement_code = fields.Char(string='Old Code', size=64)
    endorsement_code = fields.Char(string='Code', size=64)
    type = fields.Char(string='Endorsement Type', size=64)
    description = fields.Text(string='Description')
    field = fields.Many2one(comodel_name='ir.model.fields', string='Field')

    @api.model
    def create(self, values):
        values['endorsement_code'] = self.env['ir.sequence'].get('endorsement.info.seq')
        res_id = super(config_endorsement_info, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id


class config_yearly_coverage(models.Model):
    _name = 'config.yearly.coverage'

    active = fields.Boolean(string='Active', default=True)
    valid_from = fields.Date(string='Valid From')
    valid_to = fields.Date(string='Valid To')
    year_applied_id = fields.Many2one(comodel_name='config.year.applied', string='Year')
    coverage_amount = fields.Float(string='Actual Coverage', digits=(16, 2))
    min_coverage_amount = fields.Float(string='Minimum Coverage', digits=(16, 2))

    @api.model
    def create(self, values):
        res_id = super(config_yearly_coverage, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(config_yearly_coverage, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class config_model_coverage(models.Model):
    _name = 'config.model.coverage'

    name = fields.Char(compute='_get_name', string='Name', size=256, store=True)
    model_code = fields.Char(compute='_get_model_code', size=32, string='Model Code', store=True)
    type_id = fields.Many2one(comodel_name='product.type', string='Type', required=False)
    body_id = fields.Many2one(comodel_name='product.body', string='Body', required=False)
    brand_id = fields.Many2one(comodel_name='product.brand', string='Brand', required=False)
    model_id = fields.Many2one(comodel_name='product.model', string='Model', required=False)
    color_id = fields.Many2one(comodel_name='product.color', string='Color', required=False)
    weight = fields.Float(string='Unladen Weight', digits=(6, 2))
    capacity = fields.Integer(string='Authorized Capacity')
    coverage_ids = fields.Many2many(
        comodel_name='config.yearly.coverage', relation='config_model_yearly_rel',
        column1='model_coverage_id', column2='yearly_coverage_id', string='Coverage'
    )
    old_unit_code = fields.Char(string='Old Unit Code', size=64)

    # Data Migration Reference
    old_color_code = fields.Char(string='Old Color Code',size=10)
    old_brand_code = fields.Char(string='Old Color Code',size=10)
    old_model_code = fields.Char(string='Old Model Code',size=10)
    old_type_code = fields.Char(string='Old Model Code',size=10)
    coverage_amount = fields.Float(string='Coverage Amount', digits=(16, 2), help="Value will update when the model pricelist is updated.")
    max_cov_yr1 = fields.Float(string='Max Coverage Amount Yr1', digits=(16, 2), help="Value will update when the first year's coverage details are added.")
    min_cov_yr1 = fields.Float(string='Min Coverage Amount Yr1', digits=(16, 2), help="Value will update when the first year's coverage details are added.")
    active = fields.Boolean(string='Active', default=True)

    @api.depends('brand_id', 'model_id', 'color_id')
    def _get_name(self):
        for r in self:
            model_name = ''
            if r.get('brand_id', ''):
                model_name = model_name + r['brand_id'][1] + ' '

            if r.get('model_id', ''):
                model_name = model_name + r['model_id'][1] + ' '

            if r.get('color_id', ''):
                model_name = model_name + '(' + r['color_id'][1] + ')'

            r.name = model_name

    @api.model
    def create(self, values):
        values['model_code'] = self.env['ir.sequence'].get('model.info.seq')
        if 'coverage_ids' in values:
            result = self._on_change_coverage_ids(values['coverage_ids'])
            if result:
                for (key, value) in result['value'].items():
                    values[key] = value
        res_id = super(config_model_coverage, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        if 'coverage_ids' in values:
            result = self._on_change_coverage_ids(values['coverage_ids'])
            if result:
                for (key, value) in result['value'].items():
                    values[key] = value
        else:
            cov_ids = self.read(ids, ['coverage_ids'])
            for cov_id in cov_ids:
                for cov_i in cov_id['coverage_ids']:
                    cov_det = self.env['config.yearly.coverage'].browse(cov_i)
                    if cov_det:
                        if cov_det.year_applied_id.name == '1' and cov_det.active:
                            values['max_cov_yr1'] = cov_det.coverage_amount
                            values['min_cov_yr1'] = cov_det.min_coverage_amount
        ids = super(config_model_coverage, self)._write(cr, uid,  ids, values, context)
        return ids

    @api.depends('model_id')
    def _get_model_code(self):
        for r in self:
            sql_stmt = "Select coalesce(model_code, '') from product_model where id = %s" % (r.model_id.id)

            self.env.cr.execute(sql_stmt)
            try:
                r.model_code = self.env.cr.fetchall()[0][0]
            except Exception, e:
                r.model_code = ''

    # To be deleted, method not in used
    def _compute_coverage_amount(self):
        for r in self:
            sql_stmt = """Select coalesce(coverage_amount, 0.0)
                        from product_model_pricelist
                        where active = True and
                        model_id = %s order by valid_from desc limit 1""" % (r.model_id.id)

            self.env.cr.execute(sql_stmt)
            try:
                r = self.env.cr.fetchall()[0][0]
            except Exception, e:
                r = 0.0

    # To be deleted, method not in used
    def _compute_max_cov_yr1(self):
        for r in self:
            sql_stmt = """Select coalesce(coverage_amount, 0.0),
                            coalesce(minimum_coverage_amount, 0.0)
                        from config_yearly_coverage cov,
                            config_year_applied year,
                            config_model_yearly_rel rel
                        where
                            rel.model_coverage_id = cov.id and
                            rel.yearly_coverage_id = year.id and
                            cov.active = True and
                            year.name::integer = 1
                        """ % (r.model_id.id)
            self.env.cr.execute(sql_stmt)
            try:
                r = self.env.cr.fetchall()[0][0]
            except:
                r = 0.0

    @api.onchange('coverage_ids')
    def _on_change_coverage_ids(self, coverage_ids=None):
        if not coverage_ids:
            coverage_ids = self.coverage_ids
        values = {}
        max_cov_yr1 = min_cov_yr1 = 0.0
        for r in coverage_ids:
            for year in r[2]:
                obj = self.env['config.yearly.coverage'].browse(year)
                if obj and \
                    obj.active and float(obj.year_applied_id.name) == 1:
                    max_cov_yr1 = obj.coverage_amount
                    min_cov_yr1 = obj.min_coverage_amount
                    break

        values['max_cov_yr1'] = self.max_cov_yr1 = max_cov_yr1
        values['min_cov_yr1'] = self.min_cov_yr1 = min_cov_yr1

        return {'value': values}


class config_coverage_type(models.Model):
    _name = 'config.coverage.type'

    name = fields.Char(string='Name', size=24)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    old_claim_code = fields.Char(string='Old Claim Code', size=1)

    # Data Migration Reference
    old_premium_code = fields.Char(string='Old Premium Code', size=25)
    coverage_amount_range_ids = fields.Many2many(
        comodel_name='config.coverage.amount.range', relation='coverage_type_amount_range_rel',
        column1='coverage_type_id', column2='amount_range_id', string='Coverage Amount Range'
    )

    def _check_unique_name(self, values):
        if 'name' in values and values['name']:
            ids = self.search([('name', '=', values['name'])])
            if ids:
                raise Warning(_('ERROR 00102: Coverage Type (%s) already exists!' % values['name']))
        return True

    @api.model
    def create(self, values):
        self._check_unique_name(values)
        res_id = super(config_coverage_type, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        self._check_unique_name(values)
        ids = super(config_coverage_type, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class config_term(models.Model):
    _name = 'config.term'

    name = fields.Char(string='Name', size=24)
    active = fields.Boolean(string='Active', default=True)

    def _check_unique_name(self, values):
        if 'name' in values and values['name']:
            ids = self.search([('name', 'ilike', values['name'])])
            if ids:
                raise Warning(_('ERROR 00103: Term already exists!'))
        return True

    @api.model
    def create(self, values):
        self._check_unique_name(values)
        res_id = super(config_term, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        self._check_unique_name(values)
        ids = super(config_term, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class config_capacity(models.Model):
    _name = 'config.capacity'

    name = fields.Char(string='Name', size=24)
    active = fields.Boolean(string='Active', default=True)

    def _check_unique_name(self, cr, uid, values):
        if 'name' in values and values['name']:
            ids = self.search([('name', 'ilike', values['name'])])
            if ids:
                raise Warning(_('ERROR 00103: Term already exists!'))
        return True

    @api.model
    def create(self, values):
        self._check_unique_name(values)
        res_id = super(config_capacity, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        self._check_unique_name(values)
        ids = super(config_capacity, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class config_insured_product_type(models.Model):
    _name = 'config.insured.product.type'

    name = fields.Char('Name', size=64)
    active = fields.Boolean(string='Active', default=True)
    policy_series_prefix = fields.Char(string='Policy Series Prefix', size=16)

    def _check_unique_name(self, values):
        if 'name' in values and values['name']:
            ids = self.search([('name', 'ilike', values['name'])])
            if ids:
                raise Warning(_('ERROR 00104: Insured product type already exists!'))
        return True

    @api.model
    def create(self, values):
        self._check_unique_name(values)
        res_id = super(config_insured_product_type, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        self._check_unique_name(values)
        ids = super(config_insured_product_type, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class config_year_applied(models.Model):
    _name = 'config.year.applied'

    active = fields.Boolean(string='Active', default=True)
    name = fields.Char(string='Application (in year)',  size=64)
    tpl_coverage = fields.Float(string='TPL Coverage', digits=(16,2))
    tpl_unit_cond = fields.Many2one(comodel_name='config.unit.condition', string='Unit Condition(TPL)')

    @api.model
    def create(self, values):
        try:
            year = float(values['name'])
        except:
            raise Warning(_('Year value is not valid.'))
        res_id = super(config_year_applied, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id


class config_acquisition_type(models.Model):
    _name = 'config.acquisition.type'

    name = fields.Char(string='Acquisition Type', size=64)
    active = fields.Boolean(string='Active', default=True)


class config_unit_condition(models.Model):
    _name = 'config.unit.condition'

    active = fields.Boolean(string='Active', deafault=True)
    name = fields.Char(string='Condition', size=64)


class config_coverage_premium(models.Model):
    _name = 'config.coverage.premium'
    _rec_name = 'coverage_type_id'

    coverage_type_id = fields.Many2one(comodel_name='config.coverage.type', string='Coverage Type')
    is_percentage = fields.Boolean(string='Use Percentage?', default=False)
    is_coverage_fixed = fields.Boolean(string='Is Coverage Amount Fixed?', default=True)
    coverage_amount = fields.Float(string='Coverage Amount', digits=(16, 2))
    internal_rate = fields.Float(string='Internal %', digits=(3, 3))
    external_rate = fields.Float(string='External %', digits=(3, 3))
    internal_premium_amount = fields.Float(string='Internal Premium Amount', digits=(16, 2))
    external_premium_amount = fields.Float(string='External Premium Amount', digits=(16, 2))
    premium_id = fields.Many2one(comodel_name='config.premium', string='Premium Code')
    old_premium_code = fields.Char(string='Old Premium Code', size=24)
    is_internal_formula = fields.Boolean(string='Is Internal based on External premium amount?', default=False)

    @api.onchange('is_coverage_fixed')
    def on_change_coverage_fixed(self):
        if self.is_coverage_fixed:
            self.is_percentage = False
            self.external_rate = 0.00
        else:
            self.is_percentage = True

    @api.onchange('is_percentage')
    def _on_change_is_percentage(self):
        if not self.is_percentage:
            self.external_rate = 0.00

    @api.onchange('coverage_amount', 'external_rate', 'is_coverage_fixed', 'is_internal_formula', 'internal_rate')
    def _on_change_external_rate(self):
        premium_amount = 0.00
        if self.is_coverage_fixed:
            premium_amount = self.coverage_amount * self.external_rate/float(100)

            if self.is_internal_formula:
                self.internal_premium_amount = premium_amount * self.internal_rate/float(100)
        self.external_premium_amount = premium_amount

    @api.onchange('coverage_amount', 'internal_rate', 'is_coverage_fixed', 'is_internal_formula', 'external_premium_amount')
    def _on_change_internal_rate(self):
        premium_amount = 0.00
        values = {}
        if not self.is_internal_formula:
            self.internal_rate = 0.00

        if self.is_coverage_fixed:
            if self.is_internal_formula:
                premium_amount = self.external_premium_amount * self.internal_rate/float(100)
            else:
                premium_amount = self.coverage_amount * self.internal_rate/float(100)
        self.internal_premium_amount = premium_amount

    @api.onchange('external_premium_amount', 'multiplier')
    def _on_change_multiplier(self):
        if self.multiplier > 0:
            self.internal_premium_amount = self.external_premium_amount * self.multiplier/float(100)
        self.internal_premium_amount = 0.00

    @api.model
    def create(self, values):
        if 'is_coverage_fixed' in values and \
                values['is_coverage_fixed'] and \
                    'is_percentage' in values and values['is_percentage']:
            values['external_premium_amount'] = round(values['coverage_amount'] * (values['external_rate'] / 100), 2)

            if 'is_internal_formula' in values and \
                    values['is_internal_formula']:
                values['internal_premium_amount'] = \
                    round(values['external_premium_amount'] * (values['internal_rate'] / 100), 2)
            else:
                values['internal_premium_amount'] = \
                    round(values['coverage_amount'] * (values['internal_rate'] / 100), 2)

        res_id = super(config_coverage_premium, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        if isinstance(ids, list):
            ids = ids[0]
        obj = self.browse(ids)

        if 'is_coverage_fixed' in values and values['is_coverage_fixed']:
            coverage_amount = 0.00
            if 'coverage_amount' in values:
                coverage_amount = values['coverage_amount']
            else:
                coverage_amount = obj.coverage_amount

            if 'external_rate' in values and \
                values['external_rate']:
                values['external_premium_amount'] = round(coverage_amount * (values['external_rate'] / 100), 2)

            if 'internal_rate' in values and \
                values['internal_rate'] and \
                'is_internal_formula' in values and \
                values['is_internal_formula']:

                if 'external_premium_amount' in values:
                    values['internal_premium_amount'] = \
                        round(values['external_premium_amount'] * (values['internal_rate'] / 100), 2)
                else:
                    values['internal_premium_amount'] = \
                        round(obj.external_premium_amount * (values['internal_rate'] / 100), 2)
            elif 'internal_rate' in values and \
                values['internal_rate']:
                values['internal_premium_amount'] = round(coverage_amount * (values['internal_rate'] / 100), 2)

        ids = super(config_coverage_premium, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class config_memorial_lot_type(models.Model):
    _name = 'config.memorial.lot.type'
    _description = 'Memorial Lot Type'

    name = fields.Char(string='Name', size=64)
    description = fields.Text(string='Payment Terms')


class config_memorial_area(models.Model):
    _name = 'config.memorial.area'
    _description = 'Memorial Area'

    name = fields.Char(string='Name', size=64)
    description = fields.Text(string='Description')

    @api.model
    def create(self, values):

        ids = self.search([('name', 'ilike', values['name'])])
        if ids:
            raise Warning(_('ERROR 000103: Memorial Area already exists!'))
        res_id = super(config_memorial_area, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id


class config_memorial_pricelist(models.Model):
    _name = 'config.memorial.pricelist'
    _description = 'MRI Pricelist'

    name = fields.Char(compute='_get_name', string='Name', size=256, store=True)
    area_id = fields.Many2one(comodel_name='config.memorial.area', string='Area')
    lot_type_id = fields.Many2one(comodel_name='config.memorial.lot.type', string='Lot Type')
    description = fields.Text(string='Payment Terms')
    valid_from = fields.Date(string='Valid From')
    valid_to = fields.Date(string='Valid To')
    price = fields.Float(string='Selling Price', digits=(16,2))
    dp_actual = fields.Float(string='Actual Downpayment', digits=(16,2))
    dp_split = fields.Float(string='Split Downpayment', digits=(16,2))
    dp_mos = fields.Integer(tring='# of Split Mo.')
    term_id = fields.Many2one(comodel_name='config.term', string='Terms')
    balance = fields.Float(compute='_compute_balance', string='Balance', store=True)
    monthly_amortization = fields.Float(string='Monthly Amortization', digits=(16,2))
    mri_coverage = fields.Float(compute='_compute_mri_coverage', string='MRI Coverage', store=True)
    mri_amount = fields.Float(compute='_compute_mri_amount', string='MRI Amount', store=True)
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, values):
        res_id = super(config_memorial_pricelist, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.depends('price', 'dp_actual')
    def _compute_balance(self):
        #(D12*15%)/3
        for r in self:
            balance = 0.00
            if r.price:
                balance = r.price - r.dp_actual
            r.balance = balance

    @api.depends('monthly_amortization', 'term_id', 'dp_split', 'dp_actual')
    def _compute_mri_coverage(self, cr, uid, ids, field, arg, context=None):
        # monthly_amortization * terms + dp_split - dp_full
        for r in self:
            r.mri_coverage = r.monthly_amortization * int(r.term_id.name.split(' ')[0]) + r.dp_split - r.dp_actual

    @api.depends('mri_coverage')
    def _compute_mri_amount(self, cr, uid, ids, field, arg, context=None):
        # mri_coverage/1000 * 12
        for r in self:
            mri_amount = 0.00

            if r.mri_coverage:
                r.mri_amount = round((r.mri_coverage / 1000 * 12), 2)

    @api.onchange(
        'price', 'dp_actual', 'dp_split', 'term_id', 'balance', 'monthly_amortization', 'mri_coverage', 'mri_amount')
    def _on_change_mri(self):
        self.balance = self.mri_coverage = self.mri_amount = 0.00
        self.balance = self.price - self.dp_actual

        term_obj = {}
        if self.term_id:
            term_obj = self.env['config.term'].read(self.term_id, ['name'])
        terms = term_obj.get('name', ['0 months'])
        terms = terms[0].split(' ')[0]
        self.mri_coverage = self.monthly_amortization * int(terms) + self.dp_split - self.dp_actual

        if self.mri_coverage:
            self.mri_amount = self.mri_coverage / 1000 * 12

    @api.depends('area_id', 'lot_type_id', 'description')
    def _get_name(self):
        for r in self:
            r.name = r.area_id.name + ' - ' + r.lot_type_id.name + ' (' + r.description + ')'

    @api.model
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None):
        if context and 'issued_date' in context and context['issued_date']:
            args = [
                ('active', '=', True),
                ('valid_from', '<=', context['issued_date']),
                '|', ('valid_to', '>=', context['issued_date']),
                ('valid_to', '=', False)]
        return super(config_memorial_pricelist, self).search(
            args, offset=offset, limit=limit, order=order, context=context, count=count)


class config_denomination(models.Model):
    _name = 'config.denomination'
    _description = __doc__
    _order = 'denomination desc'

    active = fields.Boolean(string='Active', default=True)
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


class config_reports_limit(models.Model):
    _name = 'config.reports.limit'
    _description = __doc__

    object_id = fields.Many2one(comodel_name='ir.model', string='Object Name', required=True)
    print_cntr = fields.Integer('Print Limit', required=True)
    records = fields.One2many(comodel_name='config.reports.limit.records', inverse_name='limit_id', string='Labels')
    active = fields.Boolean(string='Active', default=True)


class config_reports_limit_records(models.Model):
    _name = 'config.reports.limit.records'
    _description = __doc__

    record_id = fields.Integer(string='Record No.')
    rec_print_cnt = fields.Integer(string='Number of Prints')
    limit_id = fields.Many2one(comodel_name='config.reports.limit', string='Report Limit')
    active = fields.Boolean(string='Active', default=True)


class config_coverage_amount_range(models.Model):
    _inherit = 'config.coverage.amount.range'
    _description = __doc__

    name = fields.Chat(related='_get_value_string', size=64, string='Name', store=True)
    coverage_amount = fields.Float(string='Coverage Amount', digits=(16, 2))
    active = fields.Boolean(string='Active', default=True)

    def _check_unique_name(self, values):
        if 'coverage_amount' in values and values['coverage_amount']:
            ids = self.search([('coverage_amount', '=', values['coverage_amount'])])
            if ids:
                raise Warning(_('ERROR 00103: Coverage Amount already exists for this type!'))

    @api.model
    def create(self, values):
        self._check_unique_name(values)
        res_id = super(config_coverage_amount_range, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.depends('name')
    def _get_value_string(self):
        for r in self:
            r.name = '{0:,.2f}'.format(r.coverage_amount)
