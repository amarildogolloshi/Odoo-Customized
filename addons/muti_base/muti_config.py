# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions
from openerp.exceptions import Warning, ValidationError # osv.osv_except replacement
from openerp.tools.translate import _
# from datetime import timedelta, time, date, datetime
# import re
# from dateutil.relativedelta import relativedelta
# import psycopg2
# from dateutil import parser
# import sys

class config_witness(models.Model):
    _name = 'config.witness'
    _description = __doc__

    def _get_branch_id(self):
        return self.env.user.branch_id

    branch_id = fields.Many2one(
        comodel_name='config.branch',
        string='Branch',
        required=True,
        default=_get_branch_id,
        active=True
    )
    witness1 = fields.Char(string='Witness 1', size=100)
    witness1_ctc = fields.Char(string='CTC #', size=100)
    witness1_ctc_date = fields.Date(string='CTC Date')
    witness1_ctc_place = fields.Char(string='CTC Place Issued', size=100)
    witness2 = fields.Char(string='Witness 2', size=100)
    witness2_ctc = fields.Char(string='CTC #', size=100)
    witness2_ctc_date = fields.Date(string='CTC Date')
    witness2_ctc_place = fields.Char(string='CTC Place Issued', size=100)
    internal_auditor = fields.Char(string='Internal Auditor', size=150)
    active = fields.Boolean(string='Active', default=True)
    city_id = fields.Many2one(comodel_name='config.city', string='Branch Municipality/City')
    bm_id = fields.Many2one(comodel_name='res.users', string='Name', required=True)
    bm_ctc_address = fields.Char(string='Address', size=250, help='BM Address indicated in CTC')
    bm_ctc = fields.Char(string='CTC #', size=100)
    bm_ctc_date = fields.Date(string='CTC Date')
    bm_ctc_place = fields.Char(string='CTC Place Issued', size=100)

    @api.model
    def create(self, values):
        if values.has_key('branch_id'):
            br_id = values['branch_id']
        else:
            values['branch_id'] = self.env['res.users'].browse(self._uid).branch_id.id
            br_id = values['branch_id']

        validate_br = self.search([('branch_id','=',br_id)])
        if validate_br:
            raise Warning(_('WARNING 00098: One record per branch.'))

        res_id = super(config_witness, self).create(values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        if values.has_key('branch_id'):
            br_id = values['branch_id']
        else:
            values['branch_id'] = self.env['res.users'].browse(self._uid).branch_id.id
            br_id = values['branch_id']
        validate_br = self.read(ids[0], ['branch_id'])
        if validate_br:
            if validate_br['branch_id'][0] != br_id:
                raise Warning(_('WARNING 00099: You cannot edit records of other branch.'))
        ids = super(config_witness, self)._write(cr, uid,  ids, values, context)
        return ids

    @api.model
    # def search(self, cr, uid, args, offset=0, limit=None, order=None, context={}, count=False, access_rights_uid=None):
    def search(self, args, offset=0, limit=None, order=None, count=False):
        results = []
        if not self._uid == 1:

            user_obj = self.env['res.users'].read(self._uid, ['branch_id'])

            if not user_obj:
                return results

            args.append(('branch_id', '=', user_obj['branch_id'][0]))

        return super(config_witness, self).search(
            args, offset=offset, limit=limit, order=order, count=count)


class config_area(models.Model):
    _name = 'config.area'

    name = fields.Char(string='Area name')
    # branch_id = fields.One2many(comodel_name='config.branch', inverse_name='area_id', string='Branch/Department')
    area_code = fields.Integer(string="Area code")
    branch_list = fields.One2many(comodel_name='config.branch', inverse_name='area_id', string='Assigned Branches', required=False)
    branch_names = fields.Char(compute='_get_branch_names', size=64, string='Assigned Branches', store=False)

class config_bracket(models.Model):
    _name = 'config.bracket'
    _description = 'Branch classification based on portfolio and perfomance rating.'

    name = fields.Char(string='Name', size=24)
    description = fields.Char(string='Description')


class config_document_number_format(models.Model):
    _name = 'config.document.number.format'
    _description = __doc__

    document = fields.Char(string='Document', size=100)
    is_system_generated = fields.Boolean(string='System Generated?')
    prefix = fields.Char(string='Prefix', size=50)
    length_series = fields.Integer(string='Length of Series')
    model = fields.Char(string='Model', size=100)
    field = fields.Char(string='Field', size=100)
    obj_date_field = fields.Char(string='Date Field of Object', size=100)
    active = fields.Boolean(string='Active', default=True)

