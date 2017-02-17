# -*- coding: utf-8 -*-
from datetime import timedelta,time,date,datetime
from dateutil import parser
from openerp import models, fields, api, exceptions


class res_users_branches(models.Model):
    _name = 'res.users.branches'

    user_id = fields.Many2one(comodel_name='res.users', string='User ID', ondelete='cascade', required=True)
    branch_id = fields.Many2one(comodel_name='config.branch', string='Branch', ondelete='cascade', required=True)
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, values):
        res_id = super(res_users_branches, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(res_users_branches, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class res_users_group_scheduler(models.Model):
    _name = 'res.users.group.scheduler'

    user_id = fields.Many2one(comodel_name='res.users', string='User ID', ondelete='cascade', required=True)
    group_id = fields.Many2one(comodel_name='res.groups', string='Group', ondelete='cascade', required=True)
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='Start Date')


    @api.model
    def create(self, values):
        res_id = super(res_users_group_scheduler, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(res_users_group_scheduler, self)._write(cr, uid,  ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class res_users(models.Model):
    _inherit = 'res.users'

    nickname = fields.Char(string='Nickname', required=False, )
    branch_ids = fields.Many2many(comodel_name='config.branch', string='Allowed Branch/es')
    branch_id = fields.Many2one(comodel_name='config.branch', string='Branch', ondelete='cascade', required=False)
    assigned_branches = fields.One2many(comodel_name='res.users.branches', inverse_name='user_id', string='Assigned Branches')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner', ondelete='cascade')
    deactivate_date = fields.Date(string='Deactivation Date')
    deactivate_reason = fields.Char(string='Reason', size=64)
    scheduler = fields.One2many(comodel_name='res.users.group.scheduler', inverse_name='user_id', string='Scheduler')