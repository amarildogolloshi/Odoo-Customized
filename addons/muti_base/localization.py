# -*- coding: utf-8 -*-
from datetime import timedelta, time, date, datetime
# from dateutil import parser
from openerp import models, fields, api, exceptions
import sys
import json
import re
from openerp.tools.translate import _


class config_logs(models.Model):
    _name = 'config.logs'
    _description = __doc__

    encoder = fields.Many2one(comodel_name='res.users', string='User')
    rec_id = fields.Integer(string='ID')
    vals = fields.Text(string='Values')
    model = fields.Many2one(comodel_name='ir.model', string='Model')
    datetime = fields.Date(string='Date/Time', default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    active = fields.Boolean(string='Active', default=True)
    operation = fields.Char(string='Operation', size=12)

    def save_logs(self, model, rec_id, values):
        rec = self.env['ir.model'].search([('model', '=', model)]).id
        if isinstance(rec_id, list):
            rec_id = rec_id[0]

        self.create({
            'rec_id': rec_id,
            'operation': sys._getframe().f_back.f_code.co_name,
            'vals': json.dumps(values, sort_keys=True, indent=4),
            'model': rec,
        })

        return True



class company(models.Model):
    _inherit = 'res.company'

    branch_id = fields.One2many(comodel_name='config.branch', inverse_name='company_id', string='Business Unit')
    code = fields.Char(string='Code')
    abbreviation = fields.Char(string='Abbreviation')
    area_id = fields.Many2one(comodel_name='config.area', string='Area')
    is_branch = fields.Boolean(string="Branch")
    active = fields.Boolean(string="Active", default=True)
    
    _sql_constraints = [
    ('name_uniq', 'unique (name,active)', 'The company name must be unique !')
    ]

    
class config_branch(models.Model):
    _name = 'config.branch'
    _order = 'name'

    def _get_branch_code(self):
        _query = 'SELECT branch_code FROM config_branch \
                  WHERE RTRIM(branch_code) != \'\' \
                  ORDER BY CAST(branch_code as INT) desc limit 1;'

        self._cr.execute(_query)
        id_returned = self._cr.fetchone()
        if id_returned:
            return int(id_returned[0]) + 1
        else:
            return 1

    branch_code = fields.Char(string='Branch code', default=_get_branch_code)
    name = fields.Char(string='Branch name', required=True)
    address = fields.Char(string='Branch address')
    telno = fields.Char(string='Branch tel #')
    # email = fields.Char(string='Email')
    is_central = fields.Boolean(string='Home Office')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner', required=True)
    active = fields.Boolean(string='Active', default=True)
    area_id = fields.Many2one(comodel_name='config.area', string='Area', required=True)
    company_id = fields.Many2one(comodel_name='res.company', string='Company')
    namerec = fields.Char(compute='_get_branch_namecode')
    mailing_list = fields.Char(string='Mailing List')
    manager = fields.Many2one(comodel_name='res.users', string='Manager', ondelete="cascade")
    # old_branch_code = fields.Char(string='Old Branch Code', size=20, readonly=True)
    bracket_id = fields.Many2one(comodel_name='config.bracket', string='Bracket')
    wh_promo_id = fields.Many2one(comodel_name='config.wh.interest.promo', string='Promo')

    def _check_email_address_input_format(self, data1):
        compiled_regex = re.compile("(^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$)")
        if data1:
            if not compiled_regex.match(data1):
                raise Warning(_('Please correct the format of the email address (it must be name@domain.com)'))

    @api.onchange('mailing_list')
    def onchange_mailing_list(self):
        compiled_regex = re.compile("(^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$)")
        if self.mailing_list:
            if not compiled_regex.match(self.mailing_list):
                return {
                    'warning': {'title': 'Invalid email', 'message': 'Please supply a valid email'},
                }

    @api.model
    def create(self, values):
        if 'mailing_list' in values:
            self._check_email_address_input_format(values['mailing_list'])

        if values['branch_code'] in [False, True, None]:
            values['branch_code'] = self._get_branch_code()
        else:
            try:
                int(values['branch_code'])
            except:
                values['branch_code'] = self._get_branch_code()
        res_id = super(config_branch, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id


    @api.multi
    def write(self, vals, context={}):
        if 'mailing_list' in vals:
            self._check_email_address_input_format(vals['mailing_list'])

        if 'branch_code' in vals:
            if vals['branch_code'] in [False, True, None]:
                vals['branch_code'] = self._get_branch_code()
            else:
                try:
                    int(vals['branch_code'])
                except:
                    vals['branch_code'] = self._get_branch_code()

        res = super(config_branch, self).write(vals)
        if ('wh_promo_id' not in vals) and \
                ('_terp_view_name' in context and context['_terp_view_name'] != 'Interest Rate Promo'):
            self.env['config.logs'].save_logs(self._name, res, vals)
        return res


    def _search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None):
        if context:
            if 'forexcludebranch' in context:
                branch_id = context['forexcludebranch'][0]
                args.append(('id', '!=', branch_id))

            if 'apv_branch' in context:
                branches = []
                br = self.env['config.branch'].read(context['apv_branch'][0], ['is_central'])
                if br:
                    if not br['is_central']:
                        branches.append(context['apv_branch'][0])

                        br_central = self.env['config.branch'].search([('is_central','=',True)])
                        if br_central:
                            branches.append(br_central[0])
                        args.append(('id', 'in', branches))

        return super(config_branch, self)._search(
            cr, uid, args, offset=offset, limit=limit, order=order, context=context,
            count=count, access_rights_uid=access_rights_uid
        )

    @api.depends('branch_code')
    def _get_branch_namecode(self):
        for r in self:
            r.namerec = r.branch_code + ' - ' + r.name

    _sql_constraints = [('unique_name', 'UNIQUE(name,active)', 'A record with the same name already exists.')]


class config_province(models.Model):
    _name = 'config.province'
    
    province_code= fields.Integer(string = 'Code', required = True)
    old_prov_code = fields.Char(string = 'Old Code')
    name = fields.Char(string = 'Name', required = True)
    active = fields.Boolean(string = 'Active')
    
class config_city(models.Model):
    _name = 'config.city'
    
    city_code = fields.Char(string = 'Code', required = True)
    name = fields.Char(string = 'City/Municipality' , required = True)
    province_id = fields.Many2one('config.province', string  = 'Province')
    active = fields.Boolean(string = 'Active')
    old_municipal_code = fields.Char(string = 'Old Code')
    

class config_barangay(models.Model):
    _name = 'config.barangay'
    
    brgy_code = fields.Char(string = 'Code' ,required = True)
    name = fields.Char(string = 'Barangay', required = True)
    city_id = fields.Many2one('config.city', string  = 'City/Municipality', ondelete="cascade", onwrite="cascade")
    zip_code = fields.Char(string = 'Zip Code',size = 4)
    province_name = fields.Char(related = 'city_id.province_id.name')
    old_brgy_code = fields.Char(string = 'Old Code')
    active = fields.Boolean(string = 'Active')

    