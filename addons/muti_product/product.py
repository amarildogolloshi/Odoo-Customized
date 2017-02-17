# -*- coding: utf-8 -*-

from openerp import models, fields, api


class product_template(models.Model):
    _inherit = 'product.template'

#     def _get_name(self):
#         name = self.name
#         barcode = self.barcode
#         ret_name = barcode + ' - ' + name
#         return ret_name

#     @api.multi
#     @api.depends('name', 'barcode')
#     def name_get(self):
#         res = []
#
#
#         for emp in self:
#
#             if emp.barcode == False:
#                 emp.barcode = ''
#             print emp.barcode,emp.name
#             res.append((emp.barcode + ' - ' + emp.name))
#
#         return res

    def _search(self, cr, uid, args, offset=0, limit=None, order=None,
        context={}, count=False, access_rights_uid=None):

        if context:
            if 'categ_name' in context:
                categ_id = self.pool.get('product.category').search(cr,uid,[('name','=',context['categ_name'])])
                args.append(("categ_id","in",categ_id))

        return super(product_template, self)._search(cr, uid, args, offset=offset, limit=limit, order=order,
         context=context, count=count, access_rights_uid=access_rights_uid)

    def _category_name(self,categ_name):
        search_id = self.env['product.category'].search([('name','=',categ_name)])
        if search_id:
            return search_id.id



    def _get_sale_ok(self):
        context = self._context
        if 'categ_name' in context:
            categ_name = context.get('categ_name')
#             categ_id = self._category_name(categ_name)
#             print categ_id
            if categ_name == 'Spareparts' or categ_name == "Motorcycle":
                val = 1
            else:
                val = 0
            print context
            return val

    def _get_type(self):
        context = self._context
        if 'categ_name' in context:
            categ_name = context.get('categ_name')
            if categ_name == 'Motorcycle' or categ_name == 'Spareparts' or categ_name =='Free':
                val = 'product'
            else:
                val = 'consu'
            print context
            return val

    def _get_zero_price(self):
        context = self._context
        if 'categ_name' in context:
            categ_name = context.get('categ_name')
            if categ_name == 'Free':
                val = 0.00
                return val

    def _default_category(self):
        context = self._context
        if 'categ_name' in context:
            default_id  =self._category_name(context.get('categ_name'))

            return default_id

    @api.one
    def _get_product_id(self):
        print 'test'
        res2 = []
        for rec in self.product_variant_ids:
            print rec.id
            search_id = self.env['product.pricelist.item'].search([('product_id','=',rec.id)])
            if search_id:
                for rec2 in search_id:
                    res2.append(rec2.id)
                print res2
        print self.env['product.pricelist.item'].browse(res2)
        self.price_history_ids = self.env['product.pricelist.item'].browse(res2)


    # prodname = fields.Char(string='Name')
    type_id = fields.Many2one(
        'product.type', string='Vehicle type', ondelete='cascade')
    group_id = fields.Many2one('product.category',string = 'Product Category')
    related_type = fields.Char(related='type_id.name', string='Type')
    brand_id = fields.Many2one(comodel_name='product.brand', string='Brand', ondelete='cascade')
    color_id = fields.Many2one(comodel_name='product.color', string='Color', ondelete='cascade')
    model_id = fields.Many2one(comodel_name='product.model', string='Model', ondelete='cascade')
    body_id = fields.Many2one(comodel_name='product.body', string='Body Type', ondelete='cascade')
    wheel_id = fields.Many2one(comodel_name='product.wheel', string='Wheel Type', ondelete="cascade")
    transmission_id = fields.Many2one(comodel_name='product.transmission', string='Transmission', ondelete="cascade")
    mc_classification_id = fields.Many2one(comodel_name='product.mc.classification',string = 'MC Classification',ondelete = "cascade")
    engineno = fields.Char(string='Engine No.')
    chassisno = fields.Char(string='Chassis No.')
    cash_price = fields.Float(string='Cash Price [COD]', digits=(16, 2))
    last_price = fields.Float(string='Last Price [LP]', digits=(16, 2))
    loan_price = fields.Float(string='Loan Price [LCP]', digits=(16, 2))
    unit_cost = fields.Float(string='Unit Cost [For Edit]', digits=(16, 2))
    rel_unit_cost = fields.Float(related='unit_cost', string='Unit Cost')
    min_dp = fields.Float(string='Minimum DP', digits=(16, 2))
    is_new =fields.Boolean(string='Brandnew')
    features = fields.Text(string='Features')
    is_repo = fields.Boolean(string='Repossessed?')
    is_depo = fields.Boolean(string='Unit Deposit?')
    is_sold_redeemed = fields.Boolean(string='Sold/Redeemed?')
    branch_id = fields.Many2one('config.branch', string='Branch Owner')
    in_transit = fields.Boolean(string='In Transit?')
    reference_doc = fields.Char(string='Reference Number', size=25)
    udr_id = fields.Many2one(comodel_name='unit.deposit.receipt', string='UDR'),
    repo_id = fields.Many2one(comodel_name='loan.repo.evaluation', string='REPO')
    repo_classification = fields.Selection([
        ('repo','Repossessed Unit'),
        ('service','Service Unit'),
        ('dismembered','Dismembered Unit'),
        ], string='Repo Classification', default='repo')
    assigned_to = fields.Many2one('res.users', string='Assigned To')
    previous_owner = fields.Char(string='Previous Owner', size=100)
    for_prev = fields.Char(compute='_get_prev', string='For Prev')
    move_ids = fields.One2many('stock.move', 'product_id', string='History')
    branch_owner = fields.Many2one('config.branch', string='Branch Owner')
    branch_location_id = fields.Many2one('stock.location', string='Location')
    mindp_ids = fields.One2many(comodel_name='product.minimum.dp', inverse_name='product_id', string='Minimum Downpayment')
