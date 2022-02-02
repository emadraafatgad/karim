from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('residual')
    def compute_sale_order_amount(self):
        for rec in self:
            item_id = self.env['account.invoice'].search(
                ['&', ('origin', '=', rec.origin), '|', ('state', '=', 'open'), ('state', '=', 'paid')])
            aggregate = 0
            invoiced_amount = 0
            for comp in item_id:
                aggregate += comp.residual
                invoiced_amount += comp.amount_total
                sale_order = self.env['sale.order'].search([('name', '=', comp.origin)], limit=1)
                print("sale order", sale_order)
                if sale_order:
                    sale_order.due_amount = aggregate
                    sale_order.invoiced_amount = invoiced_amount
                    sale_order.paid_amount = invoiced_amount - aggregate
                    if comp.state == 'paid':
                        sale_order.payment_status = 'paid'
                    elif aggregate == 0:
                        sale_order.payment_status = 'not'
                    elif aggregate < invoiced_amount:
                        sale_order.payment_status = 'partial'
