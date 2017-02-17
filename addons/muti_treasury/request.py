from openerp import models, fields, api
from openerp.tools import openerp,image_colorize, image_resize_image_big
from datetime import datetime
from openerp.exceptions import ValidationError
from openerp import SUPERUSER_ID
from comm_methods import _get_allowed_company,get_authority, _get_current_date, _get_employee_id, _get_emp_dept, _get_to_approve_by

class request(models.Model):
    _name = 'request.request'
    _desc = 'Request'
    _order = 'request_date desc'

    
    def _get_default_filter_request_type(self):
        if 'search_default' in self.env.context:
            search_default =  self.env.context['search_default']
            user_id = self.env.user.id
            username = self.env.user.name
            if user_id != SUPERUSER_ID:
                res_resource = self.env['resource.resource'].search([('user_id','=',user_id)])
                resource_id = res_resource.id
                res_employee = self.env['hr.employee'].search([('resource_id','=',resource_id)])
                department_id = res_employee.department_id.id
                if department_id:
                    department_obj = self.env['hr.department'].browse(department_id)
                    department_level_id = department_obj.level_id.id
                    department_level_obj = self.env['config.department.level'].browse(department_level_id)
    
                    res_approval = self.env['config.approval'].search([('department_id','=',department_id)])
                    if res_approval:
                        department_name =  department_obj.name
                    else:
                        department_name = ''  
                    if not department_level_obj:
                        raise ValidationError("No Level Defined. Consult Developer")           
                    filter_request_type = search_default + department_level_obj.name + department_name 
                    return filter_request_type
                
    def _get_default_company(self):
        user_id = self.env.user.id
        res_company = self.env['res.users'].browse(user_id)
        company_ids =  res_company.company_ids
        company = []
        for comp in company_ids:
            company.append(comp.id)
        return company[0]               
                    
   
    def _search(self, cr, uid, args, offset=0, limit=None, order=None,
        context={}, count=False, access_rights_uid=None):
        user = uid
        if context:
            if 'action_default' in context and user != SUPERUSER_ID:
                res_resource = self.pool.get('resource.resource').search(cr,uid,[('user_id','=',uid)])
                if res_resource:
                    resource_id = res_resource
                    res_employee = self.pool.get('hr.employee').search(cr,uid,[('resource_id','=',resource_id)])
                    employee_obj = self.pool.get('hr.employee').browse(cr, uid,res_employee)
                    department_id =  employee_obj.department_id.id
                    
                    user_obj = self.pool.get('res.users').browse(cr, uid, uid)
                    company_id = user_obj.company_id.id
                   
                    if not department_id:
                        return None
                                        
                    if context['action_default'] == 'myrequest':
                        args.append(("create_uid","=",uid))
                        args.append(("company_id","=",company_id))
                    if context['action_default'] == 'branchdept':
                        args.append(("create_uid","!=",uid))
                        args.append(("department_id","=",department_id))
                    if context['action_default'] == 'other':
                        args.append(("create_uid","!=",uid))
                        args.append(("request_through","=",department_id))

                    return super(request, self)._search(cr, uid, args, offset=offset, limit=limit, order=order,
                                                context=context, count=count, access_rights_uid=access_rights_uid)
            else:
                return super(request, self)._search(cr, uid, args, offset=offset, limit=limit, order=order,
                                            context=context, count=count, access_rights_uid=access_rights_uid)
         
    def _get_all_department(self): 
        res = []
        
        level_ids = []
        res_level = self.env['config.department.level'].search([('active','=',True)])
        for level in res_level:
            level_ids.append(level.id) 
        res_dept = self.env(user=SUPERUSER_ID)['hr.department'].search([('active','=',True)])
        for rec_dept in res_dept:
            dept_name = rec_dept.name + ' / ' + rec_dept.company_id.name
            res.append((str(rec_dept.id),dept_name))
            
        return res   
     
    @api.depends('request_det_ids')                           
    def _amount_all(self):
           for rec in self:
                total_amt =  0.0
                for det in rec.request_det_ids:
                    total_amt += det.amount
               
                rec.update({
                    'total_amount': total_amt,
                    
                })    
    
    @api.model
    def _get_default_image(self, colorize=False):
        
