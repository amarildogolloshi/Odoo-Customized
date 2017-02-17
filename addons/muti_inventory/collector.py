from openerp import models, fields, api, exceptions
import openerp
from datetime import timedelta,time,date,datetime
from dateutil import parser
from openerp.osv import osv
from openerp.exceptions import ValidationError



class config_collectors(models.Model):
    _inherit = 'config.collectors'
    
    branch = fields.Many2one(related='name.branch_id')
    
   
class config_collectors_barangay(models.Model):
    _inherit = 'config.collectors.barangay'
    

class config_brgy_assigment(models.Model):
    _inherit = 'config.brgy.assignment'

    @api.onchange('branch_id')
    def _onchange_branch(self):
        selected_branch_id = self.branch_id.id
        collector_list = self.env['config.collectors'].search([('branch','=',selected_branch_id)])
        
        c_list =[]
          
        for r in collector_list:
            c_list.append(r.id)
          
        return{'domain':{'collector_id':[('id','in',c_list)]},
                   }
        
    