#from osv import osv, fields
from openerp.osv import fields, osv

from datetime import *
from time import strptime
import math
import calendar
import xmlrpclib

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
from email.utils import COMMASPACE, formatdate
import smtplib


class XmlRpcConn(object):
    def __init__ (self):
        self.uid = 0
        self.sock_id = 0
        self.dbname = ''
        self.passwd = ''
        self.connectRPC(db='EPFC', user='admin', passwd='p4wned')
    
    def connectRPC(self, db, user, passwd):
        self.dbname = db
        self.passwd = passwd
        
        sock_common = xmlrpclib.ServerProxy ('http://localhost:8069/xmlrpc/common')

        self.uid = sock_common.login(db, user, passwd)
        self.sock_id = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')
        
        
    def executeRPC(self, mode, model_name, data):
        '''
        mode - create, read, search
        model_name - table name
        data - parameters of mode
        '''
        if mode in ('write','read'):
            result = self.sock_id.execute(self.dbname, self.uid, self.passwd, model_name, mode, data['id'], data['data'])
        elif mode == 'read':
            result = self.sock_id.execute(self.dbname, self.uid, self.passwd, model_name, mode, data['id'], data['data'])
        elif mode == 'get_id':
            result = self.sock_id.execute(self.dbname, self.uid, self.passwd, model_name, mode, data['document'], data['branch_id'], data['year'])
        elif mode == 'onchange_amount':
            result = self.sock_id.execute(self.dbname, self.uid, self.passwd, model_name, mode, data['id'], 
                                          data['loan_id'],
                                          data['is_fieldcollection'],
                                          data['cash_tendered'],
                                          data['cash'],
                                          data['total_check_amount'],
                                          data['maturity_surcharge'],
                                          data['matsur_prev_bal'],
                                          data['transaction_date'],
                                          )
        elif mode == 'set_confirm':
            result = self.sock_id.execute(self.dbname, self.uid, self.passwd, model_name, mode, data)
        elif mode == 'ps_state':
            result = self.sock_id.execute(self.dbname, self.uid, self.passwd, model_name, mode, data['lr_id'], data['dte'])
        else: #search
            result = self.sock_id.execute(self.dbname, self.uid, self.passwd, model_name, mode, data)
            
        return result        


def _save_logs(self, cr, uid, model, encoder, rec_id, vals):

    rec = self.pool.get('ir.model').search(cr, uid, [('model','=',model)])
    
    if isinstance(rec_id, list):
        rec_id = rec_id[0]
    
    self.pool.get('config.logs').create(cr, uid, {
            'encoder' : encoder,
            'rec_id': rec_id,
            'vals': vals,
            'model': rec[0],
            })    

    return True

def _save_sched_logs(self, cr, uid, message, process, process_date):
    
    self.pool.get('config.sched.logs').create(cr, uid, {
            'message' : message,
            'process': process,
            'process_date': process_date,
            })    

    return True

def _get_client_id(self, cr, uid, loan_id):
    if not loan_id:
        return False
    
    release_obj = self.pool.get('loan.loan.release')
    loan_obj = self.pool.get('loan.loan')
    
    release_det = release_obj.read(cr, uid, loan_id, ['loan_id'])
                
    client_det = loan_obj.read(cr, uid, release_det['loan_id'][0], ['client_id']) 
    
    return client_det['client_id'][0]

def _get_collector(self, cr, uid, loan_id):
    if not loan_id:
        return False
    
    loan_rel_obj = self.pool.get('loan.loan.release')
    
    loan_rec = loan_rel_obj.read(cr, uid, loan_id,['branch_id','barangay_id'])
    branch_id = loan_rec['branch_id'][0]
        
    if not loan_rec['barangay_id']:
        raise osv.except_osv("Error", 'Validation Message : ERROR 0031: Client Information has no address.')
        return False
    
    brgy_id = loan_rec['barangay_id'][0]
    
    sql_req= """
            select config_collectors.name
                from config_collectors, config_collectors_barangay
                where config_collectors.id = config_collectors_barangay.collector_id
                and config_collectors.branch = %s
                and config_collectors_barangay.barangay_id = %s
            """ % (branch_id, brgy_id)
    cr.execute(sql_req)
    sql_res = cr.dictfetchall()
    
    if not sql_res:
        raise osv.except_osv("Error", "Validation Message : ERROR 0032: No assigned collector for the client's address")
        return False        
    else:
        if len(sql_res) <> 1:
            raise osv.except_osv("Error", "Validation Message : ERROR 0033: CI Officer conflict. Barangay was assigned to 2 or more officers.")
            return False
        else:
            collector = sql_res[0]['name']

    return collector

def _get_collector2(self, cr, uid, branch_id, client_id):
    if not client_id:
        return False
    
    partner_obj = self.pool.get('res.partner')
   
    client_id = client_id 
    branch_id = branch_id
    
    brgy = partner_obj.read(cr, uid, client_id,['barangay_id'])
        
    if not brgy['barangay_id']:
        raise osv.except_osv("Error", 'Validation Message : ERROR 0034: Client Information has no address.')
        return False
    
    brgy_id = brgy['barangay_id'][0]
    
    sql_req= """
            select config_collectors.name
                from config_collectors, config_collectors_barangay
                where config_collectors.id = config_collectors_barangay.collector_id
                and config_collectors.branch = %s
                and config_collectors_barangay.barangay_id = %s
            """ % (branch_id, brgy_id)
    cr.execute(sql_req)
    sql_res = cr.dictfetchall()
    
    if not sql_res:
        raise osv.except_osv("Error", "Validation Message : ERROR 0035: No assigned collector for the client's address")
        return False        
    else:
        if len(sql_res) <> 1:
            raise osv.except_osv("Error", "Validation Message : ERROR 0036: CI Officer conflict. Barangay was assigned to 2 or more officers.")
            return False
        else:
            collector = sql_res[0]['name']

    return collector
    