#         image = image_colorize(open(openerp.modules.get_module_resource('muti_base','static/src/img', 'msg_logo.png')).read())
#         image_resize_image_big(image.encode('base64'))
        company_logo = self.env.user.company_id.logo
        return image_resize_image_big(company_logo)
    
    name = fields.Char(string="Name", related='request_no')   
    hr_employee_id = fields.Many2one('hr.employee',string="Requestor", default=_get_employee_id)
    request_no = fields.Char(string="Request No", size=50)
    department_id  = fields.Many2one('hr.department','Branch')
    request_through = fields.Selection('_get_all_department',string="Request Through")
    request_date = fields.Datetime(string="Request Date", default=_get_current_date)
    purpose = fields.Text(string="Purpose")
    iou_purpose = fields.Many2one('config.iou.purpose',string="Purpose")
    iou_loan_amt = fields.Float(string="Loan Amount", digits=(16,2))
    instruction = fields.Text(string="Special Instructions")
    source_id = fields.Many2one('config.request.source',string="Source", store=True)
    request_categ_id = fields.Many2one('config.request.categ',string="Request Category", store=True)
    request_type_id = fields.Many2one('config.approval.rule',string="Request Type")
    request_det_ids = fields.One2many('request.det', 'request_id', string="Request")
    request_approval_ids = fields.One2many('request.approval', 'request_id', string="Request")
    request_history_ids = fields.One2many('request.history', 'request_id', string="History")
    remark = fields.Text(string="Remarks")
    filter_request_type = fields.Char(string="Filter Request Type")
    to_approve_by  = fields.Many2many('res.users','request_approver_rel','request_id','user_id', string= "To Approve By")
    color = fields.Integer()
    company_id = fields.Many2one('res.company', string="Company", default=_get_default_company)
    btn_msg = fields.Char(string="Button Message")
    prnt_ctr = fields.Integer(string="Print Count")
    readonly_req_det = fields.Boolean(string="Readonly", default=True)
    recipients = fields.Char(string="Recipients")
    total_amount = fields.Float(string="Total Amount", digits=(16,2), compute='_amount_all')   
    image = fields.Binary("Photo",  default=lambda self:self._get_default_image(),
        help="This field holds the image used as photo for the company, limited to 1024x1024px.")
    image_medium = fields.Binary("Medium-sized photo", attachment=True,
        help="Medium-sized photo of the company. It is automatically "\
             "resized as a 128x128px image, with aspect ratio preserved. "\
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized photo", attachment=True,
        help="Small-sized photo of the company. It is automatically "\
             "resized as a 64x64px image, with aspect ratio preserved. "\
             "Use this field anywhere a small image is required.")    
    state = fields.Selection([('draft','Draft'),
                              ('confirm','To Be Approved'),
                              ('approve','Approved'),
                              ('disapprove','Disapproved'),
                              ('void','Void'),
                              ],
                             string="Status", default='draft')
    
    defaults = {
        'image': _get_default_image,
    }
    
    
    @api.multi
    def print_report(self, data):
        
        user_id = self.env.user.id
        create_uid = self.create_uid.id
        prnt_ctr = self.prnt_ctr
        
        if prnt_ctr >= 1:
            raise ValidationError("Document has already been PRINTED. Can print only ONCE")
        
        if user_id != create_uid:
            raise ValidationError("Sorry, you have no permission to use this button.")
        
        if self.state == 'approve':
