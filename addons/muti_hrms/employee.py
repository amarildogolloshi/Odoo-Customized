# -*- coding: utf-8 -*-
from datetime import timedelta,time,date,datetime
from dateutil import parser
from openerp import models, fields, api, exceptions

class employee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    
    @api.depends('birthday')
    def _get_age(self):
        for r in self:
            if r.birthday:
                bdate = datetime.strptime(r.birthday, "%Y-%m-%d").date()
                today = date.today()
                diffdate = today - bdate

                years = diffdate.days/365
                formonth = diffdate.days - (years * 365.25)
                months = (formonth/31)

                
#                 newdate = bdate.replace(year = date.today().year)
#                 print newdate
#                 if today > newdate:
#                     newtoday = today-newdate
#                     print newtoday
                bday = bdate.day
                tody = date.today().day
                if tody >= bday:
                    day = tody-bday
                else:
                    day = 31 - (bday-tody)
                
                r.age_complete = str(years) + ' Year/s ' + str(int(months)) + ' Month/s ' + str(day) + ' Day/s' 
                r.age = str(years)
                
            
    @api.depends('emp_children_id')
    def _get_noofchildren(self):
        
        for r in self:
            r.no_of_child = len(r.emp_children_id)
            
    def _default_country(self):
        
        res = self.env['res.country'].search([['code','=','PH']])
        print res   
        
#     @api.model
#     def create(self, vals):
#         print 'entered create ', self
#         print 'entered create vals ', vals
#         
#         context = self.env.context
#         print context
#         if context['type']:
#             vals['type'] = context['type']
#             
#             res_id = super(employee, self).create(vals)
#             return res_id 
#         
        
    @api.model
    def create(self, vals):
         
        context = self._context
             
        if not vals.get('name'):
            vals['emp_firstname'] = vals['emp_firstname'].upper().strip()
            vals['emp_middlename'] = vals['emp_middlename'].upper().strip()
            vals['emp_lastname'] = vals['emp_lastname'].upper().strip()              
            vals['name'] = vals['emp_lastname'] + ', ' + vals['emp_firstname'] + ' ' + vals['emp_middlename']
        res_id = super(employee, self).create(vals)
        return res_id
    
        if vals['emp_id']:
            emp_id = vals['emp_id'].lower()
            search_user = self.env['res.users'].search([('login','=',emp_id)])
            if search_user:
                vals['user_id'] = search_user['id']
                if vals['company_name']:
                    nickname = vals['company_name']
                    search_user.write({'nickname':nickname})
                

    
    @api.multi   
    def write(self, vals):
        if vals.get('emp_firstname') :
            vals['emp_firstname'] =  vals.get('emp_firstname').upper().strip()
        else:
            if self.emp_firstname != False:
                vals['emp_firstname'] = self.emp_firstname.upper().strip()
             
        if vals.get('emp_lastname') :
            vals['emp_lastname'] =  vals.get('emp_lastname').upper().strip()
        else:
            if self.emp_lastname != False:
                vals['emp_lastname'] = self.emp_lastname.upper().strip()
            
        if vals.get('emp_middlename') :
            vals['emp_middlename'] =  vals.get('emp_middlename').upper().strip()
        else:
            if self.emp_middlename != False:
                vals['emp_middlename'] = self.emp_middlename.upper().strip()  

        if self.emp_lastname != False or self.emp_firstname != False or self.emp_middlename != False:    
            vals['name'] = vals['emp_lastname'].upper().strip() + ', ' + vals['emp_firstname'].upper().strip() + ' ' + vals['emp_middlename'].upper().strip()
        
        if vals.get('emp_id'):
            emp_id = vals.get('emp_id').lower()
            print emp_id
            search_user = self.env['res.users'].search([('login','=',emp_id)])
            if search_user:
                vals['user_id'] = search_user['id']
                if vals.get('company_name'):
                    nickname = vals['company_name']
                    search_user.write({'nickname':nickname})
    
        res_id = super(employee, self).write(vals)
        
        return res_id 
