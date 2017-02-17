# -*- coding: utf-8 -*-
from openerp import http

# class SurveyInherit(http.Controller):
#     @http.route('/survey_inherit/survey_inherit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/survey_inherit/survey_inherit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('survey_inherit.listing', {
#             'root': '/survey_inherit/survey_inherit',
#             'objects': http.request.env['survey_inherit.survey_inherit'].search([]),
#         })

#     @http.route('/survey_inherit/survey_inherit/objects/<model("survey_inherit.survey_inherit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('survey_inherit.object', {
#             'object': obj
#         })