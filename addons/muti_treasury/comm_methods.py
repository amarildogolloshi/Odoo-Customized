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

def _get_employee_id(self):
    user_id = self.env.user.id
    res_resource = self.env['resource.resource'].search([('user_id','=',user_id)])
    if not res_resource and user_id !=1:
       raise ValidationError("No related employee assigned to current user. Please consult System Admin")
    else:
        resource_id = res_resource.id
        res_employee = self.env['hr.employee'].search([('resource_id','=',resource_id)])
        employee_id  = res_employee.id
        return employee_id


def _get_emp_dept(self):
    user_id = self.env.user.id
    res_resource = self.env['resource.resource'].search([('user_id','=',user_id)])
    if res_resource:
        resource_id = res_resource.id
        res_employee = self.env['hr.employee'].search([('resource_id','=',resource_id)])
#         department_id  = res_employee.department_id.id
        dept_id = res_employee.department_id.id 
        return  dept_id

def _get_branch_id(self, department_id):
    dept_obj = self.env['hr.department'].browse(department_id)
    branch_id = dept_obj.company_id.id
    
    return branch_id

def _get_current_date(self):
    today = datetime.today()
    return today

def _get_authority_user(self, dept_id, source_id, job_id, job_ids, create_uid):
    res_dept_approver = self.env['config.department.approver'].search([('hr_department_id','=',dept_id)])
    dept_approver_id = res_dept_approver.id
    validate_user =  self.env['config.authority.user'].search([('dept_approver_id','=',dept_approver_id),('hr_job','in',job_ids),('user_id','=',False)]) 
    get_job = ''
    for user in validate_user:
        job_name = user.sudo().hr_job.name
        get_job = job_name + ' , ' + get_job
    if validate_user:
        raise ValidationError("Configuration Error. No User Assigned to '%s'. PLease Consult Admin"% (get_job)) 
    else:
        res_authority_user = self.env['config.authority.user'].search([('dept_approver_id','=',dept_approver_id),('hr_job','=',job_id),('user_id','!=',create_uid)]) 
        if len(res_authority_user)>1:
            res_authority_user = self.env['config.authority.user'].search([('dept_approver_id','=',dept_approver_id),('hr_job','=',job_id),('source_id','=',source_id),('user_id','!=',create_uid)])
            if not   res_authority_user:
                job_obj = self.env(user=SUPERUSER_ID)['hr.job'].browse(job_id)
                job_name = job_obj.name
                source_obj = self.env['config.request.source'].browse(source_id)
                source_name = source_obj.name
                raise ValidationError("Configuration Error. No User Assigned to Job '%s' w/ Source '%s'. PLease Consult Admin"% (job_name,source_name))       
        return res_authority_user

def get_authority(self,res_authority,type_id, amnt,rec_id,dept_id,source_id):
    uid = self.env.user.id
    create_uid = self.create_uid.id
    if not create_uid:
        create_uid = uid
    
# start -- get Job Ids, User Ids, Allowed User Ids in Request Aproval -- start     
    req_aprvl_job_ids = []
    req_aprvl_user_ids = []
    req_aprvl_alwd_usr_ids = []
    res_req_aprvl = self.env['request.approval'].search([('request_id', '=', rec_id)])
    for get_req_aprvl in res_req_aprvl:
        req_aprvl_obj = self.env['request.approval'].browse(get_req_aprvl.id)
        hr_job_id = req_aprvl_obj.hr_job_id
        user_id = req_aprvl_obj.user_id.id
        alwd_usr_ids = req_aprvl_obj.allowed_user_ids
        req_aprvl_job_ids.append(hr_job_id.id) 
        req_aprvl_user_ids.append(user_id)  
        req_aprvl_alwd_usr_ids.append(alwd_usr_ids)    
# end -- get Job Ids, User Ids, Allowed User Ids in Request Aproval -- end  


# start -- get Job Ids in Config Approval Chain -- start  
    aprvl_chain_job_ids = [] 
    for rec in res_authority:
        aprvl_chain_obj = self.env['config.approval.chain'].browse(rec.id)
        amount = aprvl_chain_obj.amount
        if amount == 0 or amnt > amount:
            job_id = aprvl_chain_obj.hr_job_id.id
            aprvl_chain_job_ids.append(job_id)
# end -- get Job Ids in Config Approval Chain -- end


# start -- get Authority User, Allowed Users in Config Authority User -- start  
    auth_user_ids = [] 
    auth_allow_user_ids = []
    for chain_job_id in aprvl_chain_job_ids:
        res_authority_user = _get_authority_user(self, dept_id, source_id,chain_job_id, aprvl_chain_job_ids, create_uid)         
        for auth_user_id in res_authority_user:
            auth_user_ids.append(auth_user_id.user_id.id)  
            auth_allow_user_ids.append(auth_user_id.allow_user_ids)          
# end -- get Authority User, Allowed Users in Config Authority User -- end  

