from openerp import models, fields, api
from datetime import datetime
from comm_methods import _get_branch_id, get_chain_job_ids,_get_dept_authority

class department(models.Model):
    _inherit = 'hr.department'
    
    level_id = fields.Many2one('config.department.level',string = 'Level')
    
#     @api.model
#     def create(self, vals):    
#         res_id = super(department, self).create(vals)
#         self.env['config.department.authority'].create({'hr_department_id':res_id.id})
#         return res_id
    
class config_department_level(models.Model):
    _name = 'config.department.level'
    _desc = 'Config Department Level'

    active = fields.Boolean(string="Active",default="True")    
    name = fields.Char(string="Name")
    desc = fields.Text(string="Description")
    hr_department_ids = fields.One2many('hr.department','level_id', string="Department")   

    _sql_constraints = [
        ('name_unique','UNIQUE(name)',"The Level name must be unique"),
    ]

    @api.model
    def create(self, vals):    
 
        res_id = super(config_department_level, self).create(vals)
        res_dept = self.env['hr.department'].search([('level_id','=',res_id.id)])
        for dept in res_dept:
            res_aprvr = self.env['config.department.approver'].search([('hr_department_id','=',dept.id)])
            if not res_aprvr:
                self.env['config.department.approver'].create({'hr_department_id':dept.id})
            
            res_asgn_code= self.env['config.assigned.code'].search([('department_id','=',dept.id)])
            if not res_asgn_code:
                self.env['config.assigned.code'].create({'department_id':dept.id})

               
        return res_id

    @api.multi
    def write(self, vals):
        
        res_id = super(config_department_level, self).write(vals)
        
        for dept in self.hr_department_ids:
            res_dept_aprv = self.env['config.department.approver'].search([('hr_department_id','=',dept.id)])
            if not res_dept_aprv:
                self.env['config.department.approver'].create({'hr_department_id':dept.id})
                
            res_asgn_code= self.env['config.assigned.code'].search([('department_id','=',dept.id)])
            if not res_asgn_code:
                self.env['config.assigned.code'].create({'department_id':dept.id})
                
        return res_id
    
class config_department_approver(models.Model):
    _name = 'config.department.approver'
    _desc = 'Config Department Approver'
    
    name = fields.Char(string="Name", related='hr_department_id.name')
    active = fields.Boolean(string = "Active", default=True)
    hr_department_id = fields.Many2one('hr.department', string="Department")
#     branch_id = fields.Many2one('config.', string="Branch", related="hr_department_id.branch_id")
    branch_id = fields.Many2one('res.company', string="Branch", related="hr_department_id.company_id")
    authority_user_id = fields.One2many('config.authority.user', 'dept_approver_id' , string="Authority")

    _sql_constraints = [
        ('department_unique','UNIQUE(hr_department_id)',"Department must be unique"),
    ]

    @api.model
    def create(self, vals):
        
        
        if vals.get('hr_department_id'):
            department_id = vals['hr_department_id']
            dept_obj = self.env['hr.department'].browse(department_id)
            level_id = dept_obj.level_id.id
#             branch_id = dept_obj.branch_id.id
            branch_id = dept_obj.company_id.id
            vals['branch_id'] = branch_id
                        
            job_ids = get_chain_job_ids(self, level_id, department_id)
                             
            res_id = super(config_department_approver, self).create(vals) 
             
            get_job_ids = self.env['hr.job'].search([('id','in',job_ids)])                                
            for rec_job in get_job_ids:
                self.env['config.authority.user'].create({'dept_approver_id':res_id.id,'hr_job':rec_job.id})
                 
         
            return res_id 
     
    @api.multi
    def write(self, vals):

        if 'hr_department_id' in vals:
            department_id = vals['hr_department_id']
        else:
            department_id = self.hr_department_id.id
        dept_obj = self.env['hr.department'].browse(department_id)
        level_id = dept_obj.level_id.id
