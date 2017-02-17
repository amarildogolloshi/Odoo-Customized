# -*- coding: utf-8 -*-
from openerp import http

# class MutiTreasuryData(http.Controller):
#     @http.route('/muti_treasury_data/muti_treasury_data/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/muti_treasury_data/muti_treasury_data/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('muti_treasury_data.listing', {
#             'root': '/muti_treasury_data/muti_treasury_data',
#             'objects': http.request.env['muti_treasury_data.muti_treasury_data'].search([]),
#         })

#     @http.route('/muti_treasury_data/muti_treasury_data/objects/<model("muti_treasury_data.muti_treasury_data"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('muti_treasury_data.object', {
#             'object': obj
#         })