def _get_period(self, cr, uid, context=None):
    if context is None: context = {}
    if context.get('period_id', False):
        return context.get('period_id')
    if context.get('invoice_id', False):
        company_id = self.pool.get('account.invoice').browse(cr, uid, context['invoice_id'], context=context)
        context.update({'company_id': company_id.id})
    if type(uid) is list:
        user_id = uid[0]
    else:
        user_id = uid
    periods = self.pool.get('account.period').find(cr, user_id, context=context)
    return periods and periods[0] or False

def _get_startof_next_month(self, sourcedate, months):
    '''
    @comment returns the First Day of Next Month
    @param date sourcedate
    @param integer months
    @return date (first day of the ffg month)
    '''
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month / 12
    month = month % 12 + 1
    day = 1
   
    x_dte = str(year) + "-" + str(month) + "-" + str(day)
   
    return datetime.strptime(x_dte, "%Y-%m-%d")


def _get_matsur(self, cr, uid, loan_id, docdate):
    if not loan_id:
        return 0.00, 0.00
    
    mat_sur = 0.00
    matsur_bal = 0.00
    
    matsur_obj = self.pool.get('loan.maturity.surcharges')
    paysched_obj = self.pool.get('loan.payment.schedule')
    grace_period = self.pool.get('config.grace.period')
    matsur_rate = self.pool.get('config.maturity.surcharge.rate')
    
    #validate if under grace_period
    lastdue_recs = paysched_obj.search(cr,uid, [('loan_release_id',"=",loan_id),('due_date','!=',False)], order="due_date desc")
    if lastdue_recs:
        for lastdue_rec in lastdue_recs:
            ld_rec = paysched_obj.read(cr,uid,lastdue_rec,['due_date','branch_id'])
            last_due = ld_rec['due_date']
            br_id = ld_rec['branch_id'][0]
            break
        
        res_grace_period = grace_period.search(cr, uid, [('active','=',True)])
            
        grace_period = grace_period.read(cr, uid, res_grace_period[0], ['grace_period'])
        grace_period_val = grace_period['grace_period']

        if type(docdate) is str:
            date_now = docdate[:10]
        else:
            date_now = docdate.strftime('%Y-%m-%d')
                
        end_of_gp = datetime.strptime(last_due, "%Y-%m-%d") + timedelta(grace_period_val) 
        end_of_gp = end_of_gp.strftime('%Y-%m-%d')
        
        if end_of_gp >= date_now:
            return mat_sur, 0.00
        
        #get start date
        mat_recs = matsur_obj.search(cr, uid, [('loan_id','=',loan_id)], order="date_generated desc")
        if mat_recs:
            for mat_rec in mat_recs:
                start_rec = matsur_obj.read(cr, uid, mat_rec, ['date_generated'])
                start_date = datetime.strptime(start_rec['date_generated'][:10], "%Y-%m-%d") + timedelta(1)
                last_gen =  start_rec['date_generated'][:10]
                break
        
        else:
            #if no previous records, start_date is last_due + 1
            start_date = datetime.strptime(last_due, "%Y-%m-%d") + timedelta(1) 
            last_gen = last_due
        
        if last_gen == date_now:
            #get the existing balance
            mat_sur = 0.00
        else:    
            num_of_days = datetime.strptime(date_now, "%Y-%m-%d") - start_date + timedelta(1) 
        
            #compute maturity surcharge
            
            #get outstanding balance
            outstanding_balance = 0.00
            bal_recs = paysched_obj.search(cr,uid, [('loan_release_id',"=",loan_id),('principal_balance','!=',0.00)])
            if bal_recs:
                for bal_rec in bal_recs:
                    bal = paysched_obj.read(cr,uid,bal_rec,['principal_balance'])
                    outstanding_balance += bal['principal_balance']
            
            #get mat sur rate
            mat_rate_recs = matsur_rate.search(cr, uid, [('active','=',True),('branch_id','=',br_id)])
            if not mat_rate_recs:
                raise osv.except_osv("Error", 'Validation Message : ERROR 0037: No Maturity Surcharge Rate for the branch.')
                            
            surch = matsur_rate.read(cr, uid, mat_rate_recs[0], ['maturity_surcharge_rate'])
            mat_surcharge_rate = surch['maturity_surcharge_rate']
                                
            mat_sur = (outstanding_balance * (mat_surcharge_rate/100)) * num_of_days.days / 30
        
        #get previous mat sur balance
        
        mat_recs = matsur_obj.search(cr, uid, [('loan_id','=',loan_id)])
        if mat_recs:
            for mat_rec in mat_recs:
                matsur = matsur_obj.read(cr, uid, mat_rec, ['matsur','matsur_paid'])
                matsur_bal = matsur_bal +  matsur['matsur'] - matsur['matsur_paid']
           
    return math.ceil(mat_sur), matsur_bal

def _get_auto_user(self, cr, uid):
    
    if type(uid) is list:
        usr_id = uid[0]
    else:
        usr_id = uid
        
    user_obj = self.pool.get('res.users')

    usr = user_obj.search(cr,usr_id, [('name','=','auto_user')])
    if usr:
        usr_id = usr[0]
    
    return usr_id