#     spec_type = fields.Selection([('spare','Spareparts'),('mc','Motorcycle'),('nontrade','Non-Trade'),('free','Free Items')],string = 'Specification Type')
    is_net = fields.Boolean(string='Net', default = False)
    is_pnp_clear = fields.Boolean(string='For PNP Clearance')
    maximum_discount = fields.Float(string='Maximum Discount', digits=(16, 2))
    sale_ok = fields.Boolean(default=_get_sale_ok)
    type = fields.Selection(default=_get_type)
    product_ids = fields.Many2many(comodel_name='product.product', string='Free Items', domain=([('categ_name','=','Non-Trade')]))
    list_price = fields.Float(default=_get_zero_price)
#     addtldesc = fields.Char(string = "Additional Description")
    categ_id = fields.Many2one(default=_default_category)
    categ_name = fields.Char(string='Category Name', related='categ_id.name')
    commission = fields.Float(string='Commission', digits=(16,2))
    item_ids = fields.One2many(comodel_name='product.pricelist.item', inverse_name='product_id', string='Pricelist Items')
    price_history_ids = fields.Many2many(comodel_name='product.pricelist.item', compute='_get_product_id')
    old_barcode = fields.Char(string='Old Barcode', readonly = True)
    model_name = fields.Char(string ='Model')
    part_no = fields.Char(string='Part No.')
#     _sql_constraints = [
#         ('name_unique',
#          'UNIQUE(name)',
#          'Product Name already exist!')
#         ]

    @api.model
    def create(self, values):

        context = self._context
        search_id = self.env['product.category'].search([('id','=',values['categ_id'])])
        categ_ids = self.env['product.category'].browse(search_id.id)
        categ_name = context.get('categ_name')

        if categ_name == 'Motorcycle':
           if 'brand_id' in values:
               if values['brand_id'] <> False:
                   brand = self.env['product.brand'].browse(values['brand_id'])
                   brand_n = brand.name.strip()
               else:
                   brand_n = ''
           else:
               brand_n = ''


           if 'model_id' in values:
                   if values['model_id'] <> False:
                       model = self.env['product.model'].browse(values['model_id'])
                       model_n = model.name.strip()
                   else:
                       model_n =''
           else:
               model_n = ''


           if 'color_id' in values:
               if values['color_id'] <> False:
                   color = self.env['product.color'].browse(values['color_id'])
                   color_n = color.name.strip()
               else:
                   color_n =''
           else:
               color_n = ''

           values['name'] = brand_n + " | " + model_n + " | " + color_n
