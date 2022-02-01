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

class sale_order(models.Model):
    _inherit = 'sale.order'
    
    
    apply_discount = fields.Boolean('Apply Discount')
    discount_account_id = fields.Many2one('account.account','Discount Account', domain="[('is_discount','=',True)]")
    discount_type = fields.Selection([('amount','Amount'),('percent','Percent')],string='Discount Type')
    sale_discount = fields.Float('Sale Discount')
    
    
    @api.depends('order_line.price_total','sale_discount','discount_type','apply_discount')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=order.partner_shipping_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            disc_amt = 0.0
            if order.apply_discount:
                if order.discount_type == 'amount':
                    disc_amt = order.sale_discount
                else:
                    disc_amt = (amount_untaxed * order.sale_discount) / 100
            
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax - disc_amt,
                'disc_amount' : amount_untaxed - disc_amt,
            })
            
            
    
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    disc_amount = fields.Float('Amount After Discount',compute='_amount_all')


    @api.multi
    def action_confirm(self):
        for order in self:
            if order.apply_discount:
                if order.sale_discount <= 0.0:
                    raise ValidationError(_('Sale Discount Must be Greater then 0.'))
            res= super(sale_order,order).action_confirm()
        return res


    @api.multi
    def _prepare_invoice(self):
        res= super(sale_order,self)._prepare_invoice()
        if self.apply_discount and res:
            res.update({
                'apply_discount':self.apply_discount or False,
                'discount_account_id':self.discount_account_id and self.discount_account_id.id or False,
                'discount_type':self.discount_type,
                'sale_discount':self.sale_discount,
                'disc_amount':self.disc_amount,
            })
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
    
    
        
