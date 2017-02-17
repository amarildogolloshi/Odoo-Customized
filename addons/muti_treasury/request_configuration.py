from openerp import models, fields, api
from openerp.exceptions import ValidationError
import datetime as datetime
import time
from openerp import SUPERUSER_ID
from comm_methods import get_chain_job_ids, _get_dept_authority

class config_request_categ(models.Model):
    _name = 'config.request.categ'
    _order = 'name'
    
    active = fields.Boolean(string="Active",default="True")
    name = fields.Char(string="Name")
    desc = fields.Text(string="Description")

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The category name must be unique"),
    ]
    
    @api.model
    def create(self, vals):
        vals['name'] = vals['name'].upper().strip()
        res_id = super(config_request_categ, self).create(vals)
       
        return res_id
    
    @api.multi   
    def write(self, vals):
        
        if 'name' in vals:
            vals['name'] =  vals.get('name').upper().strip()
        
        res_id = super(config_request_categ, self).write(vals)
       
        return res_id    


        
class config_request_type(models.Model):
    _name = 'config.request.type'
    _order = 'name'
    
    active = fields.Boolean(string="Active",default="True")
    name = fields.Char(string="Name")
    desc = fields.Text(string="Description")

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The type name must be unique"),
    ]
    
    @api.model
    def create(self, vals):
        vals['name'] = vals['name'].upper().strip()
        res_id = super(config_request_type, self).create(vals)
       
        return res_id
    
    @api.multi   
    def write(self, vals):
        
        if 'name' in vals:
            vals['name'] =  vals.get('name').upper().strip()
        
        res_id = super(config_request_type, self).write(vals)
       
        return res_id 

class config_request_source(models.Model): 
    _name = 'config.request.source'
    _order = 'name'
    
    active = fields.Boolean(string="Active",default="True")
    name = fields.Char(string="Name")
    desc = fields.Text(string="Description")  
   
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The source name must be unique"),
    ]
    
    @api.model
    def create(self, vals):
        vals['name'] = vals['name'].upper().strip()
        res_id = super(config_request_source, self).create(vals)
       
        return res_id
    
    @api.multi   
    def write(self, vals):
        
        if 'name' in vals:
            vals['name'] =  vals.get('name').upper().strip()
        
        res_id = super(config_request_source, self).write(vals)
       
        return res_id 
    
    
class config_approval(models.Model):
    _name = 'config.approval'
    _order = 'department_level_id, department_id, request_categ_id'
    
    active = fields.Boolean(string="Active",default=True)
    name = fields.Char(string="Name")
    request_categ_id = fields.Many2one('config.request.categ', string="Request Category")
    department_level_id = fields.Many2one('config.department.level', string="Level")
    department_id = fields.Many2one('hr.department', string="Branch/Dept", help="Set to Blank if for ALL")
    approval_rule_ids = fields.Many2many('config.approval.rule','approval_rule_rel','approval_id','approval_rule_id',string="Approval")
    
    @api.onchange('request_categ_id','department_level_id', 'department_id') # if these fields are changed, call method
    def _get_name(self):
       for record in self.request_categ_id:

           department_level_id =  self.department_level_id.id
           department_id = self.department_id.id
           rec_id =  record.id
           if not rec_id:
                raise ValidationError("Please fill Request Category first") 
           request_categ_obj =  self.env['config.request.categ'].browse(rec_id)
           if department_level_id:
               department_level_obj = self.env['config.department.level'].browse(department_level_id)
               department_level = department_level_obj.name
           else:
               department_level = ''
           if department_id:
               department_obj = self.env['hr.department'].browse(department_id)
               department_name = department_obj.name
           else:
               department_name = ''
           request_categ =request_categ_obj.name
           
           self.name = request_categ  + department_level + department_name
           return record.name



