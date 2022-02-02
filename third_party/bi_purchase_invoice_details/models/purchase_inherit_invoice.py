# -*- coding : utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PurchaseOrderUpdate(models.Model):
    _inherit = 'purchase.order'

    invoiced_amount = fields.Float(String='Invoiced Amount', compute='_computetotal')
    amount_due = fields.Float(String='Amount Due', compute='_computedue')
    paid_amount = fields.Float(String='Paid Amount', compute='_computepaid')
    amount_paid_percent = fields.Float(compute='action_amount_paid')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id)

    out_invoiced_amount = fields.Float(String='Invoiced Amount', )
    out_amount_due = fields.Float(String='Amount Due', )
    out_paid_amount = fields.Float(String='Paid Amount', )
    out_amount_paid_percent = fields.Float()

    @api.multi
    def _out_computetotal(self):
        invoice_id = self.env['account.invoice'].search(
            ['&', ('origin', '=', self.name), '|', ('state', '=', 'open'), ('state', '=', 'paid')])
        total = 0
        for comp in invoice_id:
            total += comp.amount_total
        self.out_invoiced_amount = total

    @api.multi
    def _out_computedue(self):
        item_id = self.env['account.invoice'].search(
            ['&', ('origin', '=', self.name), '|', ('state', '=', 'open'), ('state', '=', 'paid')])
        aggregate = 0
        for comp in item_id:
            aggregate += comp.residual
        self.out_amount_due = aggregate

    @api.onchange('invoiced_amount', 'amount_due')
    def _out_computepaid(self):
        self.out_paid_amount = float(self.out_invoiced_amount) - float(self.out_amount_due)

    @api.multi
    def action_amount_paid(self):
        if self.out_invoiced_amount > 0:
            self.out_amount_paid_percent = round(100 * self.out_paid_amount / self.out_invoiced_amount, 3)


    @api.multi
    def _computetotal(self):
        invoice_id = self.env['account.invoice'].search(
            ['&', ('origin', '=', self.name), '|', ('state', '=', 'open'), ('state', '=', 'paid')])
        total = 0
        for comp in invoice_id:
            total += comp.amount_total
        self.invoiced_amount = total

    @api.multi
    def _computedue(self):
        item_id = self.env['account.invoice'].search(
            ['&', ('origin', '=', self.name), '|', ('state', '=', 'open'), ('state', '=', 'paid')])
        aggregate = 0
        for comp in item_id:
            aggregate += comp.residual
        self.amount_due = aggregate

    @api.onchange('invoiced_amount', 'amount_due')
    def _computepaid(self):
        self.paid_amount = float(self.invoiced_amount) - float(self.amount_due)

    @api.multi
    def action_amount_paid(self):
        if self.invoiced_amount > 0:
            self.amount_paid_percent = round(100 * self.paid_amount / self.invoiced_amount, 3)
