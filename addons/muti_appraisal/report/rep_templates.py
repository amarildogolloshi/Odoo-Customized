from openerp import models, fields, api
 
 
class ReportRankFileAppraisal(models.AbstractModel):
    _name = 'report.muti_appraisal.rank_file_template'
    
#     def _probi_monitoring(self, data):
#         probi_res = {}
#         request = ("select id,name,description,hr_emp_id from probationary_monitoring group by hr_emp_id,name,description,id")
# 
#         self.env.cr.execute(request)
#         for row in self.env.cr.dictfetchall():
#             probi_res[row.pop('id')] = row
#         
#         return probi_res
    
    
    @api.multi
    def render_html(self, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        bulk = data['form']['bulk']
        if 'employee_id' in data['form']:
            if data['form']['employee_id']:
                employee_id = data['form']['employee_id'][0]
            else:
                employee_id = False
        else:
            employee_id = ''
        
        if 'report_id' in data['form']:
            if data['form']['report_id']:
                report_id =  data['form']['report_id'][0]
            else:
                report_id = False
        else:
            report_id = ''
        
        if 'company_id' in data['form']:
            if data['form']['company_id']:
                company_id = data['form']['company_id'][0]
            else:
                company_id = False
        else:
            company_id = ''
            
        if 'hr_dept_id' in data['form']:
            if data['form']['hr_dept_id']:
                hr_dept_id = data['form']['hr_dept_id'][0]
            else:
                hr_dept_id = False    
        else:
            hr_dept_id = '' 
        
        if 'job_id' in data['form']:
            if data['form']['job_id']:
                job_id = data['form']['job_id'][0]
            else:
                job_id = False
        else:
            job_id = '' 
        
        if 'rater_id' in data['form']:
            if data['form']['rater_id']:
                rater_id =  data['form']['rater_id'][0]
            else:
                rater_id = False
        else:
            rater_id = ''
        
        
        print 'bulk', bulk
        print 'employee_id', employee_id
        print 'report_id', report_id
        print 'company_id', company_id
        print 'hr_dept_id', hr_dept_id
        print 'job_id', job_id
        print 'rater_id', rater_id
        print 'data_form', data['form']['bulk']
        
        
#         date_from = data['form']['date_from']
#         date_to = data['form']['date_to']
#         hr_dept_id =  data['form']['hr_dept_id'][0]
#         res_appraisal = self.env['probationary.monitoring'].search([('appraisal_date','>=',date_from),('appraisal_date','<=',date_to),\
#                                                                     ('dept_id','=',hr_dept_id)])
#         probi_monitoring_res = self.with_context(data['form'].get('used_context'))._probi_monitoring(data)
 
 
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
        }
        
        print 'docargs', docargs
        return self.env['report'].render('muti_appraisal.rank_file_template', docargs) 
    
 
class ReportManagerialAppraisal(models.AbstractModel):
    _name = 'report.muti_appraisal.managerial_template'
    
#     def _probi_monitoring(self, data):
#         probi_res = {}
#         request = ("select id,name,description,hr_emp_id from probationary_monitoring group by hr_emp_id,name,description,id")
# 
#         self.env.cr.execute(request)
#         for row in self.env.cr.dictfetchall():
#             probi_res[row.pop('id')] = row
#         
#         return probi_res
    
    
    @api.multi
    def render_html(self, data):
        print 'managerial'
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        bulk = data['form']['bulk']
        if 'employee_id' in data['form']:
            if data['form']['employee_id']:
                employee_id = data['form']['employee_id'][0]
            else:
                employee_id = False
        else:
            employee_id = ''
        
        if 'report_id' in data['form']:
            if data['form']['report_id']:
                report_id =  data['form']['report_id'][0]
            else:
                report_id = False
        else:
            report_id = ''
        
        if 'company_id' in data['form']:
            if data['form']['company_id']:
                company_id = data['form']['company_id'][0]
            else:
                company_id = False
        else:
            company_id = ''
            
        if 'hr_dept_id' in data['form']:
            if data['form']['hr_dept_id']:
                hr_dept_id = data['form']['hr_dept_id'][0]
            else:
                hr_dept_id = False    
        else:
            hr_dept_id = '' 
        
        if 'job_id' in data['form']:
            if data['form']['job_id']:
                job_id = data['form']['job_id'][0]
            else:
                job_id = False
        else:
            job_id = '' 
        
        if 'rater_id' in data['form']:
            if data['form']['rater_id']:
                rater_id =  data['form']['rater_id'][0]
            else:
                rater_id = False
        else:
            rater_id = ''
        
        
#         date_from = data['form']['date_from']
#         date_to = data['form']['date_to']
#         hr_dept_id =  data['form']['hr_dept_id'][0]
#         res_appraisal = self.env['probationary.monitoring'].search([('appraisal_date','>=',date_from),('appraisal_date','<=',date_to),\
#                                                                     ('dept_id','=',hr_dept_id)])
#         probi_monitoring_res = self.with_context(data['form'].get('used_context'))._probi_monitoring(data)
 
 
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
        }
        
        print 'docargs', docargs
        return self.env['report'].render('muti_appraisal.managerial_template', docargs)      