#             self.prnt_ctr += 1
            return self.env['report'].sudo().get_action(self, 'muti_treasury.report_request_view')
                      
       
        
    @api.model
    def create(self, vals):
        type_id = vals['request_type_id']
        if 'search_default' in self.env.context:
                request_categ_name =  self.env.context['search_default']
                department_id  = vals['department_id']
                department_obj= self.env['hr.department'].browse(department_id)
                department_name = department_obj.name
                if department_id:  
                    sequence = self.env['config.request.series'].get_sequence(department_id)              
                else:
                    raise ValidationError("No Assigned Request No. Please consult Admin")
                
                approval_rule_obj =  self.env['config.approval.rule'].browse(type_id)
                name = vals['filter_request_type'] 
                rec_config_approval = self.env['config.approval'].search([('name', '=', name)])
                request_categ_id = rec_config_approval.request_categ_id.id
                source_id = approval_rule_obj.request_source_id.id
                vals['request_categ_id'] = request_categ_id
                vals['source_id'] = source_id
                vals['request_no'] = sequence
                            
                res_id = super(request, self).create(vals)   
                rec_id = res_id.id                 
                res_request_det = self.env['request.det'].search([('request_id','=', res_id.id)])
                amt =0
                for rec in res_request_det:
                    rec_det = self.env['request.det'].browse(rec.id)
                    amount = rec_det.amount
                    amt = amt +amount
                        
                if amt>0:
                    res_authority = self.env['config.approval.chain'].search([('approval_rule_id','=', type_id)],order = 'priority asc')
                
                    authority = get_authority(self,res_authority,type_id, amt,rec_id,department_id,source_id) 
                return res_id 

    @api.multi  
    def write(self, vals):
        rec_id = self.id
        if 'request_type_id' in vals:
           request_type_id =  vals['request_type_id']
        else:
            request_type_id = self.request_type_id.id
        if 'filter_request_type' in vals:
            name = vals['filter_request_type']
        else:
            name = self.filter_request_type
        if 'request_through' in vals:
            through = vals['request_through']
        else:
            through = self.request_through
            
        dept_id = self.department_id.id 
        approval_rule_obj =  self.env['config.approval.rule'].browse(request_type_id)
        dept_obj = self.env(user=SUPERUSER_ID)['hr.department'].browse(int(through))
        branch_id = dept_obj.company_id.id
        company_obj = self.env['res.company'].browse(branch_id)
        company_id = company_obj.id  
        rec_config_approval = self.env['config.approval'].search([('name', '=', name)])
        request_categ_id = rec_config_approval.request_categ_id.id
        source_id = approval_rule_obj.request_source_id.id
        vals['request_categ_id'] = request_categ_id
        vals['source_id'] = source_id             
        
        res_id = super(request, self).write(vals)
        res_request_det = self.env['request.det'].search([('request_id','=', rec_id)])
        amt =0
        for rec in res_request_det:
            rec_det = self.env['request.det'].browse(rec.id)
            amount = rec_det.amount
            amt = amt +amount   
        
        if self.state == 'draft':
            if amt>0:
                res_authority = self.env['config.approval.chain'].search([('approval_rule_id','=', request_type_id)],order = 'priority asc')
                authority = get_authority(self,res_authority,request_type_id, amt,rec_id,dept_id,source_id) 
                

        return res_id 


    @api.onchange('company_id') 
    def _onchange_company_id(self):
        
        company_id =  self.company_id.id
        employee_id = _get_employee_id(self)
        emp_obj = self.env['hr.employee'].browse(employee_id)
        allow_dept_ids = emp_obj.hr_department_ids   
        
        get_dept = []
        for rec_dept in allow_dept_ids:
            dept  = rec_dept.id 
            comp_id = rec_dept.company_id.parent_id.id
            if company_id == comp_id:
                get_dept.append(dept)        
        
        if not get_dept:
            raise ValidationError("No Allowed Department Assigned. Please consult Administrator")
         
        self.department_id = get_dept[0]
#request_through        
        level_ids = []
        res_level = self.env['config.department.level'].search([('active','=',True)])
        for level in res_level:
            level_ids.append(level.id) 
            
