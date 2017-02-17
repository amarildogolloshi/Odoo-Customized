from openerp import models, fields, api
 
 
class ReportProbationaryMonitoring(models.AbstractModel):
    _name = 'report.muti_appraisal.probationary_monitoring_template'
    
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
        rep_option = data['form']['rep_option']
        date_as_of = data['form']['date_as_of']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        if 'company_id' in data['form']:
            if data['form']['company_id']:
                print 'company_id',  data['form']['company_id']
                company_id = data['form']['company_id'][0]
            else:
                company_id = False
        else:
            company_id = False
        
        if 'hr_dept_id' in data['form']:
            if data['form']['hr_dept_id']:
                print 'hr_dept_id',  data['form']['hr_dept_id']
                hr_dept_id = data['form']['hr_dept_id'][0]
            else:
                hr_dept_id = False
        else:
            hr_dept_id = False
        
        if company_id:
            search_company = ('company_id','child_of',company_id)
        else:
            search_company = ('company_id','!=',False)
        
        if hr_dept_id:
            search_dept = ('dept_id','=',hr_dept_id)
        else:
            search_dept = ('dept_id','!=',False)        
        
        if date_as_of == 'range':
            aprsl_args = [('appraisal_date','>=',date_from),
                      ('appraisal_date','<=',date_to),
                      search_company,search_dept,
                      ('state','not in',['fin'])]
        else:
            aprsl_args = [('appraisal_date','<=',date_as_of),
                      search_company,search_dept,
                      ('state','not in',['fin'])]
        
        res_appraisal = self.env['probationary.monitoring'].search(aprsl_args)
#         probi_monitoring_res = self.with_context(data['form'].get('used_context'))._probi_monitoring(data)


        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'appraisal_ids': res_appraisal,
        }
        
        return self.env['report'].render('muti_appraisal.probationary_monitoring_template', docargs)       