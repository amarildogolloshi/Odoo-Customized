# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import Warning, ValidationError # osv.osv_except replacement
from openerp.tools.translate import _


# class product_major_class(models.Model):
#     _name = 'product.major.class'
#     
#     @api.model
#     def create(self,vals):
#         vals['code'] = self.env['ir.sequence'].next_by_code('product.major.class')
#         return super(product_major_class, self).create(vals)
#         
#     code = fields.Char(string = 'Code', readonly = True)
#     active = fields.Boolean(string = 'Active', default = True)
#     name = fields.Char(string = 'Name', required = True)
#     make_id = fields.One2many('product.make','class_id',string = 'Make')
    

# class product_make(models.Model):
#     _name = 'product.make'
#     
#     @api.model
#     def create(self,vals):
#         vals['code'] = self.env['ir.sequence'].next_by_code('product.make')
#         return super(product_make, self).create(vals)
#     
#     code = fields.Char(string = 'Code', readonly = True)
#     class_id = fields.Many2one('product.major.class', string = 'Major Class')
#     name = fields.Char(string='Name', required = True)
#     old_make_code = fields.Char(string='Old Make Code', readonly=True)
#     active = fields.Boolean('Active', default=True)
#     group_id = fields.One2many('product.group','make_id', string = 'Group')
    
# class product_group(models.Model):
#     _name = 'product.group'
#     
# #     @api.model
# #     def create(self,vals):
# #         vals['code'] = self.env['ir.sequence'].next_by_code('product.group')
# #         return super(product_group, self).create(vals)
#     
#     code = fields.Char(string = 'Code', readonly = True)
# #     make_id = fields.Many2one('product.make', string = 'Make')
#     name = fields.Char(string='Name')
#     active = fields.Boolean('Active', default=True)
#     partgroup_id = fields.One2many('product.partgroup','group_id',string = 'Sub Group')
# #     _sql_constraints = [
# #         ('name_unique',
# #          'UNIQUE(name)',
# #          "Brand name must be unique"),
# #     ]

class product_category(models.Model):
    _inherit = 'product.category'

        
    
    @api.model
    def create(self, values):
        barcode_affix = values['barcode_affix'] if 'barcode_affix' in values else ''
        if values['parent_id']:
            parent_id = values['parent_id']
            browse_id = self.browse(parent_id)
            parent_group_code = browse_id.barcode_affix
            values['group_code'] = parent_group_code
            if parent_group_code:
                values['barcode_affix'] = str(parent_group_code) + str(barcode_affix)
            else:
                values['barcode_affix'] = str(barcode_affix)
            print values['barcode_affix']
        return super(product_category, self).create(values)
                
                
    barcode_affix = fields.Char(string = ' Barcode Affix')
    group_code = fields.Char(string = 'Group Code',readonly = True)
    group_ids = fields.One2many('product.template','group_id',string ="")

class product_model(models.Model):

    _name = 'product.model'
    vecmodel_id = fields.Char(
        string='Model ID',
        default=lambda self: self.env['ir.sequence'].get('model.seq')
    )
    brand_id = fields.Many2one('product.brand', 'Brand')
    name = fields.Char(string='Model')
    old_model_code = fields.Char(string='Old Model Code')
    active = fields.Boolean(string = 'Active', default=True)

   # _sql_constraints = [
   #     ('name_unique',
   #      'UNIQUE(name)',
   #      "Brand name must be unique"),
   #]

