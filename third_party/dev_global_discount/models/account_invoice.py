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
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def create(self, vals):
        inv_id = super(account_invoice, self).create(vals)
        purchase_pool = self.env['purchase.order']
        if self._context.get('default_purchase_id'):
            purchase_id = purchase_pool.browse(self._context.get('default_purchase_id'))
            if purchase_id.apply_discount and inv_id:
                inv_id.write({
                    'apply_discount': True,
                    'discount_account_id': purchase_id.discount_account_id and purchase_id.discount_account_id.id or False,
                    'discount_type': purchase_id.discount_type,
                    'sale_discount': purchase_id.purchase_discount,
                    'disc_amount': purchase_id.disc_amount,
                })

        return inv_id

    apply_discount = fields.Boolean('Discount Applied')
    discount_account_id = fields.Many2one('account.account', 'Discount Account', domain="[('is_discount','=',True)]")
    discount_type = fields.Selection([('amount', 'Amount'), ('percent', 'Percent')], string='Discount Type')
    sale_discount = fields.Float('Discount in SO')

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice',
                 'type', 'discount_type', 'sale_discount')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(line.amount for line in self.tax_line_ids)
        print(self.amount_untaxed,self.amount_tax)
        dis_amt = 0.0
        if self.apply_discount and self.sale_discount:
            if self.discount_type == 'amount':
                dis_amt = self.sale_discount
            else:
                dis_amt = (self.sale_discount * self.amount_untaxed) / 100

        self.amount_total = self.amount_untaxed + self.amount_tax - dis_amt
        self.disc_amount = self.amount_untaxed - dis_amt

        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    amount_untaxed = fields.Monetary(string='Untaxed Amount',
                                     store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    amount_untaxed_signed = fields.Monetary(string='Untaxed Amount in Company Currency',
                                            currency_field='company_currency_id',
                                            store=True, readonly=True, compute='_compute_amount')
    amount_tax = fields.Monetary(string='Tax',
                                 store=True, readonly=True, compute='_compute_amount')
    amount_total = fields.Monetary(string='Total',
                                   store=True, readonly=True, compute='_compute_amount')
    amount_total_signed = fields.Monetary(string='Total in Invoice Currency', currency_field='currency_id',
                                          store=True, readonly=True, compute='_compute_amount',
                                          help="Total amount in the currency of the invoice, negative for credit notes.")
    amount_total_company_signed = fields.Monetary(string='Total in Company Currency',
                                                  currency_field='company_currency_id',
                                                  store=True, readonly=True, compute='_compute_amount',
                                                  help="Total amount in the currency of the company, negative for credit notes.")

    disc_amount = fields.Float('Amount After Discount', compute='_compute_amount')

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        # Still buggy in the case of taxes applied
        """ finalize_invoice_move_lines(move_lines) -> move_lines

		    Hook method to be overridden in additional modules to verify and
		    possibly alter the move lines to be created by an invoice, for
		    special cases.
		    :param move_lines: list of dictionaries with the account.move.lines (as for create())
		    :return: the (possibly updated) final move_lines to create for this invoice
		"""
        precision_obj = self.env['decimal.precision']
        precision = precision_obj.precision_get('Account')
        total_amount = 0.0
        for inv in self:
            if inv.apply_discount:
                if not inv.discount_account_id and inv.sale_discount > 0.0:
                    raise ValidationError(_(
                        'No account is configured as Discount Account, Please configure one before applying Discount!'))

                discount_amount = inv.amount_untaxed - inv.disc_amount

                new_line = {'analytic_account_id': False, 'tax_code_id': False, 'analytic_lines': [],
                            'tax_amount': False, 'name': inv.discount_account_id.name, 'ref': '',
                            'analytics_id': False, 'currency_id': False, 'debit': False,
                            'product_id': False, 'date_maturity': False, 'credit': False,
                            'amount_currency': 0, 'product_uom_id': False, 'quantity': 1,
                            'partner_id': move_lines[0][2]['partner_id'],
                            'account_id': inv.discount_account_id.id, }

                # if there is a discount should be removed from the total amount
                if inv.disc_amount > 0.0:
                    for line in move_lines:
                        if inv.type in ('out_invoice', 'in_refund'):
                            if line[2]['debit'] > 0.0:
                                line[2]['debit'] -= inv.amount_untaxed - inv.disc_amount
                        elif inv.type in ('in_invoice', 'out_refund'):
                            if line[2]['credit'] > 0.0:
                                line[2]['credit'] -= inv.amount_untaxed - inv.disc_amount

                debit = credit = 0.0
                for line in move_lines:
                    line[2]['debit'] = round(line[2]['debit'], precision)
                    line[2]['credit'] = round(line[2]['credit'], precision)
                    debit += line[2]['debit']
                    credit += line[2]['credit']

                precision_diff = round(credit - debit, precision)

                if precision_diff != 0.0:
                    if precision_diff < 0.0:
                        new_line['credit'] = abs(precision_diff)
                    else:
                        new_line['debit'] = precision_diff
                    move_lines.append((0, 0, new_line))
            return move_lines


class AccountInvoiceRefund(models.TransientModel):
    """Refunds invoice"""

    _inherit = "account.invoice.refund"

    @api.multi
    def compute_refund(self, mode='refund'):
        inv_obj = self.env['account.invoice']
        inv_tax_obj = self.env['account.invoice.tax']
        inv_line_obj = self.env['account.invoice.line']
        context = dict(self._context or {})
        xml_id = False

        for form in self:
            created_inv = []
            date = False
            description = False
            for inv in inv_obj.browse(context.get('active_ids')):
                if inv.state in ['draft', 'proforma2', 'cancel']:
                    raise UserError(_('Cannot refund draft/proforma/cancelled invoice.'))
                if inv.reconciled and mode in ('cancel', 'modify'):
                    raise UserError(_(
                        'Cannot refund invoice which is already reconciled, invoice should be unreconciled first. You can only refund this invoice.'))

                date = form.date or False
                description = form.description or inv.name
                refund = inv.refund(form.date_invoice, date, description, inv.journal_id.id)
                if refund:
                    refund.write({
                        'disc_amount': inv.disc_amount,
                        'apply_discount': inv.apply_discount,
                        'discount_account_id': inv.discount_account_id.id,
                        'discount_type': inv.discount_type,
                        'sale_discount': inv.sale_discount,
                    })

                created_inv.append(refund.id)
                if mode in ('cancel', 'modify'):
                    movelines = inv.move_id.line_ids
                    to_reconcile_ids = {}
                    to_reconcile_lines = self.env['account.move.line']
                    for line in movelines:
                        if line.account_id.id == inv.account_id.id:
                            to_reconcile_lines += line
                            to_reconcile_ids.setdefault(line.account_id.id, []).append(line.id)
                        if line.reconciled:
                            line.remove_move_reconcile()
                    refund.action_invoice_open()
                    for tmpline in refund.move_id.line_ids:
                        if tmpline.account_id.id == inv.account_id.id:
                            to_reconcile_lines += tmpline
                            to_reconcile_lines.filtered(lambda l: l.reconciled == False).reconcile()
                    if mode == 'modify':
                        invoice = inv.read(
                            ['name', 'type', 'number', 'reference',
                             'comment', 'date_due', 'partner_id',
                             'partner_insite', 'partner_contact',
                             'partner_ref', 'payment_term_id', 'account_id',
                             'currency_id', 'invoice_line_ids', 'tax_line_ids',
                             'journal_id', 'date'])
                        invoice = invoice[0]
                        del invoice['id']
                        invoice_lines = inv_line_obj.browse(invoice['invoice_line_ids'])
                        invoice_lines = inv_obj.with_context(mode='modify')._refund_cleanup_lines(invoice_lines)
                        tax_lines = inv_tax_obj.browse(invoice['tax_line_ids'])
                        tax_lines = inv_obj._refund_cleanup_lines(tax_lines)
                        invoice.update({
                            'type': inv.type,
                            'date_invoice': form.date_invoice,
                            'state': 'draft',
                            'number': False,
                            'invoice_line_ids': invoice_lines,
                            'tax_line_ids': tax_lines,
                            'date': date,
                            'origin': inv.origin,
                            'fiscal_position_id': inv.fiscal_position_id.id,
                            'disc_amount': inv.disc_amount,
                            'apply_discount': inv.apply_discount,
                            'discount_account_id': inv.discount_account_id.id,
                            'discount_type': inv.discount_type,
                            'sale_discount': inv.sale_discount,
                        })

                        for field in ('partner_id', 'account_id', 'currency_id',
                                      'payment_term_id', 'journal_id'):
                            invoice[field] = invoice[field] and invoice[field][0]
                        inv_refund = inv_obj.create(invoice)
                        if inv_refund.payment_term_id.id:
                            inv_refund._onchange_payment_term_date_invoice()
                        created_inv.append(inv_refund.id)
                xml_id = (inv.type in ['out_refund', 'out_invoice']) and 'action_invoice_tree1' or \
                         (inv.type in ['in_refund', 'in_invoice']) and 'action_invoice_tree2'
                # Put the reason in the chatter
                subject = _("Invoice refund")
                body = description
                refund.message_post(body=body, subject=subject)
        if xml_id:
            result = self.env.ref('account.%s' % (xml_id)).read()[0]
            invoice_domain = safe_eval(result['domain'])
            invoice_domain.append(('id', 'in', created_inv))
            result['domain'] = invoice_domain
            return result
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