#         res_dept = self.env(user=SUPERUSER_ID)['hr.department'].search([('active','=',True),('level_id','in',level_ids)])
        res_dept = self.env(user=SUPERUSER_ID)['hr.department'].search([('active','=',True)])
        res = []
        for rec_dept in res_dept:
            dept_name = rec_dept.name + ' / ' + rec_dept.company_id.name
            res.append((str(rec_dept.id),dept_name))
        
        return {'domain':{'department_id':[('id','in',get_dept)]},
                'request_through':res
                }

        
    @api.onchange('request_type_id') 
    def _onchange_request_type_id(self):
        for rec in self:
            if rec.request_type_id.id:
                request_type_id = rec.request_type_id.id
                approval_rule_obj =  self.env['config.approval.rule'].browse(request_type_id)
                request_categ_id = approval_rule_obj.approval_ids
                filter_request_type = self.filter_request_type
                name =  filter_request_type 
                rec_config_approval = self.env['config.approval'].search([('name', '=', name)])
                request_categ_id = rec_config_approval.request_categ_id.id
                source_id = approval_rule_obj.request_source_id.id
                self.request_categ_id = request_categ_id
                self.source_id = source_id
     
    @api.onchange('hr_employee_id')
    def _onchange_hr_employee_id(self):
        user_id = self.env.user.id
        res_company = self.env['res.users'].browse(user_id)
        company_ids =  res_company.company_ids
        company = []
        for comp in company_ids:
            company.append(comp.id)
            
            
        return {'domain':{'company_id':[('id','in',company)]},
                }
        
    @api.onchange('department_id')
    def _onchange_hr_department(self):
        search_default = self.env.context['search_default']
        dept_id = self.department_id.id
        dept_obj = self.env['hr.department'].browse(dept_id)
        dept_level_id = dept_obj.level_id.id
        dept_level_obj = self.env['config.department.level'].browse(dept_level_id)
 
        res_aprvl = self.env['config.approval'].search([('department_id','=',dept_id)])
        if res_aprvl:
            dept_name =  dept_obj.name
        else:
            dept_name = ''
               
        if not dept_level_obj:
            raise ValidationError("No Level Defined. Consult Developer")           
        filter_request_type = search_default + dept_level_obj.name + dept_name 
        self.filter_request_type = filter_request_type
        return {'domain':{'request_type_id':[('approval_ids','=',filter_request_type)]},
                }
    
    @api.multi
    def action_draft(self):
        self.remark = ''
        user_id = self.env.user.id
        create_uid = self.create_uid.id
        to_approve_by = []
        to_aprv_by = []
               
        for aprvr_id in self.sudo().to_approve_by:
            to_aprv_by.append(aprvr_id.id)
        
        if user_id in to_aprv_by:
            self.readonly_req_det = True
        elif user_id == create_uid:
            res_aprvl = self.env['request.approval'].search([('request_id','=',self.id),('approved','=',True)])
            if not res_aprvl: 
                self.state = 'draft'
                self.btn_msg = False
                self.to_approve_by = False
                self.readonly_req_det = True
                self.recipients = to_approve_by
                res_req_aprvl = self.env['request.approval'].search([('request_id','=',self.id)]).write({'approved':False})
                self.env['request.history'].create({'request_id':self.id,'user_id':user_id,'desc':'Reset to Draft'})
            else:
                raise ValidationError("Sorry, you have no permission to use this button.\n"+ 
                                     "Request has already been approved by one of the Approvers")
        else:
            raise ValidationError("Sorry, you have no permission to use this button.")
        

    @api.multi
    def action_confirm_msg_a(self):
        user_id = self.env.user.id
        rec_user_id = self.create_uid.id
        if user_id == rec_user_id:
            self.btn_msg = 'confirm_msg_a'
        else:
            raise ValidationError("Sorry, you have no permission to use this button.")
        
        
        
