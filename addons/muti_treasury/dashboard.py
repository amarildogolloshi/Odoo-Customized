from openerp import models, fields, api

class dashboard(models.Model):
    _inherit = 'board.board'
    
    def _search(self, cr, uid, args, offset=0, limit=None, order=None,
        context={}, count=False, access_rights_uid=None):
        user = uid
        print 'user', user
        print 'context', context
                  
        return super(dashboard, self)._search(cr, uid, args, offset=offset, limit=limit, order=order,
         context=context, count=count, access_rights_uid=access_rights_uid)