def _get_interest_rate(self,cr,uid,trans_date, branch_id, brand_id, model_id, is_repo, term, fincost,product_id):
    int_rate = 0
    rebate = 0.00
    promo_id = None
    
    vec_type_id = self.pool.get('product.product').read(cr,uid,product_id,['type_id'])['type_id'][0]
    
    vec_type = self.pool.get('product.type').read(cr,uid,vec_type_id,['name'])['name']
    
    trans_date = trans_date[:10]

    #for regular transactions
    recs = self.pool.get('config.interest.rate').search(cr, uid, [('active','=',True),('branch_id','=',branch_id)])
    for rec in recs:
        res = self.pool.get('config.interest.rate').browse(cr, uid, rec)
        if res:
            if is_repo == True:
                int_rate = res['rate_repo']
            else:
                int_rate = res['rate_brandnew']
        else:
            raise osv.except_osv("Action", 'Validation Message : ERROR 00073: No Interest Rate configuration found.')
            return False    
    
    if is_repo == False:
        #for priority 1
        recs = self.pool.get('config.interest.rate.promo').search(cr, uid, 
                              [('active','=',True),
                               ('branch_id','=',branch_id), ('brand_id','=',brand_id), ('model_id','=',model_id),
                               ('start_date','<=',trans_date),('end_date','>=',trans_date),
                               ('term_from','<=',term),('term_to','>=',term),('finance_cost','<=',fincost),('is_repo','=',is_repo),
                               ('promo_for','in',('ALL',vec_type))])
        if recs:
            int_rate = self.pool.get('config.interest.rate.promo').read(cr,uid,recs[0],['rate_brandnew'])['rate_brandnew']
            rebate = self.pool.get('config.interest.rate.promo').read(cr,uid,recs[0],['rebate_brandnew'])['rebate_brandnew']
            promo_id = recs[0]
        else:
            #for priority 2
            recs = self.pool.get('config.interest.rate.promo').search(cr, uid, 
                                  [('active','=',True),
                                   ('branch_id','=',branch_id), ('brand_id','=',brand_id), ('model_id','=',False),
                                   ('start_date','<=',trans_date),('end_date','>=',trans_date),
                                   ('term_from','<=',term),('term_to','>=',term),('finance_cost','<=',fincost),('is_repo','=',is_repo),
                                   ('promo_for','in',('ALL',vec_type))])
            if recs:
                int_rate = self.pool.get('config.interest.rate.promo').read(cr,uid,recs[0],['rate_brandnew'])['rate_brandnew']
                rebate = self.pool.get('config.interest.rate.promo').read(cr,uid,recs[0],['rebate_brandnew'])['rebate_brandnew']
                promo_id = recs[0]                
            else:
                #for priority 3
                recs = self.pool.get('config.interest.rate.promo').search(cr, uid, 
                                      [('active','=',True),
                                       ('branch_id','=',branch_id), ('brand_id','=',False), ('model_id','=',False),
                                       ('start_date','<=',trans_date),('end_date','>=',trans_date),
                                       ('term_from','<=',term),('term_to','>=',term),('finance_cost','<=',fincost),('is_repo','=',is_repo),
                                       ('promo_for','in',('ALL',vec_type))])
                if recs:
                    int_rate = self.pool.get('config.interest.rate.promo').read(cr,uid,recs[0],['rate_brandnew'])['rate_brandnew']
                    rebate = self.pool.get('config.interest.rate.promo').read(cr,uid,recs[0],['rebate_brandnew'])['rebate_brandnew']
                    promo_id = recs[0]       
                else:
                    #for priority 4
                    recs = self.pool.get('config.interest.rate.promo').search(cr, uid, 
                                          [('active','=',True),
                                           ('branch_id','=',False), ('brand_id','=',brand_id), ('model_id','=',model_id),
                                           ('start_date','<=',trans_date),('end_date','>=',trans_date),
                                           ('term_from','<=',term),('term_to','>=',term),('finance_cost','<=',fincost),('is_repo','=',is_repo),
                                           ('promo_for','in',('ALL',vec_type))])
                    if recs:
                        int_rate = self.pool.get('config.interest.rate.promo').read(cr,uid,recs[0],['rate_brandnew'])['rate_brandnew']
                        rebate = self.pool.get('config.interest.rate.promo').read(cr,uid,recs[0],['rebate_brandnew'])['rebate_brandnew']
                        promo_id = recs[0]                 
                    else:
                        #for priority 5
                        recs = self.pool.get('config.interest.rate.promo').search(cr, uid, 
                                              [('active','=',True),
                                               ('branch_id','=',False), ('brand_id','=',brand_id), ('model_id','=',False),
                                               ('start_date','<=',trans_date),('end_date','>=',trans_date),
                                               ('term_from','<=',term),('term_to','>=',term),('finance_cost','<=',fincost),('is_repo','=',is_repo),
                                               ('promo_for','in',('ALL',vec_type))])
                        if recs:
                            int_rate = self.pool.get('config.interest.rate.promo').read(cr,uid,recs[0],['rate_brandnew'])['rate_brandnew']
                            rebate = self.pool.get('config.interest.rate.promo').read(cr,uid,recs[0],['rebate_brandnew'])['rebate_brandnew']
                            promo_id = recs[0]                      
                        else:
                            #for priority 6
                            recs = self.pool.get('config.interest.rate.promo').search(cr, uid, 
                                                  [('active','=',True),
                                                   ('branch_id','=',False), ('brand_id','=',False), ('model_id','=',False),
                                                   ('start_date','<=',trans_date),('end_date','>=',trans_date),
                                                   ('term_from','<=',term),('term_to','>=',term),('finance_cost','<=',fincost),('is_repo','=',is_repo),
                                                   ('promo_for','in',('ALL',vec_type))])
                            if recs:
                                int_rate = self.pool.get('config.interest.rate.promo').read(cr,uid,recs[0],['rate_brandnew'])['rate_brandnew']
                                rebate = self.pool.get('config.interest.rate.promo').read(cr,uid,recs[0],['rebate_brandnew'])['rebate_brandnew']
                                promo_id = recs[0]                      
    else:
        #for priority 1
        recs = self.pool.get('config.interest.rate.promo').search(cr, uid, 
                              [('active','=',True),
                               ('branch_id','=',branch_id), ('brand_id','=',brand_id), ('model_id','=',model_id),
                               ('start_date','<=',trans_date),('end_date','>=',trans_date),
                               ('term_from','<=',term),('term_to','>=',term),('finance_cost','<=',fincost),('is_repo','=',is_repo),
                               ('promo_for','in',('ALL',vec_type))])
        if recs:
            found = False
            for rec in recs:
                pr_rec = self.pool.get('config.interest.rate.promo').read(cr,uid,rec,['rate_repo','rebate_repo','engine_ids'])
                if pr_rec['engine_ids']:
                    if len(pr_rec['engine_ids']) != 0 :
                        srch = self.pool.get('config.interest.rate.promo.engine').search(cr,uid,[('promo_id','=',rec),('product_id','=',product_id)])
                        if srch:
                            int_rate = pr_rec['rate_repo']
                            rebate = pr_rec['rebate_repo']
                            promo_id = rec
                            found = True
                            break
            if not found:
                for rec in recs:
                    pr_rec = self.pool.get('config.interest.rate.promo').read(cr,uid,rec,['rate_repo','rebate_repo','engine_ids'])
                    if len(pr_rec['engine_ids']) == 0:
                        int_rate = pr_rec['rate_repo']
                        rebate = pr_rec['rebate_repo']
                        promo_id = rec
                        found = True
                        break    
        else:
            #for priority 2
            recs = self.pool.get('config.interest.rate.promo').search(cr, uid, 
                                  [('active','=',True),
                                   ('branch_id','=',branch_id), ('brand_id','=',brand_id), ('model_id','=',False),
                                   ('start_date','<=',trans_date),('end_date','>=',trans_date),
                                   ('term_from','<=',term),('term_to','>=',term),('finance_cost','<=',fincost),('is_repo','=',is_repo),
                                   ('promo_for','in',('ALL',vec_type))])
            if recs:
                found = False
                for rec in recs:
                    pr_rec = self.pool.get('config.interest.rate.promo').read(cr,uid,rec,['rate_repo','rebate_repo','engine_ids'])
                    if pr_rec['engine_ids']:
                        if len(pr_rec['engine_ids']) != 0 :
                            srch = self.pool.get('config.interest.rate.promo.engine').search(cr,uid,[('promo_id','=',rec),('product_id','=',product_id)])
                            if srch:
                                int_rate = pr_rec['rate_repo']
                                rebate = pr_rec['rebate_repo']
                                promo_id = rec
                                found = True
                                break
                if not found:
                    for rec in recs:
                        pr_rec = self.pool.get('config.interest.rate.promo').read(cr,uid,rec,['rate_repo','rebate_repo','engine_ids'])
                        if len(pr_rec['engine_ids']) == 0:
                            int_rate = pr_rec['rate_repo']
                            rebate = pr_rec['rebate_repo']
                            promo_id = rec
                            found = True
                            break                
            else:
                #for priority 3
                recs = self.pool.get('config.interest.rate.promo').search(cr, uid, 
                                      [('active','=',True),
                                       ('branch_id','=',branch_id), ('brand_id','=',False), ('model_id','=',False),
                                       ('start_date','<=',trans_date),('end_date','>=',trans_date),
                                       ('term_from','<=',term),('term_to','>=',term),('finance_cost','<=',fincost),('is_repo','=',is_repo),
                                       ('promo_for','in',('ALL',vec_type))])
                if recs:
                    found = False
                    for rec in recs:
                        pr_rec = self.pool.get('config.interest.rate.promo').read(cr,uid,rec,['rate_repo','rebate_repo','engine_ids'])
                        if pr_rec['engine_ids']:
                            if len(pr_rec['engine_ids']) != 0 :
                                srch = self.pool.get('config.interest.rate.promo.engine').search(cr,uid,[('promo_id','=',rec),('product_id','=',product_id)])
                                if srch:
                                    int_rate = pr_rec['rate_repo']
                                    rebate = pr_rec['rebate_repo']
                                    promo_id = rec
                                    found = True
                                    break
                    if not found:
                        for rec in recs:
                            pr_rec = self.pool.get('config.interest.rate.promo').read(cr,uid,rec,['rate_repo','rebate_repo','engine_ids'])
                            if len(pr_rec['engine_ids']) == 0:
                                int_rate = pr_rec['rate_repo']
                                rebate = pr_rec['rebate_repo']
                                promo_id = rec
                                found = True
                                break      
                else:
                    #for priority 4
                    recs = self.pool.get('config.interest.rate.promo').search(cr, uid, 
                                          [('active','=',True),
                                           ('branch_id','=',False), ('brand_id','=',brand_id), ('model_id','=',model_id),
                                           ('start_date','<=',trans_date),('end_date','>=',trans_date),
                                           ('term_from','<=',term),('term_to','>=',term),('finance_cost','<=',fincost),('is_repo','=',is_repo),
                                           ('promo_for','in',('ALL',vec_type))])
                    if recs:
                        found = False
                        for rec in recs:
                            pr_rec = self.pool.get('config.interest.rate.promo').read(cr,uid,rec,['rate_repo','rebate_repo','engine_ids'])
                            if pr_rec['engine_ids']:
                                if len(pr_rec['engine_ids']) != 0 :
                                    srch = self.pool.get('config.interest.rate.promo.engine').search(cr,uid,[('promo_id','=',rec),('product_id','=',product_id)])
                                    if srch:
                                        int_rate = pr_rec['rate_repo']
                                        rebate = pr_rec['rebate_repo']
                                        promo_id = rec
                                        found = True
                                        break
                        if not found:
                            for rec in recs:
                                pr_rec = self.pool.get('config.interest.rate.promo').read(cr,uid,rec,['rate_repo','rebate_repo','engine_ids'])
                                if len(pr_rec['engine_ids']) == 0:
                                    int_rate = pr_rec['rate_repo']
                                    rebate = pr_rec['rebate_repo']
                                    promo_id = rec
                                    found = True
                                    break                      
                    else:
                        #for priority 5
                        recs = self.pool.get('config.interest.rate.promo').search(cr, uid, 
                                              [('active','=',True),
                                               ('branch_id','=',False), ('brand_id','=',brand_id), ('model_id','=',False),
                                               ('start_date','<=',trans_date),('end_date','>=',trans_date),
                                               ('term_from','<=',term),('term_to','>=',term),('finance_cost','<=',fincost),('is_repo','=',is_repo),
                                               ('promo_for','in',('ALL',vec_type))])
                        if recs:
                            found = False
                            for rec in recs:
                                pr_rec = self.pool.get('config.interest.rate.promo').read(cr,uid,rec,['rate_repo','rebate_repo','engine_ids'])
                                if pr_rec['engine_ids']:
                                    if len(pr_rec['engine_ids']) != 0 :
                                        srch = self.pool.get('config.interest.rate.promo.engine').search(cr,uid,[('promo_id','=',rec),('product_id','=',product_id)])
                                        if srch:
                                            int_rate = pr_rec['rate_repo']
                                            rebate = pr_rec['rebate_repo']
                                            promo_id = rec
                                            found = True
                                            break
                            if not found:
                                for rec in recs:
                                    pr_rec = self.pool.get('config.interest.rate.promo').read(cr,uid,rec,['rate_repo','rebate_repo','engine_ids'])
                                    if len(pr_rec['engine_ids']) == 0:
                                        int_rate = pr_rec['rate_repo']
                                        rebate = pr_rec['rebate_repo']
                                        promo_id = rec
                                        found = True
                                        break                         
                        else:
                            #for priority 6
                            recs = self.pool.get('config.interest.rate.promo').search(cr, uid, 
                                                  [('active','=',True),
                                                   ('branch_id','=',False), ('brand_id','=',False), ('model_id','=',False),
                                                   ('start_date','<=',trans_date),('end_date','>=',trans_date),
                                                   ('term_from','<=',term),('term_to','>=',term),('finance_cost','<=',fincost),('is_repo','=',is_repo),
                                                   ('promo_for','in',('ALL',vec_type))])
                            if recs:
                                found = False
                                for rec in recs:
                                    pr_rec = self.pool.get('config.interest.rate.promo').read(cr,uid,rec,['rate_repo','rebate_repo','engine_ids'])
                                    if pr_rec['engine_ids']:
                                        if len(pr_rec['engine_ids']) != 0 :
                                            srch = self.pool.get('config.interest.rate.promo.engine').search(cr,uid,[('promo_id','=',rec),('product_id','=',product_id)])
                                            if srch:
                                                int_rate = pr_rec['rate_repo']
                                                rebate = pr_rec['rebate_repo']
                                                promo_id = rec
                                                found = True
                                                break
                                if not found:
                                    for rec in recs:
                                        pr_rec = self.pool.get('config.interest.rate.promo').read(cr,uid,rec,['rate_repo','rebate_repo','engine_ids'])
                                        if len(pr_rec['engine_ids']) == 0:
                                            int_rate = pr_rec['rate_repo']
                                            rebate = pr_rec['rebate_repo']
                                            promo_id = rec
                                            found = True
                                            break          
                                        
    int_rate = float(int_rate) / 100.00          
    
    #no rebate for terms 1 to 4 redmine 1551
    if term <= 4:
        rebate = 0
    
    return int_rate, rebate, promo_id