class config_approval_rule(models.Model):
    _name = 'config.approval.rule'
    _order = 'request_source_id,request_type_id'
    
    active = fields.Boolean(string="Active", default=True)
    filter_type= fields.Char(string="Filter Type", related='approval_ids.name')
    name = fields.Char(string="Name", related="request_type_id.name")
    request_type_id = fields.Many2one('config.request.type', string="Request Type")
    request_source_id = fields.Many2one('config.request.source', string="Source of Fund")
    approval_chain_ids = fields.One2many('config.approval.chain','approval_rule_id', string="Approval Rule")   
    approval_id = fields.Many2one('config.approval', string="Approval")
    approval_ids = fields.Many2many('config.approval','approval_rule_rel','approval_rule_id','approval_id',string="Approval")

#     @api.multi
#     def name_get(self):
#   
#         res = super(config_approval_rule, self).name_get()
#         data = []
#         for r in self:
#             display_value = str(r.request_type_id.name) + '/' +str(r.request_source_id.name)
#             data.append((r.id, display_value))
#         return data

#     @api.multi
#     def write(self, vals):                
#             
#         res_id = super(config_approval_rule, self).write(vals)
#          
#         return res_id


class config_approval_chain(models.Model):
    _name = 'config.approval.chain'
    _order = 'priority'
    
    hr_job_id = fields.Many2one('hr.job', string="Authority")
    amount = fields.Float(string="Amount(if exceeds)", digits=(16,2))
    priority = fields.Integer(string="Priority")
    approval_rule_id = fields.Many2one('config.approval.rule', string="Approval Rule")
    
    @api.multi
    def write(self, vals):
        
        res_id = super(config_approval_chain, self).write(vals)       
        rule_id = self.approval_rule_id.id
        res_aprvl = self.env['config.approval'].search([('approval_rule_ids','=',rule_id),('active','=', True)])
        for rec_aprvl in res_aprvl:
            aprvl_obj = self.env['config.approval'].browse(rec_aprvl.id)
            level_id = aprvl_obj.department_level_id.id

            res_dept = self.env['hr.department'].search([('level_id','=',level_id)])
            dept_ids = []
            for rec_dept in res_dept:
                dept_ids.append(rec_dept.id)

            res_dept_aprvr = self.env['config.department.approver'].search([('hr_department_id','in',dept_ids)])
            
            get_dept_authority = _get_dept_authority(self,res_dept_aprvr,level_id)
            
#             for rec_dept_aprvr in res_dept_aprvr:
#                 dept_id = rec_dept_aprvr.hr_department_id.id
# 
#                 res_auth = self.env['config.authority.user'].search([('dept_approver_id','=',rec_dept_aprvr.id)])
# 
#                 exist_job_ids = []
#                 for rec_auth in res_auth:
#                     auth_obj = self.env['config.authority.user'].browse(rec_auth.id)
#                     hr_job = auth_obj.hr_job.id 
#                     exist_job_ids.append(hr_job)
# 
#                 job_ids = get_chain_job_ids(self, level_id, dept_id)
#  
#                 get_job = self.env['hr.job'].search(['&',('id','in',job_ids),'!',('id','in',exist_job_ids)])      
#             
#                 get_job_ids = self.env['hr.job'].search(['&',('id','in',exist_job_ids),'!',('id','in',job_ids)])   
#                 
#                 for rec in get_job_ids:
#                     self.env['config.authority.user'].search([('dept_approver_id','=',rec_dept_aprvr.id),('hr_job','=',rec.id)]).unlink() 
#                        
#                 for rec_job in get_job:
#                     self.env['config.authority.user'].create({'dept_approver_id':rec_dept_aprvr.id,'hr_job':rec_job.id})
                    
        return res_id
        
    

class config_iou_purpose(models.Model):
    _name = 'config.iou.purpose'
    
    active = fields.Boolean(string = "Active", default=True)
    name = fields.Char(string="Name")
    desc = fields.Text(string = "Description")
    

