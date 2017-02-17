from openerp import models, fields, api
from datetime import datetime, timedelta


class hrms_monthly_report(models.Model):
    _name = 'muti_hrms.monthly.report'
    _description = 'Muti Hrms Reports'
    
    
    report_id = fields.Many2one('ir.actions.report.xml', string="Report Name")
    rep_option = fields.Selection([('as_of', 'As Of'),
                                 ('range','Range')],
                                    'Option')
    date_as_of = fields.Date(string="As Of")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    hr_dept_id = fields.Many2one('hr.department', string="Branch/Department")
    company_id = fields.Many2one('res.company', string="Company")

    def _print_report(self, data):
        report_name = self.report_id.report_name
        return self.env['report'].sudo().get_action(self, str(report_name), data=data) 
# 
    def _build_contexts(self, data):
        result = {}
        result['report_id'] = data['form']['report_id']
        result['rep_option'] = data['form']['rep_option']
        result['date_as_of'] = data['form']['date_as_of']
        result['date_from'] = data['form']['date_from']
        result['date_to'] = data['form']['date_to']
        result['hr_dept_id'] = data['form']['hr_dept_id']
        result['company_id'] = data['form']['company_id']
 
        return result
    
    
    @api.multi
    def action_generate(self, vals):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['report_id','rep_option','date_as_of','date_from','date_to','hr_dept_id','company_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
        return self._print_report(data)
    
    
#     @api.multi
#     def action_preview(self, vals):
#         self.probationary_ids
    
    
    @api.onchange('company_id')
    def _company_id(self):
        return {'domain':{'hr_dept_id':[('company_id','child_of',self.company_id.id)]},
                }
                     