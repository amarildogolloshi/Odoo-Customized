from openerp import models, fields, api, SUPERUSER_ID
from datetime import datetime
from openerp.exceptions import ValidationError

def _get_allowed_company(self):
    user_id = self.env.user.id
    res_company = self.env['res.users'].browse(user_id)
    company_ids =  res_company.company_ids
    company = []
    for comp in company_ids:
        company.append(comp.id)
    return company

def _get_current_date(self):
    today = datetime.today()
    return today

def _get_default_branch(self):
    user_id = self.env.user.id
    res_id = self.env['res.users'].search([('id', '=', user_id)]).id
    res = self.env['res.users'].browse(res_id)

    return res.branch_id.id

def _get_allowed_branches(self):
    user_id = self.env.user.id
    res_id = self.env['res.users.branches'].search([('user_id', '=', user_id),('active', '=', True)])
    res = self.env['res.users.branches'].browse(res_id)

    return res.branch_id
