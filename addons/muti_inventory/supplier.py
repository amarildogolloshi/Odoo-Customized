
# -*- coding: utf-8 -*-
from datetime import timedelta,time,date,datetime
from dateutil import parser
from openerp import models, fields, api, exceptions


class Supplier_info(models.Model):
    _name = 'supplier.info'
 
    supplier_id = fields.Char(string = 'Supplier ID')
    supplier_lname = fields.Char(string = 'Last Name')
    supplier_mname = fields.Char(string = 'Middle Name')
    supplier_fname = fields.Char(string = 'First Name')
    supplier_company = fields.Char(string = 'Company')
    supplier_agentorsalesrepresentative = fields.Char(string = 'Agent/Sales Representative')
    supplier_street1 = fields.Char(string = 'Street 1')
    supplier_street2 = fields.Char(string = 'Street 2')
    supplier_city = fields.Many2one('config.city',string = 'City', required = True)
    supplier_province = fields.Char(string = 'Province')
    supplier_country = fields.Char(string = 'Country')
    supplier_website = fields.Char(string = 'Web Site')
    supplier_status = fields.Char(string = 'Status')
    supplier_jobposition = fields.Char(string = 'Job Position')
    supplier_phone = fields.Char(string = 'Phone')
    supplier_mobile = fields.Char(string = 'Mobile')
    supplier_fax = fields.Char(string = 'Fax')
    supplier_tinno = fields.Char(string = 'Tax Identification No.')
    supplier_email= fields.Char(string = 'Email')
    supplier_tags= fields.Char(string = 'Tags')
    supplier_customer= fields.Char(string = 'Customer')  
    supplier_barcode = fields.Char(string = 'Barcode')  
    supplier_payment= fields.Char(string = 'Payments')
    supplier_vendor = fields.Char(string = 'Vendor')
    supplier_paymentterm = fields.Char(string = 'Payment Term')
    supplier_discount = fields.Char(string = 'Discount')

   
     
    
    
    

   
        

    
    
    
    