#     @api.multi
#     def action_confirm_msg_b(self):
#         user_id = self.env.user.id
#         rec_user_id = self.create_uid.id
#         if user_id == rec_user_id:
#             self.btn_msg = 'confirm_msg_b'
#         else:
#             raise ValidationError("Sorry, you have no permission to use this button.")        
       
    @api.multi
    def action_confirm(self):
        user_id = self.env.user.id
        rec_user_id = self.create_uid.id
        rf_no = self.request_no
        requestor = self.hr_employee_id.id
        type_id = self.request_type_id.id
        source_id = self.source_id.id
        if user_id == rec_user_id:
            user_id = self.env.user.id
            dept_id = self.department_id.id
            
#             res_request_det = self.env['request.det'].search([('request_id','=', self.id)])
#             amt =0
#             for rec in res_request_det:
#                 rec_det = self.env['request.det'].browse(rec.id)
#                 amount = rec_det.amount
#                 amt = amt +amount
#                     
#             if amt>0:
#                 res_authority = self.env['config.approval.chain'].search([('approval_rule_id','=', type_id)],order = 'priority asc')
#                 print 'res_authority', res_authority
#                 authority = get_authority(self,res_authority,type_id, amt,self.id,dept_id,source_id) 
#                 print 'authority', authority
                
            res_request_approval = self.env['request.approval'].search([('request_id','=',self.id),('approved','=',False)], limit =1)
            _get_to_approve_by(self,dept_id,res_request_approval)  

            
            self.state = 'confirm'
            self.btn_msg = 'confirm'      
            self.remark = ''
#SEND EMAIL
#             template_id = self.env.ref('muti_treasury.email_template_rfp')
#             self.env['mail.template'].browse(template_id.id).send_mail(self.id, force_send=True)            
            
            self.env['request.history'].create({'request_id':self.id,'user_id':user_id,'desc':'Confirm'})
            self.readonly_req_det = False
        else:
            raise ValidationError("Sorry, you have no permission to use this button.")     
        
    @api.multi
    def action_void(self):
        user_id = self.env.user.id
        self.state = 'void'
        self.btn_msg = 'void'
        self.env['request.history'].create({'request_id':self.id,'user_id':user_id,'desc':'Void'})

    @api.multi    
    def action_approve_msg_a(self):
        user_id = self.env.user.id
        to_aprve_by = self.sudo().to_approve_by
        to_aprve_by_ids = []
        for aprv_id in to_aprve_by:
            to_aprve_by_ids.append(aprv_id.id)
        for rec in to_aprve_by:
            if user_id in to_aprve_by_ids:
                self.btn_msg = 'approve_msg_a'
            else:
                raise ValidationError("Sorry, you have no permission to use this button.") 

#     @api.multi    
#     def action_approve_msg_b(self):
#         user_id = self.env.user.id
#         to_aprve_by = self.to_approve_by
#         to_aprve_by_ids = []
#         for rec in to_aprve_by:
#             if user_id == rec.id:
#                 self.btn_msg = 'approve_msg_b'
#             else:
#                 raise ValidationError("Sorry, you have no permission to use this button.")
        
    @api.multi    
    def action_approve(self):
        user_id = self.env.user.id
        to_aprve_by = self.sudo().to_approve_by
        to_aprve_by_ids = []
        for aprv_id in to_aprve_by:
            to_aprve_by_ids.append(aprv_id.id)
            
        if user_id in to_aprve_by_ids:
            user_id = self.env.user.id
            res_req_det = self.env['request.approval'].search([('request_id','=',self.id),('approved','=',False)], order = 'id asc', limit=1)
            if res_req_det:
                res_req_det.write({'approved':True})
                self.readonly_req_det = False
                self.btn_msg = 'approve_msg_a'
                res_req_aprvl = self.env['request.approval'].search([('request_id','=',self.id),('approved','=',False)], limit =1)
                if not res_req_aprvl:   
                    self.state = 'approve'
                    self.btn_msg = 'approve'
                    self.sudo().to_approve_by = False
                    self.remark = ''
                                    
                dept_id = self.department_id.id
                to_approve_by = _get_to_approve_by(self,dept_id,res_req_aprvl)  
                if to_approve_by:
                    self.sudo().write({'to_approve_by':[(6,0,[to_approve_by])]}) 
                                        
                self.env['request.history'].create({'request_id':self.id,'user_id':user_id,'desc':'Approve'})
        else:
            raise ValidationError("Sorry, you have no permission to use this button.")   
            
