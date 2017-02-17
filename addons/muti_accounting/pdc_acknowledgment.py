# -*- coding: utf-8 -*-
from datetime import *
from time import strptime
from time import mktime
import math
from openerp import models, fields, api
from openerp.exceptions import ValidationError

def _get_branch_id(self):
     
    uid = self.env.user.id
    print 'uid', uid
     
    user_obj = self.env['res.users'].browse(uid)
    
    branch_id =  user_obj.branch_id.id
    print 'branch_id', branch_id
    

    return branch_id


class pdc_acknowledgment(models.Model):
    _name = 'pdc.acknowledgment'
    _description = 'Post-Dated Check Acknowledgment'
       
    branch_id = fields.Many2one('config.branch', string = 'Branch', default=_get_branch_id)
    transaction_date = fields.Date(string = 'Transaction Date')
    apc_number = fields.Char(string = 'APC No.', size = 50)
    apc_date = fields.Date(string = 'Doc Date', required = True)
    res_partner_id = fields.Many2one('res.partner', string = 'Payor', required = True)
    total_check_amount = fields.Float(compute = '_get_total_check_info', method=True, type='float', string='Total Check Amount')
    apc_ids = fields.One2many('pdc.acknowledgment.det', 'apc_id', string = 'Post-Dated Check Information')
    state = fields.Selection([
        ('draft',"Draft"), 
        ('confirm',"Confirmed"),
        ('post',"Posted"),
        ('void',"Void")],'State')
    void_state = fields.Selection([
            ('notvoid','Not Void'),
            ('recommend','Recommend for Void'),
            ('void','Void'),
        ],'Void State')
    
    @api.model
    def create(self,vals):
        
        values['branch_id'] = self._get_branch_id([0])
        check_apc_if_exist = self.search([('apc_number','=',vals['apc_number']),('branch_id','=',vals['branch_id'])])
        
        if check_apc_if_exist:
            raise ValidationError('APC is already exist!')
        
        res_user_id = super(pdc_acknowledgment,self).create(vals)
        
        return res_user_id
    
    @api.multi
    def write(self,vals):
        
        autosave = False
        
        if vals.has_key('state'):
            if vals['void_state'] in ('notvoid','recommend'):
                autosave = True
        
        if not autosave:
            br_id = self._get_branch_id(self.ids)
            
            if 'apc_number' in vals:
                apc_num = vals['apc_number']
            else:
                #den = self.browse(cr,uid, ids)
                apc_num = ['apc_number'].id

            #if not vals.has_key('branch_id'):
                #den = self.browse(cr,uid, ids)
                #br_id = den[0]['branch_id'].id
            
            check_apc_if_exist = self.search(cr, uid, [('id','!=',self.ids[0]), 
                                                ('apc_number', '=', apc_num), 
                                                ('branch_id', '=', br_id)])

            if check_apc_if_exist:
                raise ValidationError('APC is already exist!')

        return super(pdc_acknowledgment, self).write(vals)
    
    def set_confirm(self, ids, context=None):
        """
        """
        self.write(self.env.cr, self.uid, ids[0], {'state':'confirm'})
    
        return True

    def set_draft(self, ids, context=None):
        """
        """
        now = datetime.now()
        date_now = now.strftime("%Y-%m-%d")
        perm_rec = self.perm_read(cr, uid, ids, ['create_date'])        
        is_offline = tools.config.get('offline_mode')
        if is_offline and perm_rec[0]['create_date'][:10] < date_now:
            raise ValidationError('Set Back To Draft not allowed for records of previous days while on LOCAL CONNECTION') 
               
        self.write(self.env.cr, self.uid, ids[0], {'state':'draft'})

        return True
    
    def set_notvoid(self, ids, context=None):
        """
        """

        self.write(self.env.cr, self.uid, ids[0], {'void_state':'notvoid'})
        
        return True
    
    def set_recommend_void(self, ids, context=None):
        """
        """
       
        self.write(self.env.cr, self.uid, ids[0], {'void_state':'recommend'})

        return True
    
    def set_void(self, ids, context=None):
        """
        """
       
        self.write(self.env.cr, self.uid, ids[0], {'state':'void','void_state':'void'})

        return True
    
    @api.depends('apc_ids')
    def _get_total_check_info(self):
        """
        @comment Function that automatically computes for the Total Check Info upon saving
        @return check_amount
        """
        check_amount = 0.00
        
        for record in self:
            for n in record.apc_ids:
                res = self.env('pdc.acknowledgment.det').browse(n.id)
                if res:
                    if not res['cancelled']:
                        check_amount +=  res['check_amount']

        result[record.id] = check_amount
        return result
    
    @api.onchange('apc_number')
    def onchange_ap_series(self):
        self.apc_no = ''
        if self.apc_number:
                self.apc_no = "AP" + self.apc_number[2:].zfill(8)

        return {'value': {'apc_number':self.apc_no, } }
       
        