def _mo_amort(self, cr, uid, inq_term, inq_downpayment, inq_cash_price, inq_loan_price, is_repo, trans_date, branch, brand, model, product_id):  
    monthly_amort = 0
    reb = 0
    branch_id = self._get_branch_id(cr, uid, [0])   
    
    if not inq_term:
        return 0,0, None
    
    sql_res = """
    SELECT brandnewamount, repoamount
    FROM config_rebates
    WHERE
      (active = True)
      and branch_id = %s
    """ % (branch_id)

    cr.execute(sql_res)
    sql_res = cr.dictfetchone()

    if sql_res:
        if is_repo == True:
            reb = sql_res['repoamount']
        else:
            reb = sql_res['brandnewamount']
    else:
        raise osv.except_osv("Action", 'Validation Message : ERROR 0038: No rebate configuration found for the branch.')
        reb = False

    if inq_term:
        res = self.pool.get('config.payment.terms').browse(cr, uid, inq_term)
        xterm = res['term']

    fincost = inq_loan_price - inq_downpayment

    int_rate, rebs, promo_id = _get_interest_rate(self,cr,uid,trans_date, branch, brand, model,is_repo,xterm,fincost, product_id)
    
    if promo_id:
        reb = rebs
        
    if not inq_downpayment:
        inq_downpayment = 0
        
    if xterm:
        if inq_loan_price:
            if xterm == 1: 
                monthly_amort =  inq_cash_price - inq_downpayment
            if xterm in (2,3,4):
                price = inq_cash_price - inq_downpayment
                if inq_downpayment >= (inq_cash_price/2):
                    monthly_amort =  math.ceil((price + (price * 0.03 * xterm)) / xterm)
                else:
                    monthly_amort =  math.ceil((price + (price * 0.05 * xterm)) / xterm)
            if xterm > 4:
                monthly_amort =  math.ceil(((inq_loan_price - inq_downpayment) * int_rate) / (1 - ((1 + int_rate)**(-xterm))))
            else:
                #terms 1 to 4 has no rebate redmine 1551
                reb = 0        
                
    return monthly_amort, reb, promo_id

