# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################
#
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    apply_discount = fields.Boolean('Apply Discount')
    discount_account_id = fields.Many2one('account.account','Discount Account', domain="[('is_discount','=',True)]")
    discount_type = fields.Selection([('amount','Amount'),('percent','Percent')],string='Discount Type')
    purchase_discount = fields.Float('Purchase Discount')
    
    
    @api.depends('order_line.price_total','apply_discount','purchase_discount','discount_type')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            disc_amount = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            if order.apply_discount:
                if order.discount_type == 'amount':
                    disc_amount = order.purchase_discount
                else:
                    disc_amount = (order.purchase_discount * amount_untaxed) / 100
                    
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax - disc_amount,
                'disc_amount': amount_untaxed  - disc_amount
            })
    
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')
    disc_amount = fields.Float('Amount After Discount',compute='_amount_all')

    @api.multi
    def button_confirm(self):
        for order in self:
            if order.apply_discount:
                if order.purchase_discount <= 0.0:
                    raise ValidationError(_('Purchase Discount Must be Greater then 0.'))
        return super(purchase_order,self).button_confirm()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


    
    
        