class bypass_activation(models.Model):
    _name = 'bypass.activation'
    

    
    def _get_user(self):
        user = self.env.user.id
        return user
    
    def _assigned_user(self):
        user = self.env.user.id      
        res_user_assigned = self.env['bypass.activation.history'].search([('user_id','=',user)], order='id desc' )               
        return res_user_assigned
    
    
    @api.model  
    def create(self, vals):
        user = self.env.user.id
        res = self.search([('user_id', '=', user)]).unlink()
        res_id = super(bypass_activation, self).create(vals)  
    
        return res_id
    
    user_id = fields.Many2one('res.users', string="User", default=_get_user)
    start_date = fields.Date(string="Start Date",default = lambda *a: time.strftime('%Y-%m-%d'))
    end_date = fields.Date(string="End Date",default = lambda *a: time.strftime('%Y-%m-%d'),)
    reason = fields.Text(string="Reason")
    assigned_user_ids = fields.Many2many('res.users', 'activation_user_rel' ,'activation_id', 'user_id', string="Assigned Users" )
    active = fields.Boolean(string="Active", default=True)
    
    @api.model   
    def bypass_activate(self):
        print 'bypass activation scheduler running'
        date_today = datetime.datetime.now().strftime("%Y-%m-%d")
        res_bypass_activation = self.search([('start_date','<=',date_today),('end_date','>=',date_today),
                                            ('active','=',True)])

        for rec in res_bypass_activation:
            get_assigned_users = rec.assigned_user_ids
            user = rec.user_id.id
            assigned_user_ids = []
            for user_id in get_assigned_users:
                assigned_user_ids.append(user_id.id)
            print ''  
            self.env['config.authority.user'].search([('user_id','=', user)]).write({'allow_bypass':True, 'allow_user_ids':[(6,0,[assigned_user_ids])]})
            self.get_activation_history(rec)

            
        bypass_activation_ids = []
        for rec in  res_bypass_activation:
              bypass_activation_ids.append(rec.id)
        res = self.search([('id','not in', bypass_activation_ids)])#.write({'allow_bypass':True, 'allow_user_ids':[(6,0,[assigned_user_ids])]})

        for rec in res:
            user_id = rec.user_id.id
            rec_auth_user = self.env['config.authority.user'].search([('user_id','=', user_id)])
            for rec in rec_auth_user:
                rec.allow_bypass = False
                rec.allow_user_ids = False
                            
        return True 

    def get_activation_history(self,rec_id):
        user_id = rec_id.user_id.id   
        start_date = rec_id.start_date
        end_date = rec_id.end_date
        reason = rec_id.reason
        assigned_user_ids = rec_id.assigned_user_ids
        user_ids = []
        for rec in assigned_user_ids:
            user_ids.append(rec.id)
        res_activate_history = self.env['bypass.activation.history'].search([('user_id','=', user_id),('start_date','=',start_date),('end_date','=',end_date),
                                                                             ('reason','=',reason)])

        user_equal = False
        for rec in res_activate_history:
            assigned_users_id = []
            get_assigned_users = rec.assigned_user_ids
            for rec_user in get_assigned_users:
                assigned_users_id.append(rec_user.id)
            if user_ids == assigned_users_id:
                user_equal = True
                    
        if not user_equal:   
                self.env['bypass.activation.history'].create({'start_date':start_date,'end_date':end_date,'reason':reason,
                                                      'user_id':user_id,'assigned_user_ids':[(6,0,user_ids)]})


        
    @api.onchange('user_id')
    def onchange_user_id(self):
        user = self.env.user.id
        res = self.search([('user_id','=', user)], order="id desc", limit = 1 )
        if res:
            self.start_date = res.start_date
            self.end_date = res.end_date
            self.assigned_user_ids = res.assigned_user_ids
            self.reason = res.reason
            self.active = res.active
        else:
            return None
            

        
    
class bypass_user_history(models.Model):
    _name = 'bypass.activation.history'    
    
    start_date = fields.Date(string="Start Date",default = lambda *a: time.strftime('%Y-%m-%d'))
    end_date = fields.Date(string="End Date",default = lambda *a: time.strftime('%Y-%m-%d'),)
    reason = fields.Text(string="Reason")
    user_id = fields.Many2one('res.users', string="User")
    assigned_user_ids = fields.Many2many('res.users', 'activation_history_user_rel' ,'history_id', 'user_id', string="Assigned Users" )

          
    

    
    
    
 
    