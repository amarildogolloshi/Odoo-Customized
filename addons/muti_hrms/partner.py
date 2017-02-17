
# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime


class Partner(models.Model):
    _inherit = 'res.partner'
    
    def _search(self, cr, uid, args, offset=0, limit=None, order=None,
        context={}, count=False, access_rights_uid=None):
        if context:
            if 'partner_type' in context:
                args.append(("partner_type","=",context['partner_type']))
                  
        return super(Partner, self)._search(cr, uid, args, offset=offset, limit=limit, order=order,
         context=context, count=count, access_rights_uid=access_rights_uid)
        
#     def create(self,cr,uid,vals,context = None):
#         print 'context', context
#         if context:
#              
#             if 'partner_type' in context:
#                 vals['partner_type'] = context['partner_type']
#          
#        
#                 firstname = vals['first_name'].upper().strip()
#                 middlename = vals['middle_name'].upper().strip()
#                 lastname = vals['last_name'].upper().strip()
#                  
#                 vals['name'] = lastname + ', ' + firstname + ' ' + middlename
#  
#         return super(Partner,self).create(cr,uid,vals,context=context)

    @api.model
    def create(self, vals):
         
        context = self._context
        if 'partner_type' in context:
            vals['partner_type'] = context.get('partner_type')
        print context.get('partner_type')
        if not vals.get('name'):
            
            vals['first_name'] = vals['first_name'].upper().strip()
            vals['middle_name'] = vals['middle_name'].upper().strip()
            vals['last_name'] = vals['last_name'].upper().strip()
              
            vals['name'] = vals['last_name'] + ', ' + vals['first_name'] + ' ' + vals['middle_name']
        res_id = super(Partner, self).create(vals)
        return res_id

    
    @api.multi   
    def write(self, vals):
        if vals.get('first_name') :
            vals['first_name'] =  vals.get('first_name').upper().strip()
        else:
            if self.first_name != False:
                vals['first_name'] = self.first_name.upper().strip()
             
        if vals.get('last_name') :
            vals['last_name'] =  vals.get('last_name').upper().strip()
        else:
            if self.last_name != False:
                vals['last_name'] = self.last_name.upper().strip()
            
        if vals.get('middle_name') :
            vals['middle_name'] =  vals.get('middle_name').upper().strip()
        else:
            if self.middle_name != False:
                vals['middle_name'] = self.middle_name.upper().strip()  
        
        if vals.get('street') :
            vals['street'] =  vals.get('street').upper().strip()
        else:
            if self.street != False:
                vals['street'] = self.street.upper().strip()  
        if self.first_name != False or self.first_name != False or self.middle_name != False:    
            vals['name'] = vals['last_name'].upper().strip() + ', ' + vals['first_name'].upper().strip() + ' ' + vals['middle_name'].upper().strip()

        res_id = super(Partner, self).write(vals)
        
        return res_id 

    partner_id = fields.Many2one('hr.employee', string  = 'Partners', ondelete="cascade", onwrite="cascade", required = True)
    first_name = fields.Char(string = 'First')
    last_name = fields.Char(string = 'Last')
    middle_name = fields.Char(string = 'Middle')   
    partner_type = fields.Selection([('parent','Parents'),('children','Children'),('spouse','Spouse')],string = 'Type')
    external_job_id = fields.Many2one('employee.external.jobs',string = 'Job/Occupation')
    gender = fields.Selection([('male','Male'),('female','Female')],string = 'Gender')
    birthday = fields.Date(string = 'Birthday')
    province_id = fields.Many2one('config.province',string = 'Province')
    city_id = fields.Many2one('config.city',string = 'City')
    barangay_id = fields.Many2one('config.barangay',string = 'Barangay')
    date_marriage = fields.Date(string = 'Date of Marriage')