#     @api.onchange('province_id')        
#     def _onchange_filter_city(self):
#         print self.province_id
#     
#         for record in self.province_id:
#             print record.id
#             self.filter_city = record.id
#             search_province = self.env['localization.city'].search([('province_id','=',record.id)])
#             if search_province:
#                 print search_province
#                 for rec_city in search_province:
#                     print rec_city
    emp_id = fields.Char(string = 'Employee ID', required=  True)
    emp_lastname = fields.Char(string = 'Last Name',required = True)
    emp_firstname = fields.Char(string = 'First Name' , required = True)
    emp_middlename = fields.Char(string = 'Middle Name', required = True)
    company_name = fields.Char(string = 'Company Name', required = True)
    age = fields.Char(compute = '_get_age', store = True)
    age_complete = fields.Char(compute = '_get_age',string = 'Age')
#     job_level = fields.Char(related = 'job_id.job_level_id.name',string = "Employee Classification")
    job_level = fields.Many2one('config.job.level',related = 'job_id.job_level_id',string = "Employee Classification")
    height = fields.Float(string ='Height in cm' )
    weight = fields.Float(string = 'Weight in lbs')
    no_of_child = fields.Integer(string = 'No. of Children', compute = '_get_noofchildren')
    sss_no = fields.Char(string = 'SSS No.')
    phic_no = fields.Char(string = 'PHilHealth No.')
    hdmf_no = fields.Char(string = 'HDMF No.')
    tin_no = fields.Char(string = 'TIN No.')
    skype = fields.Char(string = 'Skype Name')
    contact1 = fields.Char(string = 'Contact Number(1)')
    contact2 = fields.Char(string = 'Contact Number(2)')
    personal_email = fields.Char(string = 'Email Address')
    permanent_address = fields.Char(string = 'Permanent Address')
    current_address = fields.Char(string = 'Current Address')
#     province_id = fields.Many2one('config.province',string = 'Province',required = True)
#     city_id = fields.Many2one('config.city',string = 'City', required = True)
#     barangay_id = fields.Many2one('config.barangay',string = 'Barangay')
#     city_id = fields.Char(string = 'City',related = 'barangay_id.city_id.name')
    religion_id = fields.Many2one('employee.religion',string = 'Religion')
    education_id = fields.One2many('employee.education','education_id', string = 'Educational Background')
    blood_type_id = fields.Many2one('employee.medical.blood',string = 'Blood Type')
    physical_ids = fields.Many2many('employee.medical.phydisorder',string = 'Physical Disorder/s')
    allergy_ids = fields.Many2many('employee.medical.allergy',string = 'List of Allergy/ies')
    health_ids = fields.Many2many('employee.medical.healthprob',string = 'List of Health Problem/s')
    work_id = fields.One2many('employee.workexperience','work_id',string = 'Work Experience')
    emp_parent_id = fields.One2many('res.partner','partner_id',string = 'Parents',context={'partner_type': 'parent'})
    emp_children_id = fields.One2many('res.partner','partner_id',string = 'Children',context={'partner_type': 'children'})
#     emp_children_id = fields.One2many('employee.children','emp_children_id',string = 'Children')
    emp_spouse_id = fields.One2many('res.partner','partner_id',string = 'Spouse',context={'partner_type': 'spouse'})
    skill_ids = fields.Many2many('employee.skills','employee_skills_rel','emp_skill_id','skill_id',string = 'Skills')
    emp_license_id = fields.One2many('employee.license','emp_license_id',string = 'License')
    emp_organisation_id = fields.One2many('employee.organisation','emp_organisation_id',string = 'License')
    external_seminar_id = fields.One2many('employee.seminar','emp_seminar_id',string = 'External Seminar',context={'type': 'external'})
    internal_seminar_id = fields.One2many('employee.seminar','emp_seminar_id',string = 'Internal Seminar',context={'type': 'internal'})
    employee_awards_ids = fields.Many2many('employee.awards',string = 'Employee Awards/Recognitions')
    employee_status_id = fields.Many2one('employee.status',string = 'Employee Status')
    marital = fields.Selection(selection_add=[("singleparent", "Single Parent"),("separated", "Separated")])
    date_hired=fields.Date(string ='Actual Date of Joining')
    regularization_date = fields.Date(string="Regularization Date")
    payroll_date_hired = fields.Date(string = 'Payroll Hiring Date')
    medical_benefits_id = fields.One2many('employee.medical.benefits','emp_id',string = 'Employee Medical Assistance Benefits')
    physical_medical_dental_id = fields.One2many('employee.physical.medical.dental','emp_id',string = 'Physical/Medical/Dental Examination')
    emergency_name = fields.Char(string = 'Name')
    emergency_contact1 = fields.Char(string = 'Contact(1)')
    emergency_contact2 = fields.Char(string = 'Contact(2)')
    emergency_address = fields.Text(string = 'Address')
    emergency_relationship = fields.Char(string = 'Relationship')
    emp_report_to_ids = fields.Many2many('hr.employee','emp_report_rel','emp_id','report_to_id',string="Employee")
    
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         'The name must be unique'),
        ]
     
    