class pdc_acknowledgment_det(models.Model):
    
    _name = 'pdc.acknowledgment.det'
    _description = 'PDC Acknowledgment Details'
    
    apc_id = fields.Many2one('pdc.acknowledgment', string = 'APC ID')
    check_date = fields.Date(string = 'Check Date')
    check_number = fields.Char(string = 'Check Number', size=50)
    check_amount = fields.Float(string = 'Check Amount', digits=(16, 2))
    bank = fields.Char(string = 'Bank', size=20)
    bank_branch = fields.Char(string = 'Bank Branch', size=20)
    cancelled = fields.Boolean(string = 'Cancelled?')
    
    @api.model
    def create(self, vals): 
    
        ma = 0.00
        apc_id = vals['apc_id']
        check_amount = vals['check_amount']
        cancelled = vals['cancelled'] 
        uid = self.env.user               
        check_apc_if_exist = self.search([('check_number','=',vals['check_number']),('bank','=',vals['bank']),('bank_branch','=',vals['bank_branch'])])
     
        if check_apc_if_exist:
            raise ValidationError('Check Number already encoded.')
     
        uid = self.env.user
        ids = apc_id
#         if not cancelled:
#             ma = self._get_ma(cr, uid, vals, context)
                         
        if not (check_amount >= ma):
            raise ValidationError('Amount should be equal or greater to {:,}.'.format(ma))
               
        res_id = super(pdc_acknowledgment_det, self).create(vals)
     
        return res_id
    
    @api.multi
    def write(self, vals):
        
        if not vals.has_key('check_number'):
            #den = self.browse(cr,uid, ids)
            #vals['check_number'] = den[0]['check_number']
            checknum = ['check_number']
        else:
            checknum = vals['check_number']

        if not vals.has_key('bank'):
            #den = self.browse(cr,uid, ids)
            #vals['bank'] = den[0]['bank']
            bank_id = ['bank']
        else:
            bank_id = vals['bank']

        if not vals.has_key('bank_branch'):
            #den = self.browse(cr,uid, ids)
            #vals['bank_branch'] = den[0]['bank_branch'] 
            bbranch_id = ['bank_branch']
        else:
            bbranch_id = vals['bank_branch']
        
        if not vals.has_key('check_amount'):
            #den = self.browse(cr,uid, ids)
            #vals['check_amount'] = den[0]['check_amount']
            check_amt = ['check_amount']
        else:
            check_amt = vals['check_amount']

        if not vals.has_key('cancelled'):
            #den = self.browse(cr,uid, ids)
            #vals['cancelled'] = den[0]['cancelled']
            cancelled_check = ['cancelled']
        else:
            cancelled_check = vals['cancelled']
            
        if not vals.has_key('apc_id'):
            #den = self.browse(cr,uid, ids)
            #vals['apc_id'] = den[0]['apc_id'].id
            apc = ['apc_id'].id
        else:
            apc = vals['apc_id']

        check_apc_if_exist = self.search([('id','!=',ids[0]),('check_number','=',vals['check_number']),('bank','=',vals['bank']),('bank_branch','=',vals['bank_branch'])])
        
        if check_apc_if_exist:
            raise ValidationError('Check Number already encoded.')
        
        
        ma = 0.00
        apc_id = vals['apc_id']
        check_amount = vals['check_amount']
        cancelled = vals['cancelled']
        #if not cancelled:
            #ma = self._get_ma(cr, uid, vals, context)
                            
        if not (check_amount >= ma):
            raise ValidationError('Amount should be equal or greater to {:,}.'.format(ma))
            
        res = super(pdc_acknowledgment_det, self).write(vals)

        return res
        
        