def write_to_file (self, body):
    with open('/tmp/records.txt', "w") as fileObj:
        fileObj.write(body.encode('UTF-8'))
    fileObj.close()


def update_offline_dox(self):
    RpcConn = XmlRpcConn() # instanstiate our xmlrpc object

    '''
    mode - create, read, search
    model_name - table name
    data - parameters of mode
    '''
    
    #for purchase order
    modl = 'loan.purchase.order'
    dox = 'Purchase Order'
    recs = RpcConn.executeRPC('search', modl, [('po_number',"=",False)])    
    for rec in recs:
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['branch_id','application_date']}  )  
        year = ind_rec['application_date'][:4]
        br_id = ind_rec['branch_id'][0]
        seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
        result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'po_number':seq_number}})
        
    #for loan.mcreg.batch
    modl = 'loan.mcreg.batch'
    dox = 'MC Registration'
    recs = RpcConn.executeRPC('search', modl, [('name',"=",False)])    
    for rec in recs:
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['branch_id','generation_date']}  )  
        year = ind_rec['generation_date'][:4]
        br_id = ind_rec['branch_id'][0]
        seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
        result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'name':seq_number}})
        
    #for loan.mcreg.optional
    modl = 'loan.mcreg.optional'
    dox = 'MC Registration - Optional'
    recs = RpcConn.executeRPC('search', modl, [('name',"=",False)])    
    for rec in recs:
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['branch_id','generation_date']})  
        year = ind_rec['generation_date'][:4]
        br_id = ind_rec['branch_id'][0]
        seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
        result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'name':seq_number}})
        
    #for loan.mcreg.liquidation
    modl = 'loan.mcreg.liquidation'
    dox = 'MC Registration CA Liquidation'
    recs = RpcConn.executeRPC('search', modl, [('doc_number',"=",False)])    
    for rec in recs:
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['branch_id','transaction_date']})  
        year = ind_rec['transaction_date'][:4]
        br_id = ind_rec['branch_id'][0]
        seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
        result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'doc_number':seq_number}})

    #for loan.loan.release
    modl = 'loan.loan.release'
    dox = 'Delivery Confirmation Slip'
    recs = RpcConn.executeRPC('search', modl, [('dcs_number',"=",False)])    
    for rec in recs:
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['branch_id','dr_date']})  
        if ind_rec['dr_date']:
            year = ind_rec['dr_date'][:4]
            br_id = ind_rec['branch_id'][0]
            seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
            result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'dcs_number':seq_number}})

    #for loan.contract.cancellation.request
    modl = 'loan.contract.cancellation.request'
    dox = 'FCS Cancellation'
    recs = RpcConn.executeRPC('search', modl, [('ccr_number',"=",False)])    
    for rec in recs:
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['branch_id','ccr_date']})  
        year = ind_rec['ccr_date'][:4]
        br_id = ind_rec['branch_id'][0]
        seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
        result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'ccr_number':seq_number}})        
                
    #for cashier.repo.unit.return
    modl = 'cashier.repo.unit.return'
    dox = 'REPO-Cash Unit Return'
    recs = RpcConn.executeRPC('search', modl, [('urc_number',"=",False)])    
    for rec in recs:
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['branch_id','urc_date']})  
        year = ind_rec['urc_date'][:4]
        br_id = ind_rec['branch_id'][0]
        seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
        result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'urc_number':seq_number}})    

    #for cashier.repo.unit.return
    modl = 'cashier.check.encashment'
    dox = 'Check Encashment'
    recs = RpcConn.executeRPC('search', modl, [('doc_number',"=",False)])    
    for rec in recs:
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['branch_id','doc_date']})  
        year = ind_rec['doc_date'][:4]
        br_id = ind_rec['branch_id'][0]
        seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
        result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'doc_number':seq_number}})   
        
    #for loan.pretermination
    modl = 'loan.pretermination'
    dox = 'Pretermination'
    recs = RpcConn.executeRPC('search', modl, [('doc_number',"=",False)])    
    for rec in recs:
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['branch_id','transaction_date']})  
        year = ind_rec['transaction_date'][:4]
        br_id = ind_rec['branch_id'][0]
        seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
        result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'doc_number':seq_number}})   

    #for loan.change.term
    modl = 'loan.change.term'
    dox = 'Change Term'
    recs = RpcConn.executeRPC('search', modl, [('doc_number',"=",False)])    
    for rec in recs:
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['branch_id','transaction_date']})  
        year = ind_rec['transaction_date'][:4]
        br_id = ind_rec['branch_id'][0]
        seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
        result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'doc_number':seq_number}})   

    #for loan.other.adjustment
    modl = 'loan.other.adjustment'
    dox = 'Other Adjustment'
    recs = RpcConn.executeRPC('search', modl, [('doc_number',"=",False)])    
    for rec in recs:
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['branch_id','transaction_date']})  
        year = ind_rec['transaction_date'][:4]
        br_id = ind_rec['branch_id'][0]
        seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
        result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'doc_number':seq_number}})   
        
    #for loan.pretermination.comp
    modl = 'loan.pretermination.comp'
    dox = 'Pretermination Computation'
    recs = RpcConn.executeRPC('search', modl, [('doc_number',"=",False)])    
    for rec in recs:
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['branch_id','transaction_date']})  
        year = ind_rec['transaction_date'][:4]
        br_id = ind_rec['branch_id'][0]
        seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
        result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'doc_number':seq_number}})   

    #for loan.change.term.comp
    modl = 'loan.change.term.comp'
    dox = 'Change Term Computation'
    recs = RpcConn.executeRPC('search', modl, [('doc_number',"=",False)])    
    for rec in recs:
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['branch_id','transaction_date']})  
        year = ind_rec['transaction_date'][:4]
        br_id = ind_rec['branch_id'][0]
        seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
        result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'doc_number':seq_number}})   

    #for loan.repo.evaluation
    modl = 'loan.repo.evaluation'
    dox = 'Unit Repossession Slip'
    recs = RpcConn.executeRPC('search', modl, [('doc_number',"=",False)])    
    for rec in recs:
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['branch_id','create_date']})  
        year = ind_rec['create_date'][:4]
        br_id = ind_rec['branch_id'][0]
        seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
        result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'doc_number':seq_number}}) 

    #for unit.deposit.receipt
    modl = 'unit.deposit.receipt'
    dox = 'Unit Deposit Receipt'
    recs = RpcConn.executeRPC('search', modl, [('doc_number',"=",False)])    
    for rec in recs:
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['branch_id','transaction_date']})  
        year = ind_rec['transaction_date'][:4]
        br_id = ind_rec['branch_id'][0]
        seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
        result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'doc_number':seq_number}}) 
        
    #for unit.redemption
    modl = 'unit.redemption'
    dox = 'Unit Redemption'
    recs = RpcConn.executeRPC('search', modl, [('doc_number',"=",False)])    
    for rec in recs:
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['branch_id','doc_date']})  
        year = ind_rec['doc_date'][:4]
        br_id = ind_rec['branch_id'][0]
        seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
        result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'doc_number':seq_number}}) 
        
    #for loan.mc.repo.job.order
    modl = 'loan.mc.repo.job.order'
    dox = 'Job Order'
    recs = RpcConn.executeRPC('search', modl, [('jo_number',"=",False)])    
    for rec in recs:
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['branch_id','transaction_date']})  
        year = ind_rec['transaction_date'][:4]
        br_id = ind_rec['branch_id'][0]
        seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
        result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'jo_number':seq_number}}) 
                
    #for acctg.apv
    modl = 'acctg.apv'
    dox = 'Accounts Payable Voucher'
    recs = RpcConn.executeRPC('search', modl, [('doc_number',"=",False)])    
    for rec in recs:
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['branch_id','transaction_date']})  
        year = ind_rec['transaction_date'][:4]
        br_id = ind_rec['branch_id'][0]
        seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
        result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'doc_number':seq_number}}) 
    
    #for acctg.request.for.payment
    modl = 'acctg.request.for.payment'
    dox = 'Payment Request Voucher'
    recs = RpcConn.executeRPC('search', modl, [('rfp_number',"=",False)])    
    for rec in recs:
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['branch_id','rfp_date']})  
        year = ind_rec['rfp_date'][:4]
        br_id = ind_rec['branch_id'][0]
        seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
        result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'rfp_number':seq_number}}) 

    #for acctg.petty.cash
    modl = 'acctg.petty.cash'
    dox = 'Petty Cash Fund Summary'
    recs = RpcConn.executeRPC('search', modl, [('doc_number',"=",False)])    
    for rec in recs:
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['branch_id','create_date']})  
        year = ind_rec['create_date'][:4]
        br_id = ind_rec['branch_id'][0]
        seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
        result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'doc_number':seq_number}}) 

    #for acctg.cash.advance.request
    modl = 'acctg.cash.advance.request'
    dox = 'Cash Advance Request'
    recs = RpcConn.executeRPC('search', modl, [('doc_number',"=",False)])    
    for rec in recs:
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['branch_id','doc_date']})  
        year = ind_rec['doc_date'][:4]
        br_id = ind_rec['branch_id'][0]
        seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
        result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'doc_number':seq_number}}) 

    #for account.move
    modl = 'account.move'
    recs = RpcConn.executeRPC('search', modl, [('name',"=",'/')])
    for rec in recs:
        dox = None
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['branch_id','date','transtype','je']})  
        year = ind_rec['date'][:4]
        br_id = ind_rec['branch_id'][0]
        
        if ind_rec['transtype'] in ('apv','apv2','fcs_cancel','fcs_cancel_ho','changeterm','ib_owner',
                                    'ib_central','loan_release','loan_release_co','loan_release_re',
                                    'mcregliq','other_loan_adj','othercol_dp','trans_owner_from',
                                    'trans_owner_to','trans_owner_ho','preterm','reconexp','repo',
                                    'rcs_cancel','rcs_cancel_ho'):
            dox = 'Journal Voucher'
        elif ind_rec['transtype'] in ('fincol','cashover','ib_collect','othercol','repocash'):
            dox = 'Cash Receipts Journal'
        elif ind_rec['transtype'] == 'cashshort' :
            dox = 'Cash Voucher'
        elif ind_rec['transtype'] in ('deposit_check','deposit'):
            dox = 'Deposit'
        elif ind_rec['transtype'] in ('deposit_ho','deposit_check_ho'):
            dox = 'Bank Transactions Journal'            
        elif ind_rec['transtype'] == 'reqpymt' :
            dox = 'Check Voucher'
        elif ind_rec['transtype'] == 'manual' :
            if ind_rec['je'] == 'jv':
                dox = 'Journal Voucher'
            elif ind_rec['je'] == 'btj': 
                dox = 'Bank Transactions Journal'
                
        if dox != None:
            seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
            try:
                result = RpcConn.executeRPC('write', modl, {'id': [rec], 'data':{'name':seq_number}}) 
            except:
                print 'Account Move No line Error Message %s' % rec
                continue

    #for acctg.request.for.payment for CV number
    modl = 'acctg.request.for.payment'
    recs = RpcConn.executeRPC('search', modl, [('cv_number',"=",'/')])    
    for rec in recs:
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['move_id']})
        if ind_rec['move_id']:
            move_id = ind_rec['move_id'][0]
            
            cv_rec = RpcConn.executeRPC('read', 'account.move', {'id': move_id, 'data':['name']})
            cv_num = cv_rec['name']
        
            result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'cv_number':cv_num}}) 
            
    #for stock.picking
    modl = 'stock.picking'
    recs = RpcConn.executeRPC('search', modl, [('doc_number',"=",False)])
    for rec in recs:
        dox = None
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['origin','to_branch_id','from_branch_id','date','doc_offline']})  
        year = ind_rec['date'][:4]
        
        if ind_rec['doc_offline'] == 'WS':
            dox = 'Withdrawal Slip'
            br_id = ind_rec['to_branch_id'][0]
        elif ind_rec['doc_offline'] == 'ATS':
            dox = 'Asset Transfer Slip'
            if ind_rec['origin']:
                if ind_rec['origin'][:3] in ('UDR','URS'):
                    br_id = ind_rec['to_branch_id'][0]
                else:
                    br_id = ind_rec['from_branch_id'][0]
            else:
                continue
        elif ind_rec['doc_offline'] == 'STR' :
            dox = 'Stock Transfer Request'
            br_id = ind_rec['to_branch_id'][0]
                
        if dox != None:
            seq_number = RpcConn.executeRPC('get_id','sequence', {'document': dox, 'branch_id': br_id, 'year':year})
            result = RpcConn.executeRPC('write', modl, {'id': [rec], 'data':{'doc_number':seq_number,'name':seq_number}}) 

        return True
    