class employee_religion(models.Model):
    _name = 'employee.religion'
    
    name = fields.Char(string = 'Religion', required = True)
    
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         'The religion must be unique')
        ]
    
    
class employee_education_level(models.Model):
    _name = 'employee.education.level'
    
    name = fields.Char(string = 'Level', required = True)
    
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         'The level must be unique')
        ]
    
    
class employee_education_course(models.Model):
    _name = 'employee.education.course'
    
    name = fields.Char(string = 'Course', required = True)
    noofyears = fields.Float(string = 'No of Years',required = True)
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         'The course must be unique')
        ]
    
class employee_education(models.Model):
    _name = 'employee.education'
    
    def _get_years(self):
        
        this_year = datetime.today().year
        
        results = [(str(x), str(x)) for x in range(this_year-40, this_year)]
        return results
    
    education_id = fields.Many2one('hr.employee', string  = 'Employees', ondelete="cascade", onwrite="cascade", required = True)
    level_id = fields.Many2one('employee.education.level',string = 'Level', required = True)
    school = fields.Char(string = 'School Name', required = True)
    address = fields.Char(string = 'School Address', required = True)
    course_id = fields.Many2one('employee.education.course',string = 'Course')
    major = fields.Char(string = 'Major')
    year = fields.Selection(_get_years, 'Year', required = True)
    
    
    
    
class employee_medical_blood(models.Model):
    _name = 'employee.medical.blood'
    
    name = fields.Char(string = ' Blood Type', required = True)
    
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         'The blood type must be unique')
        ]
    
    
class employee_medical_phydisorder(models.Model):
    
    _name = 'employee.medical.phydisorder'
    
    name = fields.Char(string = 'Physical Disorder', required = True)
    
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         'The physical disorder must be unique')
        ]
    
    
    
class employee_medical_allergy(models.Model):
    
    _name = 'employee.medical.allergy'
    
    name = fields.Char(string = ' Allergy', required = True)
    
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         'The allergy must be unique')
        ]
    
    
class employee_medical_healthprob(models.Model):
    _name = 'employee.medical.healthprob'
    
    name = fields.Char(string = ' Health Problem', required = True)
    
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         'The health problem must be unique')
        ]

class employee_medical_benefits(models.Model):
    _name = 'employee.medical.benefits'
    
    emp_id = fields.Many2one('hr.employee')
    date_process = fields.Date(string = 'Date Processed')
    amount =fields.Float(digits=(16,2),string = 'Amount')
    
class employee_physical_medical_dental(models.Model):
    _name = 'employee.physical.medical.dental'
    
    emp_id = fields.Many2one('hr.employee')
    date_process = fields.Date(string = 'Date Processed')
    amount =fields.Float(digits=(16,2),string = 'Amount')
    
    
