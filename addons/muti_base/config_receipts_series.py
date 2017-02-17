# -*- coding: utf-8 -*-
from datetime import timedelta
from openerp import models, fields, api
from openerp.exceptions import ValidationError


def get_branch_id(self):
     
    uid = self.env.user.id
    print 'uid', uid
     
    user_obj = self.env['res.users'].browse(uid)
    
    branch_id =  user_obj.branch_id.id
    print 'branch_id', branch_id
    

    return branch_id


class config_receipts_series(models.Model):   
    _name = 'config.receipts.series'
    _description = 'Config Receipt Series'
    
    branch_id = fields.Many2one('config.branch', string = 'Branch', default=get_branch_id)# 
    name = fields.Char(string = 'Series', size=100)
    receipt_type = fields.Selection([('OR', 'Official Receipt'), #use for credit collection
                                     ('CSI-SP-', 'Cash Sales Invoice Spare Parts'),#use for cash sales/collection
                                     ('CSI-MC-', 'Cash Sales Invoice Motorcycle'),#use for cash sales/collection
                                     ('CI-SP-','Credit Sales Invoice Spare Parts'),#use for credit sales/on account
                                     ('CI-MC-','Credit Sales Invoice Motorcycle'),#use for credit sales/on account
                                     ('TR-','Temporary Receipt')],
                                    'Type')
    cashier = fields.Boolean(string = 'Assigned To Cashier',default=True)
    or_from = fields.Integer(string = 'Series Start')
    or_to = fields.Integer(string = 'Series End')
    leaves = fields.Integer(string = '# of Pages')
    receipts_ids = fields.One2many('config.receipts.series.det', 'crs_id', string = 'Receipts')

    state = fields.Selection([
        ('draft',"Draft"), 
        ('fin',"Finalized")],default = 'draft')
        
   
    @api.model
    def create(self,vals):

        if vals['or_from'] == 0 or vals['or_to'] == 0:
            raise ValidationError('Series From and To should have a value.')
        
        if vals['or_from'] > vals['or_to']:
            raise ValidationError('From should be less than To.')
        
        vals['state'] = 'draft'
        
        or_number = vals['receipt_type'] + str(vals['or_from']).zfill(8) + ' - ' + vals['receipt_type'] + str(vals['or_to']).zfill(8) 
        vals['name'] = or_number 
        
        return super(config_receipts_series, self).create(vals)
 
    @api.multi
    def write(self,vals):
        change_cashier = False
        if vals.has_key('cashier'):
            change_cashier = True
            cshr = vals['cashier']
            
        
        if 'receipt_type' in vals:
            receipt_type = vals['receipt_type']
        else:
            receipt_type = self.receipt_type
            
        if 'or_from' in vals:
            or_from = vals['or_from']
        else:
            or_from = self.or_from
            
        if 'or_to' in vals:
            or_to = vals['or_to']
        else:
            or_to = self.or_to
        
            
        or_number = receipt_type  + str(or_from).zfill(8) + ' - ' + receipt_type  + str(or_to).zfill(8) 
        vals['name'] = or_number 
            
        res = super(config_receipts_series, self).write(vals)

        if change_cashier:
           get_dets = self.read(vals,[('receipts_ids')])
           
           for self.or_det in get_dets[0]['receipts_ids']:
                self.env['config.receipts.series.det'].create(self.or_det,{'cashier':cshr})
        
        return res
    

    def _search(self, cr, uid, args, offset=0, limit=None, order=None,
            context={}, count=False, access_rights_uid=None):
          
        user = uid
        if context:
            if 'receiptseries_filter_br' in context:
                br_id = self.get_branch_id(cr, uid, [0])
                branches = []
                branches.append(br_id)
                assigned_branches = self.pool.get('res.users').search(cr,uid, [('user_id','=',uid),('branch_id','!=',br_id)])
                if assigned_branches:
                    for brnchs in assigned_branches:
                        brs = self.pool.get('res.users').read(cr,uid,brnchs,['branch_id'])
                        branches.append(brs['branch_id'][0])
                          
                args.append(("branch_id","in",branches))
  
  
  
        return super(config_receipts_series, self)._search(cr, uid, args, offset=offset, limit=limit, order=order,
        context=context, count=count, access_rights_uid=access_rights_uid) 
                 
    @api.multi
    def action_finalized(self):
        print 'or_from', self.or_from
        print 'or_to',self.or_to
        print 'receipts_ids',self.receipts_ids
        
        if self.state != 'draft':
            raise ValidationError("Warning", 'Validation Message - Finalized button already clicked.')  

        if self.receipts_ids:
            for rec in self.receipts_ids:
                self.env['config.receipts.series.det'].search([('id','=',rec.id)]).unlink()
        
        for receipt in range(self.or_from,  self.or_to+1):
            or_num = self.receipt_type + str(receipt).zfill(8)
 
            self.env['config.receipts.series.det'].create({
                                                           'crs_id': self.id,
                                                           'cashier':self.cashier,
                                                           'or_number': or_num,
                                                           'state' : 'unused',
                                                           })                                   
        self.state = 'fin'
 
        return True
     
    @api.multi
    def action_draft(self):


        if self.state == 'draft':    _defaults = {
        'branch_id' : _get_branch_id,
        'cashier' : True,
        'state' : 'init',
    }
        raise ValidationError("Already in draft") 

        for receipt in self.receipts_ids:

            get_stat_obj = self.env['config.receipts.series.det'].browse(receipt.id)

            get_stat = get_stat_obj.state
        
            if get_stat== 'used':
                raise ValidationError("One of the receipts is already used.") 
   
        self.state = 'draft'
 
        return True 
    
    @api.onchange('or_from', 'leaves')
    def onchange_or_from(self):
                  
        self.or_to = 0
           
        if self.or_from and self.leaves:
            self.or_to = self.or_from + self.leaves - 1
                               
        return {'value': {'self.or_to':self.or_to,} }
    
                           
