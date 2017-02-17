import time
from openerp import models, fields, api, tools
from openerp.tools.translate import _
from openerp.exceptions import Warning, ValidationError # osv.osv_except replacement

# def _code_get(self, cr, uid, context={}):
#     cr.execute('select prefix, document from config_document_number_format')
#     return cr.fetchall()

class sequence(models.Model):
    _name = 'sequence'
    _order = 'name'

    def _code_selection(self, *args, **kwargs):
        self._cr.execute('select prefix, document from config_document_number_format')
        return self._cr.fetchall()

    def _get_company_id(self):
        return self.env['res.company']._company_default_get('ir.sequence')

    name = fields.Char(string='Name', size=64, required=True)
    code = fields.Selection(selection=_code_selection, string='Code', size=64, required=True)
    active = fields.Boolean(string='Active', default=True)
    prefix = fields.Char(string='Prefix', size=64, help="Prefix value of the record for the sequence")
    suffix = fields.Char(string='Suffix', size=64, help="Suffix value of the record for the sequence")
    number_next = fields.Integer(string='Next Number', default=1, required=True, help="Next number of this sequence")
    number_increment = fields.Integer('Increment Number', default=1, required=True, help="The next number of the sequence will be incremented by this number")
    padding = fields.Integer(string='Number padding', default=0, required=True, help="OpenERP will automatically adds some '0' on the left of the 'Next Number' to get the required padding size.")
    company_id = fields.Many2one(comodel_name='res.company', string='Company', default=_get_company_id)
    branch_id = fields.Many2one(comodel_name='config.branch', string='Branch')
    dyear = fields.Char(string='Year', size=4)

    def _process(self, s, branch, d_year):
        return (s or '') % {
            'year':time.strftime('%Y'),
            'month': time.strftime('%m'),
            'day':time.strftime('%d'),
            'y': d_year[2:4],
            'doy': time.strftime('%j'),
            'woy': time.strftime('%W'),
            'weekday': time.strftime('%w'),
            'h24': time.strftime('%H'),
            'h12': time.strftime('%I'),
            'min': time.strftime('%M'),
            'sec': time.strftime('%S'),
            'branch': branch,
        }

    def get_id(self, document, branch_id, d_year, context=None):
        branch = None
        sql = '''SELECT id, number_next, prefix, suffix, padding
                      FROM sequence
                      WHERE name='%s'
                       AND active=true''' %  document
        if branch_id:
            branch = self.env['config.branch'].browse(branch_id).branch_code

            sql = sql + ' and branch_id=%s' % branch_id

        if d_year:
            sql = sql + " and dyear='%s'" % d_year

        sql = sql + " order by id"
        self._cr.execute(sql)
        res = self._cr.dictfetchone()
        if not res:
            rec = self.env['config.document.number.format'].search([('document', '=', document)])
            if not rec.id:
                raise Warning(_('Document sequence not found.'))
            self.create({'name': rec.document,
                'code': rec.prefix,
                'active': True,
                'prefix': rec.prefix,
                'suffix': '',
                'number_next': 1,
                'number_increment': 1,
                'padding' : rec.length_series,
                'branch_id': branch_id,
                'dyear' : d_year,
            })

            self._cr.execute(sql)
            res = self._cr.dictfetchone()

        if res:
            self._cr.execute(
                'UPDATE sequence SET number_next=number_next+number_increment WHERE id=%s AND active=true',
                (res['id'],)
            )
            if res['number_next']:
                return self._process(res['prefix'], branch, d_year) + '%%0%sd' % res['padding'] % res['number_next'] + self._process(res['suffix'], branch, d_year)
            else:
                return self._process(res['prefix']) + self._process(res['suffix'], branch, d_year)
        return False

    def get(self, cr, uid, code):
        return self.get_id(cr, uid, code, test='code')