class employee_workexperience(models.Model):
    _name = 'employee.workexperience'
    
    work_id = fields.Many2one('hr.employee', string  = 'Employees', ondelete="cascade", onwrite="cascade", required = True)
    company = fields.Char(string = 'Company', required = True)
    address= fields.Char(string = 'Address', required = True)
    external_job_id = fields.Many2one('employee.external.jobs',string = 'Position', required = True)
    date_from = fields.Date(string = 'Date From', required = True)
    date_to = fields.Date(string = 'Date To', required = True)
    reason_for_leaving = fields.Char(string = 'Reason for Living')
    length_service = fields.Char(compute = '_get_length_service')
     
    @api.depends('date_from','date_to')
    def _get_length_service(self):
        print self.date_from, self.date_to 
        if self.date_from <> False and self.date_to <> False:
            datefrom = datetime.strptime(self.date_from, "%Y-%m-%d").date()
            dateto = datetime.strptime(self.date_to, "%Y-%m-%d").date()
            diffdate = dateto - datefrom
            years = diffdate.days/365
            formonth = diffdate.days - (years * 366)
            months = formonth/30
            forday = formonth - (months * 30)
            self.length_service = str(years) + ' Year/s ' + str(months) + ' Month/s and ' + str(forday) + ' Day/s'
            
#             
# class employee_parents(models.Model):
#     _name = 'employee.parents'
#     
#     emp_parent_id = fields.Many2one('hr.employee', string  = 'Employees', ondelete="cascade", onwrite="cascade", required = True)
#     first_name = fields.Char(string = 'First Name', required = True)
#     middle_name = fields.Char(string = 'Middle Name', required = True)
#     last_name = fields.Char(string = 'Last Name', required = True)
#     gender = fields.Selection([('male','Male'),('female','Female')], required = True)
#     address = fields.Char(string = 'Address' , required = True)
#     occupation = fields.Char(string = 'Occupation' , required = True)
    
    
# class employee_children(models.Model):
#     _name = 'employee.children'
#     
#     emp_children_id = fields.Many2one('hr.employee', string  = 'Employees', ondelete="cascade", onwrite="cascade", required = True)
#     first_name = fields.Char(string = 'First Name')
#     middle_name = fields.Char(string = 'Middle Name')
#     last_name = fields.Char(string = 'Last Name')
#     gender = fields.Selection([('male','Male'),('female','Female')])
#     birthdate = fields.Date(string = 'Birthday')
    
    
# class employee_spouse(models.Model):
#     _name = 'employee.spouse'
#     
#     emp_spouse_id = fields.Many2one('hr.employee', string  = 'Spouse', ondelete="cascade", onwrite="cascade", required = True)
#     first_name = fields.Char(string = 'First Name', required = True)
#     middle_name = fields.Char(string = 'Middle Name', required = True)
#     last_name = fields.Char(string = 'Last Name', required = True)
#     gender = fields.Selection([('male','Male'),('female','Female')], required = True)
#     occupation = fields.Char(string = 'Occupation' , required = True)


# class employee_skills_category(models.Model):
#     _name = 'employee.skill.category'
#     
#     name = fields.Char(string = 'Name', required = True)
#     skill_id = fields.One2many('employee.skills','skill_id',string = 'Skill')
#     
class employee_skills_category(models.Model):
    _name = 'employee.skills.category'
    _order ='skill_id'
    name = fields.Char(string = 'Name', required = True)
    skill_id = fields.One2many('employee.skills','skill_category_id',string = 'Skill')
     
class employee_skills(models.Model):
    _name = 'employee.skills'
    _order = 'skill_category_id'
    
    emp_id = fields.Many2one('hr.employee',string = 'Employee')
    name = fields.Char(string =' Name', required = True)
    skill_category_id = fields.Many2one('employee.skills.category',string = 'Skill Category')

    

class employee_conf_license(models.Model):
    _name = 'employee.conf.license'
    
    name = fields.Char(string =' Name', required = True)
    
    
class employee_license(models.Model):
    _name = 'employee.license'
    
    emp_license_id = fields.Many2one('hr.employee', string  = 'License', ondelete="cascade", onwrite="cascade", required = True)
    license_conf_id = fields.Many2one('employee.conf.license',string ='Type', required = True)
    license_no = fields.Char(string = 'License Number', required = True)
    restriction_no = fields.Char(string = 'Restriction Number')
    date_issued = fields.Date(string = 'Date Issued',required = True)
    date_expiry = fields.Date(string = 'Date Expiry', required = True)
    renewed_by = fields.Selection([('personal','Personal'),('company','Company')], required = True)
    
    