class config_receipts_series_det(models.Model):       
    _name = 'config.receipts.series.det'
    _description = 'Config Receipt Series Detail'
      
    crs_id = fields.Many2one('cashier.receipts.series',string = 'Receipt Series', required=False)
    branch_id = fields.Many2one('config.branch', string = 'Branch', required=False)
    cashier = fields.Boolean(string = 'Assigned To Cashier')
    or_number = fields.Char(string = 'OR Number', size=50)
    creditcol_id = fields.Many2one('cashier.credit.collection', 'Credit Coll', required=False)  
    cashsale_id = fields.Many2one('cashier.cashsale.collection', 'Cash Sales', required=False) 
    creditsale_id = fields.Many2one('cashier.creditsale.collection', 'Credit Sales', required=False)   
    creditmemo_id = fields.Many2one('cashier.creditmemo.collection', 'Credit Memo', required=False)  
    state = fields.Selection([('unused', 'Unused'),
                    ('used', 'Used'),
                    ('void','Void')])
    
    
    def _search(self, cr, uid, args, offset=0, limit=None, order=None,
            context={}, count=False, access_rights_uid=None):
         
        user = uid
        if context:
            if 'receipts_filter_br' in context:
                br_id = self.get_branch_id(cr, uid, [0])
                branches = []
                branches.append(br_id)
                assigned_branches = self.pool.get('res.users').search(cr,uid, [('user_id','=',uid),('branch_id','!=',br_id)])
                if assigned_branches:
                    for brnchs in assigned_branches:
                        brs = self.pool.get('res.users').read(cr,uid,brnchs,['branch_id'])
                        branches.append(brs['branch_id'][0])
                     
                args.append(("branch_id","in",branches))
 
        return super(config_receipts_series_det, self)._search(cr, uid, args, offset=offset, limit=limit, order=order,
        context=context, count=count, access_rights_uid=access_rights_uid)
    
    def set_void(self, cr, uid, ids, context=None):
        """
        @comment sets the status to void
        @return boolean True or False
        """
         
        pool = self.pool.get
         
        br_id = self.get_branch_id(cr, uid, [0])
         
        rec = self.read(cr, uid, ids, ['crs_id','branch_id','state'])
         
        for recs in self.browse(cr, uid, ids, context=None):
            crs_id = recs.crs_id.id
            br_id = recs.branch_id.id   
             
        or_found = pool('config.receipts_series_det').search(cr,uid,[('crs_id','=',crs_id),('branch_id','=',br_id)])
        if not or_found: 
            raise ValidationError("Error", 'Validation Message - OR does not exist!')
         
        #Check State
        if rec[0]['state'] == 'unused':
            #state is draft
            self.write(cr, uid, ids[0], {'state':'void'})
        elif rec[0]['state'] == 'void':
            #state is void
            raise ValidationError("Error", 'Validation Message - State is already void')
         
        return True

    

    
     

        
