# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
import time
from dateutil import parser
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF

class muti_appraisal(models.Model):
    _name = 'muti_appraisal.appraisal'
    _description = 'MUTI Appraisal'
        
    @api.model
    def create(self, vals):
        vals['state'] = 'draft'
         
        res = super(muti_appraisal, self).create(vals)   
        return res
    
    @api.multi  
    def write(self, vals):

        return super(muti_appraisal, self).write(vals)
    
    @api.multi
    def _get_default_comp_id(self):
        company_id = self.env.ref('base.main_company')
        company_res = self.env['res.company'].search([('parent_id','=',company_id.id)], limit=1)
        company_id = company_res.id
        return company_res
        
    name = fields.Char(string="Name")
    bulk = fields.Boolean(string="Bulk", default=False)
    company_id = fields.Many2one('res.company', string="Company", default=_get_default_comp_id)
    branch_id = fields.Many2one('res.company', string="Branch")
    hr_dept_id = fields.Many2one('hr.department', string="Department") 
    job_id = fields.Many2one('hr.job', string="Position")   
    employee_id = fields.Many2one('hr.employee', string="Employee")
    employee_ids = fields.Many2many('hr.employee','appraisal_employee_rel', 'appraisal_id', 'emp_id', string="Employee")
    survey_id = fields.Many2one('survey.survey', string="Type of Appraisal")
    report_id = fields.Many2one('ir.actions.report.xml', string="Report")
    start_date = fields.Date(string="Start Date",default = lambda *a: time.strftime('%Y-%m-%d'))
    end_date = fields.Date(string="End Date",default = lambda *a: time.strftime('%Y-%m-%d'))
    deadline = fields.Date(string="Appraisal Deadline",default = lambda *a: time.strftime('%Y-%m-%d'))
    rater_id = fields.Many2one('hr.employee', string="Rater")
    superior_id = fields.Many2one('hr.employee', string="Rater's Superior")
    state =  fields.Selection([
            ('draft', 'New'),
            ('cancel', 'Cancelled'),
            ('wait', 'In Progress'),
            ('progress', 'Waiting Appreciation'),
            ('done', 'Done'),
        ], 'Status', copy=False)


    @api.multi
    def name_get(self):
   
        res = super(muti_appraisal, self).name_get()
        data = []
        for r in self:
            display_value = str(r.deadline) + '/' +str(r.employee_id.name)
            data.append((r.id, display_value))
        return data
    
    @api.onchange('bulk')
    def _choose_bulk(self): 
        self.employee_id = False
        self.company_id = False
        self.branch_id = False
        self.hr_dept_id = False
        self.job_id = False
        self.report_id = False
        self.rater_id = False
        return {'domain':{'rater_id':[('active','=',True)]},
                }
    
    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            self.employee_ids = self.employee_id
            job_level_id = self.employee_id.job_level.parent_id
            res_config_appraisal = self.env['config.appraisal'].search([('job_level_id','=',job_level_id.id)])
            if not  res_config_appraisal:
                raise ValidationError(" '%s' not defined in Employees>Appraisal>Appraisal Type" % str(job_level_id.name) )
            else:
                for rec in res_config_appraisal:
                    report_id = rec.report_id.id
                    self.report_id = report_id
                    

            report_to_ids = []            
            for rec in self.employee_id.emp_report_to_ids:
                report_to_ids.append(rec.id)
            return {'domain':{'rater_id':[('id','in',report_to_ids)],'report_id':[('id','in',[report_id])]},
                    
                }    
    

    @api.onchange('company_id')
    def onchange_company_id(self):       
        company_id = self.env.ref('base.main_company').id
        self.employee_id = False
        self.branch_id = False
        self.hr_dept_id = False
        self.job_id = False
        self.report_id = False
        self.rater_id = False
        return {'domain':{'branch_id':[('parent_id','=',[self.company_id.id])],'company_id':[('parent_id','=',[company_id])],\
                          'hr_dept_id':[('company_id','child_of',[self.company_id.id])]},
                    
                }
    @api.onchange('branch_id')
    def onchange_branch_id(self):
        self.employee_id = False
        self.hr_dept_id = False
        self.job_id = False
        self.report_id = False
        self.rater_id = False
        branch_id = self.branch_id.id
        if branch_id:
            args =  ('company_id','=',[branch_id])
        else:
            args =  ('company_id','=', self.company_id.id)
        return {'domain':{'hr_dept_id':[args]},
                }
        
    @api.onchange('hr_dept_id')
    def onchange_hr_dept_id(self): 
        self.employee_id = False
        self.job_id = False
        self.report_id = False
        self.rater_id = False
        emp_res = self.env['hr.employee'].search([('active','=',True),('department_id','=',self.hr_dept_id.id)])
        job_ids = []
        for rec_emp in emp_res:
            job_ids.append(rec_emp.job_id.id)
        return {'domain':{'job_id':[('id','in',job_ids)],},
                }

    @api.onchange('job_id')
    def onchange_job_id(self):
        emp_res = self.env['hr.employee'].search([('active','=',True),('department_id','=',self.hr_dept_id.id),('job_id','=',self.job_id.id)])
        job_level_id = self.job_id.job_level_id.parent_id.id
        res_config_appraisal = self.env['config.appraisal'].search([('job_level_id','=',job_level_id)])
        get_report_ids = []
        for rec in res_config_appraisal:
            report_id = rec.report_id.id
            get_report_ids.append(rec.report_id.id)
            self.report_id = report_id
        self.employee_ids = emp_res
        return {'domain':{'report_id':[('id','in',get_report_ids)],},
                }
        
    @api.onchange('rater_id')
    def onchange_rater_id(self):
        if self.rater_id:
            report_to_ids = []            
            for rec in self.rater_id.emp_report_to_ids:
                report_to_ids.append(rec.id)
            return {'domain':{'superior_id':[('id','in',report_to_ids)]},
                    
                }    
        
    def _print_report(self, data):
        return self.env['report'].sudo().get_action(self, 'muti_appraisal.probationary_monitoring_template', data=data) 

    def _build_contexts(self, data):
        result = {}
        
        result['report_id'] = data['form']['report_id'] 
        result['employee_id'] = data['form']['employee_id']
        result['company_id'] = data['form']['company_id']
        result['hr_dept_id'] = data['form']['hr_dept_id'] 
        result['job_id'] = data['form']['job_id'] 
        result['rater_id'] = data['form']['rater_id'] 
        print 'result', result

        return result
    
    @api.multi
    def process_appraisal(self, vals):
       
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['bulk','report_id','employee_id','company_id','hr_dept_id','job_id','rater_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))      
        print 'process_data', data['form']  
        if self.report_id:
            template_name = self.report_id.report_name
            print 'template_name', template_name
            return self.env['report'].sudo().get_action(self, str(template_name), data=data)  