class employee_conf_organisation(models.Model):
    _name = 'employee.conf.organisation'
    
    name = fields.Char(string  = 'Organisation', required = True)
    
    
class employee_organisation(models.Model):
    _name = 'employee.organisation'
    
    emp_organisation_id = fields.Many2one('hr.employee', string  = 'Organisation', ondelete="cascade", onwrite="cascade", required = True)
    organisation_id = fields.Many2one('employee.conf.organisation',string = 'Organisation', required = True)
    position = fields.Char(string = 'Position', required = True)
    date_from = fields.Date(string = 'Date From', required = True)
    date_to = fields.Date('Date To', help = "Serves as Present if blank")
    
    
class employee_conf_seminar(models.Model):
    _name = 'employee.conf.seminar'
    
    name = fields.Char(string = 'Seminar',required = True)
    
    
class employee_seminar(models.Model):
    _name = 'employee.seminar'
    
    def _search(self, cr, uid, args, offset=0, limit=None, order=None,
        context={}, count=False, access_rights_uid=None):
        if context:
            if 'type' in context:
                args.append(("type","=",context['type']))
                   
        return super(employee_seminar, self)._search(cr, uid, args, offset=offset, limit=limit, order=order,
         context=context, count=count, access_rights_uid=access_rights_uid)
         
     
    @api.model
    def create(self, vals):
          
        context = self.env.context
        if context['type']:
            vals['type'] = context['type']
              
            res_id = super(employee_seminar, self).create(vals)
            return res_id
#      
#     @api.multi 
#     def write(self, vals):
#         context = self.env.context
#         print context
#         res_id = super(employee_seminar, self).write(vals)
#          
#          
#         return res_id
     
    emp_seminar_id = fields.Many2many('hr.employee')
    seminar_id = fields.Many2one('employee.conf.seminar',string = 'Seminar', required = True)
    agency_id = fields.Many2one('res.partner',string = 'Agency')
    date_from = fields.Date(string = 'Date From', required = True)
    date_to = fields.Date(string = 'Date To', required = True)
    type = fields.Selection([('external','External'),('internal','Internal')],string = 'Type',required = True)
    address = fields.Text(string = 'Address')
    
    
class employee_external_jobs(models.Model):
    _name = 'employee.external.jobs'
    
    name = fields.Char(string = 'Job')
    
class employee_status(models.Model):
    _name = 'employee.status'
    
    name = fields.Char(string = 'Status', required = True)


class employee_awards(models.Model):
    _name = 'employee.awards'
    
    employee_awards_id = fields.Many2many('hr.employee')
    name = fields.Char(string = 'Awards/Recognition', required = True)
    date_awarded = fields.Date(string = 'Date Awarded', required = True)
    place_awarded = fields.Char(string = 'Awarded at', required = True)
    

# class hr_job(models.Model):
#     _inherit = 'hr.job'
#     
#     name = fields.Char(string = 'Job')
#     

class config_job_level(models.Model):
 
    _name = 'config.job.level'
    _order = 'name'

    
    code = fields.Char(string = 'Code')
    name = fields.Char(string = 'Name')
    parent_id = fields.Many2one('config.job.level',string = 'Category')
    child_ids = fields.One2many('config.job.level', 'parent_id', string="Child Job Level")
    complete_name = fields.Char(string="Complete Name", compute='_complete_name')

    @api.depends('parent_id','name') 
    def _complete_name(self):
            self.name_get()
            
    @api.multi
    def name_get(self):
   
        res = super(config_job_level, self).name_get()
        data = []
        for r in self:
            print 'r', r.name
            if r.parent_id.name:
                display_value = str(r.parent_id.name) + '/' +str(r.name)
            else:
                display_value = str(r.name)
            data.append((r.id, display_value))
            r.complete_name = display_value
        return data  
           
    
class hr_job(models.Model):
 
    _inherit = 'hr.job'
    
    job_level_id = fields.Many2one('config.job.level', string = 'Level')
    company_id = fields.Many2one('res.company', string='Company')
