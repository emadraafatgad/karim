# -*- coding: utf-8 -*-
from odoo import http

# class MrpQuotation(http.Controller):
#     @http.route('/mrp_quotation/mrp_quotation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mrp_quotation/mrp_quotation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mrp_quotation.listing', {
#             'root': '/mrp_quotation/mrp_quotation',
#             'objects': http.request.env['mrp_quotation.mrp_quotation'].search([]),
#         })

#     @http.route('/mrp_quotation/mrp_quotation/objects/<model("mrp_quotation.mrp_quotation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mrp_quotation.object', {
#             'object': obj
#         })