# start -- get Request Approvers -- start  
    if (aprvl_chain_job_ids != req_aprvl_job_ids) or (req_aprvl_user_ids != auth_user_ids) or (req_aprvl_alwd_usr_ids != auth_allow_user_ids):
        
        for get_job_id in aprvl_chain_job_ids:
            if get_job_id:
                for rec_aprvl in res_req_aprvl:
                   self.env['request.approval'].search([('id', '=', rec_aprvl.id)]).unlink()
                   
                res_authority_user = _get_authority_user(self, dept_id, source_id, get_job_id, aprvl_chain_job_ids, create_uid)
                if res_authority_user:
                    user_id = res_authority_user.user_id.id
                    allowed_users = res_authority_user.allow_user_ids
                    allow_user_ids = []
                    for get_user_id in allowed_users:
                        allow_user_ids.append(get_user_id.id)
                
                    self.env['request.approval'].create({'request_id':rec_id, 'hr_job_id':get_job_id,'user_id':user_id,'allowed_user_ids':[(6,0,allow_user_ids)]}) 
            else:
               raise ValidationError("No Authority Assigned to Request Type Selected. Please Consult Admin.")
# end -- get Request Approvers -- end                

def _get_to_approve_by(self,dept_id,res_req_aprvl):
#     res_req_aprvl = self.env['request.approval'].search([('request_id','=',self.id),('approved','=',False)], limit =1)
    user = self.env.user.id
    if res_req_aprvl:
        rec_request_approval = self.env['request.approval'].browse(res_req_aprvl.id)
        get_job_id = rec_request_approval.hr_job_id.id
        get_user_id = rec_request_approval.user_id.id

        res_dept_approver = self.env['config.department.approver'].search([('hr_department_id','=',dept_id)])
        res_authority_user = self.env['config.authority.user'].search([('dept_approver_id','=',res_dept_approver.id),('hr_job','=',get_job_id),\
                                                                       ('user_id','=',get_user_id)])

        to_approve_by = []
        recipients = ''
        rec_authority_user = self.env(user=SUPERUSER_ID)['config.authority.user'].browse(res_authority_user.id)
        user_id = rec_authority_user.user_id.id
        partner_id = rec_authority_user.user_id.partner_id.id

        if not user_id:
            raise ValidationError("Configuration Error. PLease Consult Developer") 
        to_approve_by.append(user_id)
        recipients = str(partner_id)
        allow_bypass = rec_authority_user.allow_bypass
        if allow_bypass:
            allow_user_ids = rec_authority_user.allow_user_ids
            for allow_user in allow_user_ids:
                to_approve_by.append(allow_user.id)
                recipients = recipients + ',' + str(allow_user.partner_id.id)

        if to_approve_by:
                self.sudo().write({'to_approve_by':[(6,0,[to_approve_by])],'recipients':recipients}) 

#         return to_approve_by
        
def get_chain_job_ids(self, level_id, dept_id):
    
            res_aprvl =  self.env['config.approval'].search([('department_level_id','=',level_id),('department_id','=',dept_id)])
            if not  res_aprvl:
                res_aprvl =  self.env['config.approval'].search([('department_level_id','=',level_id )])
            aprvl_list = []
            for rec_aprvl in res_aprvl:
                aprvl_list.append(rec_aprvl.id)
                          
            res_aprvl_rule = self.env['config.approval.rule'].search([('approval_ids','in',aprvl_list)])                
            rule_list = []
            for rec_rule in res_aprvl_rule:
                rule_list.append(rec_rule.id)
  
            res_aprvl_chain = self.env['config.approval.chain'].search([('approval_rule_id','in',rule_list)])
            branch_id = _get_branch_id(self, dept_id)
  
            job_ids = []
            for rec_chain in res_aprvl_chain:
                chain_obj = self.env['config.approval.chain'].browse(rec_chain.id)
                get_job = chain_obj.hr_job_id.id
                job_ids.append(get_job)
            
            return job_ids
        
def _get_dept_authority(self,res_dept_aprvr,level_id):
    
#     res_dept_aprvr = self.env['config.department.approver'].search([('hr_department_id','in',dept_ids)])

    for rec_dept_aprvr in res_dept_aprvr:
        dept_id = rec_dept_aprvr.hr_department_id.id

        res_auth = self.env['config.authority.user'].search([('dept_approver_id','=',rec_dept_aprvr.id)])

        auth_user_exist_job_ids = []
        for rec_auth in res_auth:
            auth_obj = self.env['config.authority.user'].browse(rec_auth.id)
            hr_job = auth_obj.hr_job.id 
            auth_user_exist_job_ids.append(hr_job)

        chain_job_ids = get_chain_job_ids(self, level_id, dept_id)

        get_job = self.env['hr.job'].search(['&',('id','in',chain_job_ids),'!',('id','in',auth_user_exist_job_ids)])      
    
        get_job_ids = self.env['hr.job'].search(['&',('id','in',auth_user_exist_job_ids),'!',('id','in',chain_job_ids)])   
        
        for rec in get_job_ids:
            self.env['config.authority.user'].search([('dept_approver_id','=',rec_dept_aprvr.id),('hr_job','=',rec.id)]).unlink() 
               
        for rec_job in get_job:
            self.env['config.authority.user'].create({'dept_approver_id':rec_dept_aprvr.id,'hr_job':rec_job.id})

    return