#         branch_id = dept_obj.branch_id.id
        branch_id = dept_obj.company_id.id
        vals['branch_id'] = branch_id

        res_id = super(config_department_approver, self).write(vals)
        
        res_dept_aprvr = self.env['config.department.approver'].search([('hr_department_id','=',department_id)])
        
        get_dept_authority = _get_dept_authority(self,res_dept_aprvr,level_id)
             
        return res_id


#     @api.onchange('hr_department_id')
#     def get_branch(self):
#         print 'onchange'
#         department_id = self.hr_department_id.id
#         if department_id:
#             branch_id = _get_branch_id(self, department_id)
#             self.branch_id = branch_id

        


class config_authority_user(models.Model):
    _name = 'config.authority.user'
    _order = 'hr_job'
    _desc = 'Config Authority User'
    
    active =  fields.Boolean(string = "Active", default=True)
    dept_approver_id = fields.Many2one('config.department.approver', ondelete="cascade", string="Department")
    hr_job = fields.Many2one('hr.job', string="Authority")
    source_id = fields.Many2one('config.request.source',string="Source")
    user_id = fields.Many2one('res.users',string ="User")
    allow_bypass = fields.Boolean(string = "Allow Bypass", default=False)
    allow_user_ids = fields.Many2many('res.users','allow_user_rel','authority_user_id','user_id',string="Allowed User")
  
    _sql_constraints = [
        ('name_unique','UNIQUE(dept_approver_id,hr_job,source_id)',"Multiple Authority exist"),
    ]

    
class config_assigned_code(models.Model):
    _name = 'config.assigned.code'
    _order = 'bu_code,area_id,dept_code'
    _desc = 'Config Assigned Code'
    
    name =  fields.Char(string="Name", related="department_id.name")
    active = fields.Boolean(string = "Active", default=True)
    department_id = fields.Many2one('hr.department', string="Department")
#     branch_id = fields.Many2one('config.branch', string="Branch")
    company_id = fields.Many2one('res.company', string="Branch")
    bu_code = fields.Char(string="Bu Code")
    area_id = fields.Char(string="Area")
    dept_code = fields.Char(string="Dept Code") 

#     _sql_constraints = [
#         ('code_unique','UNIQUE(bu_code,area_id,dept_code)',"The assigned code must be unique"),
#     ]
    
    @api.model
    def create(self, vals):
        department_id = vals['department_id']
        if department_id:
            branch_id = _get_branch_id(self, department_id)
            vals['company_id'] = branch_id
            comp_obj = self.env['res.company'].browse(vals['company_id'])
            area_id = comp_obj.area_id.id
            if not area_id:
                area_id = ''   
            bu_code = comp_obj.parent_id.code  
            if not bu_code:
                bu_code = ''
            if 'dept_code' in vals:
                dept_code = vals['dept_code']
            else:
                dept_code =''            
           
            today = datetime.today()
            current_year = today.year
            year =str(current_year)[-2:]
            series_prefix = str(year) + '-' + str(bu_code) + '-' + str(area_id) + '-' + str(dept_code) 
            res_req_series = self.env['config.request.series'].search([('department_id','=',department_id)])
            if not res_req_series:
                self.env['config.request.series'].create({'department_id':department_id,'prefix':series_prefix})
            else:
                self.env['config.request.series'].search([('department_id','=',department_id)]).write({'prefix':series_prefix})
                
            vals['area_id'] = area_id
            vals['bu_code'] = bu_code
            
            
        res_id = super(config_assigned_code, self).create(vals) 
        return res_id


    @api.multi
    def write(self, vals):
        
        if 'department_id' in vals:
            dept_id =  vals['department_id']
        else:
            dept_id = self.department_id.id
        
        branch_id = _get_branch_id(self, dept_id)
        vals['company_id'] = branch_id
        comp_obj = self.env['res.company'].browse(vals['company_id'])
        if 'area_id' in vals:
            area_id = vals['area_id']
        else:
            area_id = self.area_id
        if not area_id:
            area_id = ''   
        if 'bu_code' in vals:    
            bu_code = vals['bu_code']
        else:
            bu_code = self.bu_code
        if not bu_code:
            bu_code = ''  
        if not bu_code:
            bu_code = ''
        if 'dept_code' in vals:
            dept_code = vals['dept_code']
        else:
            dept_code = self.dept_code
        if not dept_code:
            dept_code =''    
        today = datetime.today()
        current_year = today.year
        year =str(current_year)[-2:]
        
        series_prefix = str(year) + '-' + str(bu_code) + '-' + str(area_id) + '-' + str(dept_code) 
        res_req_series = self.env['config.request.series'].search([('department_id','=',dept_id)])
        if not res_req_series:
            self.env['config.request.series'].create({'department_id':dept_id,'prefix':series_prefix})
        else:
            self.env['config.request.series'].search([('department_id','=',dept_id)]).write({'prefix':series_prefix})
         
        vals['area_id'] = area_id
        vals['bu_code'] = bu_code
               
        res_id = super(config_assigned_code, self).write(vals) 
        return res_id
    
    @api.onchange('department_id')
    def onchange_department(self):
        if self.department_id:
            department_id = self.department_id.id
            branch_id = _get_branch_id(self, department_id)

            comp_obj = self.env['res.company'].browse(branch_id)
            area_id = comp_obj.area_id.id
            bu_code = comp_obj.parent_id.code
            
            self.bu_code = bu_code
            self.company_id = branch_id
            self.area_id = area_id
            