def update_payment(self):
    RpcConn = XmlRpcConn() # instanstiate our xmlrpc object
    
    body_ = ''

    #check for conflict for Fin Coll
    modl = 'cashier.financing.collection'
    recs = RpcConn.executeRPC('search', modl, [('state','=','offline')])
    for rec in sorted(recs):
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['loan_id','or_date']})  
        loan_release_id = ind_rec['loan_id'][0]
        or_date = ind_rec['or_date']
        with_conflict, list_or = check_conflict(self,loan_release_id,or_date)
        if with_conflict:
            result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'state':'conflict'}})
            body_ += list_or
            continue 
        
        state_then = RpcConn.executeRPC('ps_state', 'loan.payment.schedule', {'lr_id':loan_release_id, 'dte': or_date})
        post_payment(self, rec, modl)
        state_then = RpcConn.executeRPC('ps_state', 'loan.payment.schedule', {'lr_id':loan_release_id, 'dte': datetime.now().strftime('%Y-%m-%d')})
                                                                                   
        
    #check for conflict for Inter-Branch Fin Coll
    modl = 'cashier.financing.collection.otherbranch'
    recs = RpcConn.executeRPC('search', modl, [('state','=','offline')])
    for rec in sorted(recs):
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['loan_id','or_date']})  
        loan_release_id = ind_rec['loan_id'][0]
        or_date = ind_rec['or_date']
        with_conflict, list_or = check_conflict(self, loan_release_id,or_date)
        if with_conflict:
            result = RpcConn.executeRPC('write', modl, {'id': rec, 'data':{'state':'conflict'}})
            body_ += list_or
            continue 
        
        state_then = RpcConn.executeRPC('ps_state', 'loan.payment.schedule', {'lr_id':loan_release_id, 'dte': or_date})
        post_payment(self, rec, modl)
        state_now = RpcConn.executeRPC('ps_state', 'loan.payment.schedule', {'lr_id':loan_release_id, 'dte': datetime.now().strftime('%Y-%m-%d')})
        
    print "body_: ", body_
    if body_ != '':
        write_to_file(self,body_)
    
        
    return True

