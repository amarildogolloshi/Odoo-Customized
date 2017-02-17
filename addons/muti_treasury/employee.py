from openerp import models, fields, api


class employee(models.Model):
    _inherit = 'hr.employee'
    
    hr_department_ids = fields.Many2many('hr.department','employee_dept_rel','employee_id', string = "Department")
    
    @api.model
    def create(self,vals):

        vals['hr_department_ids']= [(6, 0, [vals['department_id']])]
        
        res_id = super(employee,self).create(vals)
        
        return res_id
        