class product_brand(models.Model):
    _name = 'product.brand'

    @api.model
    def create(self,vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('product.brand')
        return super(product_brand, self).create(vals)

    def _brand_sequence(self):
        return self.env['ir.sequence'].get('brand.seq')

    brand_id = fields.Char(
        string='Brand ID',
        default=_brand_sequence
    )
    name = fields.Char(string='Brand Name')
    old_brand_code = fields.Char(string='Old Brand Code')
    active = fields.Boolean(string='Active', default=True)
    barcode_prefix = fields.Integer(string='Barcode prefix')
    # _sql_constraints = [
    #     ('name_unique',
    #      'UNIQUE(name)',
    #      "Brand name must be unique"),
    # ]




class product_color(models.Model):
    _name = 'product.color'

    veccolor_id = fields.Char(
        string='Color ID',
        default=lambda self: self.env['ir.sequence'].get('color.seq')
    )
    name = fields.Char(string='Color')
    old_color_code = fields.Char(string='Old Color Code', readonly=True)
    active = fields.Boolean('Active', default=True)

#     _sql_constraints = [
#         ('name_unique',
#          'UNIQUE(name)',
#          "Color must be unique"),
#     ]


class product_body(models.Model):
    _name = 'product.body'

    vecbody_id = fields.Char(
        string='Body ID',
        default=lambda self: self.env['ir.sequence'].get('body.seq')
    )
    name = fields.Char(string='Body Type')
    old_body_code = fields.Char(string='Old Body Code', readonly=True)
    active = fields.Boolean(string='Active', default=True)

#     _sql_constraints = [
#         ('name_unique',
#          'UNIQUE(name)',
#          "A record with the same name already exists."),
#     ]

class product_wheel(models.Model):
    _name = 'product.wheel'

    vecwheel_id = fields.Char(
        string='Wheel ID',
        default=lambda self: self.env['ir.sequence'].get('wheel.seq')
    )
    name = fields.Char(string='Wheel Type')
    old_wheel_code = fields.Char(string='Old Wheel Code', readonly=True)
    active = fields.Boolean(string='Active', default=True)
#     _sql_constraints = [
#         ('name_unique',
#          'UNIQUE(name)',
#          "A record with the same name already exists."),
#     ]


class product_transmission(models.Model):
    _name = 'product.transmission'

    vectrans_id = fields.Char(
        string='Transmission ID',
        default=lambda self: self.env['ir.sequence'].get('trans.seq')
    )
    name = fields.Char(string='Transmission Type')
    old_transmission_code = fields.Char(string='Old Transmission Code', readonly=True)
    active = fields.Boolean(string='Active', default=True)

#     _sql_constraints = [
#         ('name_unique',
#          'UNIQUE(name)',
#          'Transmission Type should be unique.'),
#     ]


class product_type(models.Model):
    _name = 'product.type'

    def _get_vectype_id(self):
        return self.env['ir.sequence'].get('trans.seq')

    vectype_id = fields.Char(
        string='Type ID',
        default=_get_vectype_id #lambda self: self.env['ir.sequence'].get('vectype.seq')
    )
    name = fields.Char(string='Vehicle Type')
    old_vehicle_code = fields.Char(string='Old Vehicle Code', readonly=True)
    active = fields.Boolean(string='Active', default=True)

#     _sql_constraints = [
#         ('name_unique',
#          'UNIQUE(name)',
#          'A record with the same name already exists.'),
#     ]


class product_minimum_dp(models.Model):
    _name = 'product.minimum.dp'
    product_id = fields.Many2one(comodel_name='product.product', string='Product', ondelete="cascade", required=True)
    branch_id = fields.Many2one(comodel_name='config.branch', string='Branch', ondelete="cascade", required=True)
    cash_price = fields.Float(string='Cash Price', digits=(16, 2))
    loan_price = fields.Float(string='Loan Price', digits=(16, 2))
    min_dp = fields.Float(string='Minimum DP', digits=(16, 2))
    active = fields.Boolean(string='Active')
    start_date = fields.Date(string='Start Date Effect', required=True)
    end_date = fields.Date(string='End Date Effect', required=True)
    wh_interest_promo_id = fields.Many2one('config.wh.interest.promo', string='Promo Id', ondelete="cascade")

    @api.model
    def create(self, values):
        res_id = super(product_minimum_dp, self).create(values)
        self.env['config.logs'].save_logs(self._name, res_id.id, values)
        return res_id

    @api.model
    def _write(self, cr, uid, ids, values, context=None):
        ids = super(product_minimum_dp, self)._write(ids, values, context)
        self.env['config.logs'].save_logs(self._name, ids, values)
        return ids


class product_mc_classification(models.Model):
    _name = 'product.mc.classification'
    _description = __doc__

    _rec_name = 'mc_classification'
    mc_classification = fields.Char(string='MC Classification', size=20)
    breaking_period = fields.Integer(string='Breaking Period', required=True)
    active = fields.Boolean(string='Active', default=True)
# 
#     @api.model
#     def create(self, values):
#         res_id = super(product_mc_classification, self).create(values)
#         self.env['config.logs'].save_logs(self._name, res_id, values)
#         return res_id

#     @api.model
#     def _write(self, cr, uid, ids, values, context=None):
#         ids = super(product_mc_classification, self)._write(cr, uid,  ids, values, context)
#         self.env['config.logs'].save_logs(self._name, ids, values)
#         return ids

    @api.one
    @api.constrains('or_amount')
    def check_breaking_period(self, cr, uid, ids, context=None):
        """
        @comment Function that checks if Breaking Period is valid - should be >= 30
        @return boolean True or False
        """
        cols = self.read(cr, uid, ids, ['breaking_period'])

        if cols[0]['breaking_period'] < 30:
            raise Warning(_('Breaking Period should be >= 30!'))
        
        
# class product_partgroup(models.Model):
#     
#     _name = 'product.partgroup'
#     
#      @api.model
#      def create(self,vals):
#          vals['code'] = self.env['ir.sequence'].next_by_code('product.partgroup')
#          return super(product_partgroup, self).create(vals)
#     
#     code = fields.Char(string = 'Code', readonly = True)
#     active = fields.Boolean(string = 'Active', default = True)
#      old_partgroup_code = fields.Char(string = 'Old Partgroup Code', readonly = True)
#     name = fields.Char(string = "Name", required = True)
#     group_id = fields.Many2one('product.group',string = 'Group')
    