def check_conflict(self, loan_release_id, or_date):
    RpcConn = XmlRpcConn() # instanstiate our xmlrpc object
    
    list_or = ''
    with_conflict = False
    counter = 0
    
    ind_rec = RpcConn.executeRPC('read', 'loan.loan.release', {'id': loan_release_id, 'data':['name']})
    list_or = ind_rec['name'] + '\n'
        
    #for Financing Collection
    modl = 'cashier.financing.collection'
    recs = RpcConn.executeRPC('search', modl, [('loan_id',"=",loan_release_id),('or_date','>=',or_date)])        
    for rec in recs:
        counter += 1
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['or_number','or_date']})
        list_or += "      FINCOL " + ind_rec['or_number'] + ' - ' + ind_rec['or_date'] + '\n'
    
    #for Financing Collection
    modl = 'cashier.financing.collection.otherbranch'
    recs = RpcConn.executeRPC('search', modl, [('loan_id',"=",loan_release_id),('or_date','>=',or_date)])        
    for rec in recs:
        counter += 1
        ind_rec = RpcConn.executeRPC('read', modl, {'id': rec, 'data':['or_number','or_date']})
        list_or += "      IBFINC " + ind_rec['or_number'] + ' - ' + ind_rec['or_date'] + '\n'

    if counter > 1:
        with_conflict = True
    
    return with_conflict, list_or
    
