# -*- coding: utf-8 -*-
from openerp import http

# class Request(http.Controller):
#     @http.route('/request/request/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/request/request/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('request.listing', {
#             'root': '/request/request',
#             'objects': http.request.env['request.request'].search([]),
#         })

#     @http.route('/request/request/objects/<model("request.request"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('request.object', {
#             'object': obj
#         })