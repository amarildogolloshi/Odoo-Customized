# -*- coding: utf-8 -*-
import openerp
from datetime import timedelta,time,date,datetime
from dateutil import parser
from openerp import models, fields, api, exceptions
from openerp.osv import osv



class muti_supplier(models.Model):
    _inherit = 'res.partner' 
    
    def _get_default_active(self):
        if 'default_active' in self.env.context:
            print 'in'
            default_active = self.env.context['default_active']
            if default_active == 'supplier':
                return True
            else:
                return False
        
    old_code = fields.Char(string = 'Old Code')
    supplier_id = fields.Char(string='Supplier ID', readonly=True)
    suffix = fields.Char(string='Suffix')

#     wholesale= fields.Boolean('Wholesale') 
#     retail= fields.Boolean('Retail') 

    bank_account= fields.Char()
    credit_card= fields.Char()
    mode_payment = fields.Selection([('collection','For Collection'),('sending','For Sending')], string = 'Mode of Payment')
#     vendor = fields.Boolean()
#     customer_payment_term = fields.Many2one('account.payment.term',string = 'Customer Payment Term')
#     vendor_payment_term = fields.Many2one('account.payment.term',string = 'Vendor Payment Term')
    discount = fields.Char(string = 'Discount') 
    supplier = fields.Boolean(default = _get_default_active)
    
    @api.model
    def create(self, vals):
        print 'entered create ', self
        print 'entered create vals ', vals
        contxt = self.env.context
        if 'supplier' in contxt:
            sequence = self.env['ir.sequence'].get('supplier_id')       
            vals['supplier_id']=sequence   
             
        vals['supplier']=True
        vals['customer']=False
        
        context = self._context
        if (vals.get('company_type'))=='person':            
                if (vals.get('first_name'))==0 or (vals.get('last_name'))==0:
                    raise osv.except_osv(('Error'), ('Fill First Name and Last Name first.'))
                else:
                    if (vals.get('middle_name'))==0:
                        vals['middle_name'] = ''
                    else:
                        vals['middle_name'] = vals['middle_name'].upper().strip()
                    if (vals.get('suffix'))==0:
                        vals['suffix'] = ''
                    else:
                        vals['suffix'] = vals['suffix'].upper().strip()
                    vals['first_name'] = vals['first_name'].upper().strip()                    
                    vals['last_name'] = vals['last_name'].upper().strip()
                    vals['name'] = vals['last_name'] + ', ' + vals['first_name'] + ' ' + vals['middle_name']+ ' ' + vals['suffix']
           
                    res_id = super(muti_supplier, self).create(vals)                    
                    return res_id
        if (vals.get('company_type'))=='company':
            if(vals.get('name'))==0:
                raise osv.except_osv(('Error'), ('Fill Company Name first.'))
            else:  
                vals['name']=vals['name']
                res_id = super(muti_supplier, self).create(vals)                    
                return res_id
    @api.multi   
    def write(self, vals):
       
            if vals.get('first_name') :
                vals['first_name'] =  vals.get('first_name').upper().strip()
            else:
                if self.first_name != False:
                    vals['first_name'] = self.first_name.upper().strip()
             
            if vals.get('middle_name'):
                vals['middle_name'] =  vals.get('middle_name').upper().strip()
            else:
                if self.middle_name != False:
                    vals['middle_name'] = self.middle_name.upper().strip()
            
            if vals.get('last_name'):
                vals['last_name'] =  vals.get('last_name').upper().strip()
            else:
                if self.last_name != False:
                    vals['last_name'] = self.last_name.upper().strip() 
                
            if vals.get('suffix') :
                vals['suffix'] =  vals.get('suffix').upper().strip()
            else:
                if self.suffix != False:
                    vals['suffix'] = self.suffix.upper().strip()   

            if self.last_name != False or self.middle_name != False or self.first_name != False or self.suffix != False:    
                vals['name'] = vals['last_name'].upper().strip() + ', ' + vals['first_name'].upper().strip() + ' ' + vals['middle_name'].upper().strip() + ' ' + vals['suffix'].upper().strip()

            res_id = super(muti_supplier, self).write(vals)
            return res_id 

        
   