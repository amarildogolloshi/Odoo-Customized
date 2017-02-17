from openerp import models, fields, api

class pos_config(models.Model):
    _inherit = 'pos.config'
    
    branch_id = fields.Many2one('config.branch',string = 'Branches', required = True)