class config_request_series(models.Model):
    _name = 'config.request.series'
    _desc = 'Config Request Series'
    
    active = fields.Boolean('Active', default=True)
    name = fields.Char(string="Name")
    department_id = fields.Many2one('hr.department', string="Department")
    company_id = fields.Many2one('res.company', string="Company", related='department_id.company_id')
    length_series = fields.Integer(string="Length Series", size=2)
    prefix = fields.Char(string="Prefix", size=64)
    nxt_number = fields.Integer(string="Next Number")
    number_increment = fields.Integer(string="Increment", default=1)
    sequence = fields.Char(string="Sequence")


    @api.model
    def create(self, vals):
        if 'prefix' in vals:
            prefix = vals['prefix']
        else:
            prefix = ''
        if 'nxt_number' in vals:
            nxt_no = vals['nxt_number']
        else:
            nxt_no = ''        
            
        sequence = prefix + '-' + str(nxt_no).zfill(5)
        vals['sequence'] = sequence
        
        res_id = super(config_request_series, self).create(vals) 
        return res_id
        

    @api.multi
    def write(self, vals):
        if 'prefix' in vals:
            prefix = vals['prefix']
        else:
            prefix = self.prefix
        if not prefix:
            prefix = ''
        
        if 'nxt_number' in vals:
            nxt_no = vals['nxt_number']
        else:
            nxt_no = self.nxt_number
        if not nxt_no:
            nxt_no = ''
        
        sequence = prefix + '-' + str(nxt_no).zfill(5)
        vals['sequence'] = sequence
        
        res_id = super(config_request_series, self).write(vals) 
        return res_id
        

    @api.multi
    def name_get(self):
   
        res = super(config_request_series, self).name_get()
        data = []
        for r in self:
            display_value = str(r.department_id.name) + '/' +str(r.department_id.company_id.name)
            data.append((r.id, display_value))
        return data   
    
    
    def get_sequence(self, dept_id):
        
        res = self.search([('department_id', '=', dept_id)])
        get_obj = self.browse(res.id)
        sequence = get_obj.sequence
        no_incrmnt = get_obj.number_increment
        nxt_no = get_obj.nxt_number
        if sequence:
            nxt_sequence = sequence + str(no_incrmnt)
            nxt_number = nxt_no + no_incrmnt
            self.search([('department_id', '=', dept_id)]).write({'sequence':nxt_sequence,'nxt_number':nxt_number})
            
        return sequence
        
        
        


        
            
            