def post_payment(self, rec_id, modl):
    RpcConn = XmlRpcConn() # instanstiate our xmlrpc object
    
    ind_rec = RpcConn.executeRPC('read', modl, {'id': rec_id, 'data':['loan_id','is_fieldcollection',
                                                                    'cash_tendered','cash','total_check_amount',
                                                                    'maturity_surcharge','matsur_prev_bal','transaction_date']})
    
    #recompute breakdown
    recompute = RpcConn.executeRPC('onchange_amount', modl, {'id' : [rec_id],
                                                             'loan_id': ind_rec['loan_id'][0], 
                                                             'is_fieldcollection': ind_rec['is_fieldcollection'], 
                                                             'cash_tendered':ind_rec['cash_tendered'], 
                                                             'cash': ind_rec['cash'],
                                                             'total_check_amount' : ind_rec['total_check_amount'] , 
                                                             'maturity_surcharge' : ind_rec['maturity_surcharge'],
                                                             'matsur_prev_bal' : ind_rec['matsur_prev_bal'],
                                                             'transaction_date' : ind_rec['transaction_date'],
                                                             })
    
    confirm = RpcConn.executeRPC('set_confirm', modl, [rec_id])
        
    return True

def send_email (send_from, send_to, subject, body_msg, files=[], server='smtp.gmail.com', port=587):
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime = True)
    msg['Subject'] = subject    
    msg.attach(MIMEText(body_msg))
    for attach_file in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(attach_file,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(attach_file)))
        msg.attach(part)
    
    server = smtplib.SMTP(server, port)
    server.starttls()
    server.login("auberonsolutions", "$tabilized")
    server.sendmail(send_from, send_to, msg.as_string())    


         
 

        