#     @api.multi
#     def action_review(self):
#         user_id = self.env.user.id
#         dept_id = self.department_id.id
#         res_request_approval = self.env['request.approval'].search([('request_id','=',self.id),('approved','=',True)],order='id desc', limit =1)
#         if res_request_approval:
#             to_approve_by = _get_to_approve_by(self,dept_id,res_request_approval)
#             res_request_approval.write({'approved':False})
#             self.state = 'review'
#             self.remark = ''
#             
#         else:
#             self.state = 'draft' 
#             self.remark = ''     
#         self.env['request.history'].create({'request_id':self.id,'user_id':user_id,'desc':'For Review'})
        
    @api.multi    
    def action_disapprove(self):
        user_id = self.env.user.id
        to_aprve_by = self.sudo().to_approve_by
        to_aprve_by_ids = []
        for rec in to_aprve_by:
            if user_id == rec.id:
                self.state = 'disapprove'
                self.sudo().to_approve_by = False
                self.btn_msg = 'disapprove'
                self.env['request.history'].create({'request_id':self.id,'user_id':user_id,'desc':'Disapprove'})  
                self.remark = ''
                
            else:
                raise ValidationError("Sorry, you have no permission to use this button.")   
    
    @api.multi    
    def action_edit(self):
        user_id = self.env.user.id
        to_approve_by = self.sudo().to_approve_by
        for aprvr_id in to_approve_by:
            if user_id == aprvr_id.id:
                self.readonly_req_det = True
            else:
                self.readonly_req_det = False
                raise ValidationError("Sorry, you have no permission to use this button.")
            
        
#         self.readonly_req_det = True   
                                 
class request_det(models.Model):
    _name = 'request.det'
    _desc = 'Request Detail'
    _order = 'id'
    
    request_id = fields.Many2one('request.request',ondelete='cascade', string="Request")
    unit = fields.Char('Unit')
    qty = fields.Float(string="Quantity",digits=(16, 2))
    account = fields.Char(string="Account", size=300)
    particulars = fields.Char(string="Particulars", size = 50)
    price = fields.Float(string="Price", digits=(16, 2))
    amount = fields.Float(string="Amount", digits=(16, 2), compute ='_get_amount')
    vendor = fields.Many2one('res.partner', string="Vendor/Supplier")
    total = fields.Float(string="Total amount", digits=(16,2))
    term = fields.Char(string="Term", size=100)

       
    @api.onchange('qty', 'price')
    def _get_amount(self):
        for r in self:
            r.amount = r.qty * r.price

            

class request_approval(models.Model):
    _name = 'request.approval'
    _desc = 'Request Approval'
    
    hr_job_id = fields.Many2one('hr.job', string="Authority")
    user_id = fields.Many2one('res.users', string="Approver")
    allowed_user_ids =fields.Many2many('res.users', 'req_aprvl_user_rel', 'req_aprvl_id', 'user_id' ,string="Sub-Approvers") 
    request_id = fields.Many2one('request.request',ondelete='cascade', string="Request")
    approved = fields.Boolean(string="Approved", default=False)
           

class request_history(models.Model):
    _name = 'request.history'
    _desc = 'Request History'
         
    date = fields.Datetime(string="Date", default=_get_current_date)
    user_id = fields.Many2one('res.users', string ="User")
    desc = fields.Text(string="Description")
    request_id = fields.Many2one('request.request',ondelete='cascade', string="Request")

 
    
        
    