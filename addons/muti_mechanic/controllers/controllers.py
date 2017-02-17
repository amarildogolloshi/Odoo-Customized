# -*- coding: utf-8 -*-
from openerp import http

# class MutiMechanic(http.Controller):
#     @http.route('/muti_mechanic/muti_mechanic/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/muti_mechanic/muti_mechanic/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('muti_mechanic.listing', {
#             'root': '/muti_mechanic/muti_mechanic',
#             'objects': http.request.env['muti_mechanic.muti_mechanic'].search([]),
#         })

#     @http.route('/muti_mechanic/muti_mechanic/objects/<model("muti_mechanic.muti_mechanic"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('muti_mechanic.object', {
#             'object': obj
#         })