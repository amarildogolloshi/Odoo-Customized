from openerp import models, fields, api, exceptions

class Warehouse(models.Model):
    _inherit = 'stock.warehouse'

    branch_id = fields.Many2one('config.branch',string='Branch')