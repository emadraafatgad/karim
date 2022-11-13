# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # price: total template price, context dependent (partner, pricelist, quantity)
    # price = fields.Float(
    #     'Price', compute='_compute_template_price', inverse='_set_template_price',
    #     digits=dp.get_precision('Product Price'), track_visibility='onchange')
    # # list_price: catalog price, user defined
    # list_price = fields.Float(
    #     'Sales Price', default=1.0,
    #     digits=dp.get_precision('Product Price'),
    #     help="Price at which the product is sold to customers.", track_visibility='onchange',)
    # # lst_price: catalog price for template, but including extra for variants
    # lst_price = fields.Float(
    #     'Public Price', related='list_price', readonly=False,
    #     digits=dp.get_precision('Product Price'), track_visibility='onchange',)
    # standard_price = fields.Float(
    #     'Cost', compute='_compute_standard_price',
    #     inverse='_set_standard_price', search='_search_standard_price',
    #     digits=dp.get_precision('Product Price'), groups="base.group_user",
    #     help="Cost used for stock valuation in standard price and as a first price to set in average/FIFO.", track_visibility='onchange',)

    @api.one
    def _get_sale_price_history(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        sale_history_obj = self.env['sr.sale.price.history'].sudo()
        sale_history_ids = []
        domain = [('product_id','in', self.product_variant_ids.ids)]
        sale_order_line_record_limit = int(ICPSudo.get_param('sale_order_line_record_limit'))
        sale_order_status = ICPSudo.get_param('sale_order_status')
        if not sale_order_line_record_limit:
            sale_order_line_record_limit = 30
        if not sale_order_status:
            sale_order_status = 'sale'
        if sale_order_status == 'sale':
            domain += [('state','=','sale')]
        elif sale_order_status == 'done':
            domain += [('state','=','done')]
        else:
            domain += [('state','=',('sale','done'))]

        sale_order_line_ids = self.env['sale.order.line'].sudo().search(domain,limit=sale_order_line_record_limit,order ='create_date desc')
        for line in sale_order_line_ids:
            sale_price_history_id = sale_history_obj.create({
                    'name':line.id,
                    'partner_id' : line.order_partner_id.id,
                    'user_id' : line.salesman_id.id,
                    'product_tmpl_id' : line.product_id.product_tmpl_id.id,
                    'variant_id' : line.product_id.id,
                    'sale_order_id' : line.order_id.id,
                    'sale_order_date' : line.order_id.date_order,
                    'product_uom_qty' : line.product_uom_qty,
                    'unit_price' : line.price_unit,
                    'currency_id' : line.currency_id.id,
                    'total_price' : line.price_subtotal
                })
            sale_history_ids.append(sale_price_history_id.id)
        self.sale_price_history_ids = sale_history_ids

    @api.one
    def _get_purchase_price_history(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        purchase_history_obj = self.env['sr.purchase.price.history'].sudo()
        purchase_history_ids = []
        domain = [('product_id','in', self.product_variant_ids.ids)]
        purchase_order_line_record_limit = int(ICPSudo.get_param('purchase_order_line_record_limit'))
        purchase_order_status = ICPSudo.get_param('purchase_order_status')
        if not purchase_order_line_record_limit:
            purchase_order_line_record_limit = 30
        if not purchase_order_status:
            purchase_order_status = 'purchase'
        if purchase_order_status == 'purchase':
            domain += [('state','=','purchase')]
        elif purchase_order_status == 'done':
            domain += [('state','=','done')]
        else:
            domain += [('state','=',('purchase','done'))]

        purchase_order_line_ids = self.env['purchase.order.line'].sudo().search(domain,limit=purchase_order_line_record_limit,order ='create_date desc')
        for line in purchase_order_line_ids:
            purchase_price_history_id = purchase_history_obj.create({
                    'name':line.id,
                    'partner_id' : line.partner_id.id,
                    'user_id' : line.order_id.user_id.id,
                    'product_tmpl_id' : line.product_id.product_tmpl_id.id,
                    'variant_id' : line.product_id.id,
                    'purchase_order_id' : line.order_id.id,
                    'purchase_order_date' : line.order_id.date_order,
                    'product_uom_qty' : line.product_qty,
                    'unit_price' : line.price_unit,
                    'currency_id' : line.currency_id.id,
                    'total_price' : line.price_total
                })
            purchase_history_ids.append(purchase_price_history_id.id)
        self.purchase_price_history_ids = purchase_history_ids



    sale_price_history_ids = fields.Many2many("sr.sale.price.history",string="Sale Price History",compute="_get_sale_price_history")
    purchase_price_history_ids = fields.Many2many("sr.purchase.price.history",string="Purchase Price History", compute="_get_purchase_price_history")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    
    @api.one
    def _get_sale_price_history(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        sale_history_obj = self.env['sr.sale.price.history'].sudo()
        sale_history_ids = []
        domain = [('product_id','in', self.ids)]
        sale_order_line_record_limit = int(ICPSudo.get_param('sale_order_line_record_limit'))
        sale_order_status = ICPSudo.get_param('sale_order_status')
        if not sale_order_line_record_limit:
            sale_order_line_record_limit = 30
        if not sale_order_status:
            sale_order_status = 'sale'
        if sale_order_status == 'sale':
            domain += [('state','=','sale')]
        elif sale_order_status == 'done':
            domain += [('state','=','done')]
        else:
            domain += [('state','=',('sale','done'))]

        sale_order_line_ids = self.env['sale.order.line'].sudo().search(domain,limit=sale_order_line_record_limit,order ='create_date desc')
        for line in sale_order_line_ids:
            sale_price_history_id = sale_history_obj.create({
                    'name':line.id,
                    'partner_id' : line.order_partner_id.id,
                    'user_id' : line.salesman_id.id,
                    'product_tmpl_id' : line.product_id.product_tmpl_id.id,
                    'variant_id' : line.product_id.id,
                    'sale_order_id' : line.order_id.id,
                    'sale_order_date' : line.order_id.date_order,
                    'product_uom_qty' : line.product_uom_qty,
                    'unit_price' : line.price_unit,
                    'currency_id' : line.currency_id.id,
                    'total_price' : line.price_subtotal
                })
            sale_history_ids.append(sale_price_history_id.id)
        self.sale_price_history_ids = sale_history_ids
        
    @api.one
    def _get_purchase_price_history(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        purchase_history_obj = self.env['sr.purchase.price.history'].sudo()
        purchase_history_ids = []
        domain = [('product_id','in', self.product_variant_ids.ids)]
        purchase_order_line_record_limit = int(ICPSudo.get_param('purchase_order_line_record_limit'))
        purchase_order_status = ICPSudo.get_param('purchase_order_status')
        if not purchase_order_line_record_limit:
            purchase_order_line_record_limit = 30
        if not purchase_order_status:
            purchase_order_status = 'purchase'
        if purchase_order_status == 'purchase':
            domain += [('state','=','purchase')]
        elif purchase_order_status == 'done':
            domain += [('state','=','done')]
        else:
            domain += [('state','=',('purchase','done'))]

        purchase_order_line_ids = self.env['purchase.order.line'].sudo().search(domain,limit=purchase_order_line_record_limit,order ='create_date desc')
        for line in purchase_order_line_ids:
            purchase_price_history_id = purchase_history_obj.create({
                    'name':line.id,
                    'partner_id' : line.partner_id.id,
                    'user_id' : line.order_id.user_id.id,
                    'product_tmpl_id' : line.product_id.product_tmpl_id.id,
                    'variant_id' : line.product_id.id,
                    'purchase_order_id' : line.order_id.id,
                    'purchase_order_date' : line.order_id.date_order,
                    'product_uom_qty' : line.product_qty,
                    'unit_price' : line.price_unit,
                    'currency_id' : line.currency_id.id,
                    'total_price' : line.price_total
                })
            purchase_history_ids.append(purchase_price_history_id.id)
        self.purchase_price_history_ids = purchase_history_ids



    sale_price_history_ids = fields.Many2many("sr.sale.price.history",string="Sale Price History",compute="_get_sale_price_history")
    purchase_price_history_ids = fields.Many2many("sr.purchase.price.history",string="Purchase Price History", compute="_get_purchase_price_history")

