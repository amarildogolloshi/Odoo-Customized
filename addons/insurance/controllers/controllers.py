# -*- coding: utf-8 -*-
from openerp import http

# class Insurance(http.Controller):
#     @http.route('/insurance/insurance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/insurance/insurance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('insurance.listing', {
#             'root': '/insurance/insurance',
#             'objects': http.request.env['insurance.insurance'].search([]),
#         })

#     @http.route('/insurance/insurance/objects/<model("insurance.insurance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('insurance.object', {
#             'object': obj
#         })