#                if values.has_key('is_repo'):
#                    if values['is_repo']:
#                        isrep = "(REPO) "
#                        values['name'] = 'REPO TEMPLATE'
#                    else:
#                        values['name'] = values['prodname']
#                if values.has_key('is_depo'):
#                    if values['is_depo']:
#                        isrep = "(DEPO) "
#                        values['name'] = 'DEPO TEMPLATE'

#                values['prodname'] = isrep + brand_n + " | " + model_n + " | " + color_n

    #         self.env['config.logs'].save_logs(self._name, res_id, values)
        if categ_name == 'Spareparts' or categ_ids.name == 'Spareparts':
            group_id = self.env['product.category'].browse(values['group_id']).barcode_affix
            seq_find = group_id
            search_seq = self.env['ir.sequence'].search([('code','=',seq_find)])
            if search_seq:
                inc_code = self.env['ir.sequence'].next_by_code(seq_find)
                values['barcode'] = str(group_id) + str(inc_code)
            else:
                self.env['ir.sequence'].create({'name':seq_find,'code':seq_find,'padding':4})
                inc_code = self.env['ir.sequence'].next_by_code(seq_find)
                values['barcode'] = str(group_id) + str(inc_code)
#             partgroup = self.env['product.partgroup'].browse(values['partgroup_id'])
#             partgroup_n = partgroup.name.strip()
#             values['name'] = partgroup_n + ' ' + values['addtldesc']
        res_id = super(product_template, self).create(values)
        return res_id

#     @api.model
#     def _write(self, values):
#         ids = super(product_template, self)._write(values)
# #         self.env['config.logs'].save_logs(self._name, ids, values)
#         return ids

    @api.onchange('branch_id')
    def onchange_branch_id(self):
        if not self.branch_id.id:
            self.branch_location_id = False
        else:
            self.branch_location_id = self.env['stock.warehouse'].search((['branch_id', '=', self.branch_id.id], )).lot_stock_id

    @api.onchange('type_id')
    def onchange_type_id(self):
        self.related_type = self.type_id.name

    @api.depends('reference_doc')
    def _get_prev(self):
        for r in self:
            ret = ''
            if not r.reference_doc or r.reference_doc == 'Beginning Balance' :
                ret = 'BB'
            r.for_prev = ret

    # def name_get(self, cr, user, ids, context=None):
    #     if context is None:
    #         context = {}
    #     if not len(ids):
    #         return []
    #     def _name_get(d):
    #         name = d.get('name','')
    #         code = d.get('default_code',False)
    #         if code:
    #             name = '[%s] %s' % (code,name)
    #         if d.get('variants'):
    #             name = name + ' - %s' % (d['variants'],)
    #         return (d['id'], name)
    #
    #     result = []
    #     for product in self.browse(cr, user, ids, context=context):
    #         mydict = {
    #                   'id': product.id,
    #                   'name': product.prodname,
    #                   'default_code': product.default_code,
    #                   'variants': product.variants
    #                   }
    #         result.append(_name_get(mydict))
    #     return result


class product_product(models.Model):
    _inherit = 'product.product'

    @api.multi
    def name_get(self):
        data = []
        for r in self:
            name = r.name
            code = r.default_code
            if code:
                name = '[%s] %s' % (code, name)
            data.append((r.id, name))
        return data


class stock_warehouse(models.Model):
    _inherit = 'stock.warehouse'

    branch_id = fields.Many2one(comodel_name='config.branch', string='Branch')
    #
    # def get_location_of_branch(self, cr, uid, branch_id, type='lot_stock_id'):
    #     location = []
    #     # print "***** type: %s" % type
    #     # print "***** branch_id: %s" % branch_id
    #     warehouse_id = self.search(cr, uid, [('branch_id', '=', branch_id)])
    #     if not warehouse_id:
    #         raise osv.except_osv("Error",
    #                              'ERROR 000193: Warehouse for branch (%s) is not defined in  Warehouse > Configuration > Warehouse Management > Warehouse.' % (
    #                              branch_id))
    #     warehouse_obj = self.read(cr, uid, warehouse_id[0], [type])
    #     # print "***** warehouse_obj: %s" % warehouse_obj
    #     if warehouse_obj and type in warehouse_obj:
    #         location = warehouse_obj[type]
    #     # print "***** location: ", location
    #     # print "***** len(location): ", len(location)
    #     # print "***** location[0]: ", location[0]
    #     return list(location)
