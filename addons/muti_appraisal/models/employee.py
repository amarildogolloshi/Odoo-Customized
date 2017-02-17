from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
import time

class hr_employee(models.Model):
    _inherit = 'hr.employee'
    
    probitionary_monitoring_ids = fields.One2many('probationary.monitoring', 'hr_emp_id', string="Employee Monitoring")
    regular_monitoring_ids = fields.One2many('regular.monitoring', 'hr_emp_id', string="Employee Monitoring")
    appraisal_id = fields.Many2one('muti_appraisal.appraisal', string="Appraisal")
    probi_state = fields.Selection([
                    ('draft', 'New'),
                    ('fin', 'Finalize'),
                ], 'Status', copy=False, default='draft')
#     probi_remarks = fields.Text(string="Remarks") 
    appraisal_evaluation_ids = fields.One2many('config.appraisal.evaluation','hr_employee_id', string="Evaluation") 

    @api.multi    
    def action_probi_draft(self):
        self.env['probationary.monitoring'].search([('hr_emp_id','=',self.id)]).write({'state':'draft'})
        self.probi_state = 'draft'
    
    @api.multi    
    def action_probi_final(self):
        self.env['probationary.monitoring'].search([('hr_emp_id','=',self.id)]).write({'state':'fin'})
        self.probi_state = 'fin'

        
class probationary_monitoring(models.Model):
    _name = 'probationary.monitoring'
    _order = 'appraisal_num'
    
    def _get_years(self):
        
        this_year = datetime.today().year
        
        results = [(str(x), str(x)) for x in range(this_year-40, this_year+10)]
        return results
    
    
    
    name = fields.Char(string="Name") 
    appraisal_num = fields.Selection([(1, '1st'), (2, '2nd'), (3, '3rd'), (4, '4th'), (5, '5th'), (6, '6th'), (7, '7th'), (8, '8th'), (9, '9th'), (10, '10th')], default=1, required=True, string="Appraisal No.")
    appraisal_date = fields.Date(string="Appraisal Date")
    rating = fields.Float(string="Rating", digits=(16, 2))
    description = fields.Char(string="Description")
    remarks = fields.Text(string="Remarks")
    hr_emp_id = fields.Many2one('hr.employee', string="HR Employee")
    dept_id = fields.Many2one('hr.department', string="Branch/Dept", related='hr_emp_id.department_id')
    company_id = fields.Many2one('res.company', string="Company", related='dept_id.company_id')
    rater_id = fields.Many2one('hr.employee', string="Rater")
    emp_id = fields.Char(string="Employee", related="hr_emp_id.emp_id")
    state =  fields.Selection([
            ('draft', 'New'),
            ('fin', 'Finalize'),
        ], 'Status', copy=False, default='draft')
    
 
    @api.model
    def create(self, vals):
        if 'rating' in vals:
            rate = vals['rating']
            desc = self._get_rating_desc(rate)
            vals['description'] = desc
   
        return super(probationary_monitoring, self).create(vals)

    @api.multi
    def write(self, vals): 
        res_id = super(probationary_monitoring, self).write(vals)       
        for rec in self:
            if 'rating' in vals:
                rate = vals['rating']
            else:
                rate = rec.rating
            desc = rec._get_rating_desc(rate)
            if 'description' in vals:
                vals['description'] = desc
            else:               
                rec.description = desc
                 
        return res_id
    
    @api.onchange('appraisal_num')
    def onchange_appraisal_num(self):
        appraisal_num = self.appraisal_num
        emp_id = self.emp_id
        res_emp = self.env['hr.employee'].search([('emp_id','=',emp_id)])
        res_aprsl_eval = self.env['config.appraisal.evaluation'].search([('appraisal_num','=',appraisal_num),('hr_employee_id','=', res_emp.id)])
        self.appraisal_date = res_aprsl_eval.due_date
         
    @api.model   
    def probi_reminder_email(self):
        print 'probationary_email running'
        today = datetime.today().strftime('%Y-%m-%d')
        res_probi_mntr = self.env['probationary.monitoring'].search([('appraisal_date','>=',today)])
        for rec in res_probi_mntr:
            appraisal_date =  rec.appraisal_date
            d1 = datetime.strptime(today, '%Y-%m-%d')
            d2 = datetime.strptime(appraisal_date, '%Y-%m-%d')
            daysDiff = str((d2-d1).days) 
            print 'daysDiff', daysDiff
# SEND EMAIL            
            template_id = self.env.ref('muti_appraisal.email_temp_probi_reminder')
            self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)
#             if daysDiff <= 5:
#                 
            
        
         
#     @api.onchange('emp_id')
#     def onchange_emp_id(self):
# 
#         emp_id = self.emp_id
#         res_emp = self.env['hr.employee'].search([('emp_id','=', emp_id)])
#         aprsl_eval_ids = res_emp.appraisal_evaluation_ids
#         print 'aprsl_eval_ids', aprsl_eval_ids
#         aprsl_num = []
#         for rec in aprsl_eval_ids:
#             aprsl_num.append(rec.appraisal_num)
#         return {'domain':{'appraisal_num':[('id','in ',[1])]},
#                 }
    
    @api.onchange('rating')
    def onchange_rating(self):
        rate = self.rating
        desc = self._get_rating_desc(rate)
        self.description =  desc


    def _get_rating_desc(self,rate):
        res_rating = self.env['config.appraisal.rating'].search([('active','=',True),('start_rate','<=',rate),('end_rate','>=',rate)])
        if res_rating:
            for rating_id in res_rating:
                desc = rating_id.description
                print 'description', desc
            
            return desc
        
        
class regular_monitoring(models.Model):
    _name = 'regular.monitoring'
    
    name = fields.Char(string="Name")
    date = fields.Date(string="Date")
    rating = fields.Float(string="Rating", digits=(16, 2))
    description = fields.Char(string="Description")
    remarks = fields.Text(string="Remarks")
    hr_emp_id = fields.Many2one('hr.employee', string="HR Employee")  
    rater_id = fields.Many2one('hr.employee', string="Rater")  
    
class hr_employee(models.Model):
    _inherit = 'hr.employee'
    
    def _search(self, cr, uid, args, offset=0, limit=None, order=None,
        context={}, count=False, access_rights_uid=None):
        
        if context:
            if 'employee_id' in context:
                employee_id =  context['employee_id']
                res_emp = self.pool.get('hr.employee').search(cr,uid,[('emp_id','=',employee_id)])
                report_to_ids = []
                for rec_emp in res_emp:
                    emp_obj = self.pool.get('hr.employee').browse(cr, uid,rec_emp)
                    get_report_to_ids = emp_obj.emp_report_to_ids
                    for rec in get_report_to_ids:
                        report_to_ids.append(rec.id)
                args.append(("id","in",report_to_ids))                
        return super(hr_employee, self)._search(cr, uid, args, offset=offset, limit=limit, order=order,
                                            context=context, count=count, access_rights_uid=access_rights_uid)