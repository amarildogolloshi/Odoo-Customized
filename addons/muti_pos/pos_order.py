from openerp import models, fields, api

from functools import partial

class pos_order(models.Model):
    _inherit = 'pos.order'
    
    sales_clerk = fields.Many2one('res.users')
    checker = fields.Many2one('res.users')
    
    def _order_fields(self, cr, uid, ui_order, context=None):
        process_line = partial(self.pool['pos.order.line']._order_line_fields, cr, uid, context=context)
        return {
            'name':         ui_order['name'],
            'user_id':      ui_order['user_id'] or False,
            'sales_clerk':      ui_order['sales_clerk'] or False,
            'checker':      ui_order['checker'] or False,
            'session_id':   ui_order['pos_session_id'],
            'lines':        [process_line(l) for l in ui_order['lines']] if ui_order['lines'] else False,
            'pos_reference':ui_order['name'],
            'partner_id':   ui_order['partner_id'] or False,
            'date_order':   ui_order['creation_date'],
            'fiscal_position_id': ui_order['fiscal_position_id']
        }