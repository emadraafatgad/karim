from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoiced_amount = fields.Float()
    paid_amount = fields.Float()
    due_amount = fields.Float()
    total_downpayment = fields.Float()
    remaining = fields.Float()
    payment_status = fields.Selection([('not', 'Not Paid'), ('partial', 'Partially Paid'), ('paid', 'Paid'), ],
                                      track_visibility='onchange',
                                      default='not')
    campaign_id = fields.Many2one('utm.campaign', 'Campaign',
                                  help="This is a name that helps you keep track of your different campaign efforts, e.g. Fall_Drive, Christmas_Special")
    source_id = fields.Many2one('utm.source', 'Source',
                                help="This is the source of the link, e.g. Search Engine, another domain, or name of email list")
    medium_id = fields.Many2one('utm.medium', 'Medium',
                                help="This is the method of delivery, e.g. Postcard, Email, or Banner Ad",
                                oldname='channel_id')

    def get_invoice_status(self):
        self.compute_sale_order_amount()
        # invoiecs = self.env['account.invoice'].search([])
        # for invoice in invoiecs:
        #     invoice.compute_sale_order_amount()

    # @api.depends('residual')
    def compute_sale_order_amount(self):
        for rec in self:
            all_invoice_id = self.env['account.invoice'].search(
                ['&', ('origin', '=', rec.name), '|', ('state', '=', 'open'), ('state', '=', 'paid')])
            if not all_invoice_id:
                rec.due_amount = rec.disc_amount
                rec.total_downpayment = 0
                rec.invoiced_amount = 0
                rec.paid_amount = 0
                rec.remaining = rec.disc_amount
                rec.payment_status = 'not'
                break

            sum_residual = 0
            print(all_invoice_id)
            invoiced_amount = 0
            for inv in all_invoice_id:
                sum_residual += inv.residual
                invoiced_amount += inv.amount_total
            sale_order = rec
            print("sale order", sale_order)
            total_downpayment = 0
            order_state = 'paid'
            flag = False
            full_invoiced = True
            for line in rec.order_line:
                if not len(line.invoice_lines) > 0:
                    full_invoiced = False
                if line.product_uom_qty == 0 and line.price_unit:
                    paid = False
                    for inv_l in line.invoice_lines:
                        if inv_l.invoice_id.state != 'paid':
                            order_state = 'not'
                        else:
                            paid = True
                    if paid:
                        total_downpayment += line.price_unit
                if not line.invoice_lines and not flag:
                    order_state = 'not'
                    flag = True
                elif line.invoice_lines:
                    for inv_line in line.invoice_lines:
                        if inv_line.invoice_id.state != 'paid':
                            order_state = 'not'
                # if order_state != 'not':
                #     if line.product_uom_qty == 0 and line.price_unit:
                #         total_downpayment += line.price_unit
            if total_downpayment > 0 and order_state == 'not':
                order_state = 'partial'
                print(total_downpayment)
            if sale_order:
                print("invoiced_amount,total_downpayment,sum_residual")
                print(invoiced_amount, total_downpayment, sum_residual)
                sale_order.due_amount = rec.disc_amount
                sale_order.total_downpayment = total_downpayment
                sale_order.invoiced_amount = invoiced_amount - total_downpayment
                sale_order.paid_amount = rec.disc_amount - sum_residual if full_invoiced else total_downpayment
                sale_order.remaining = sum_residual if full_invoiced else sale_order.disc_amount - sale_order.paid_amount
                sale_order.payment_status = 'paid' if sale_order.remaining == 0 else "partial"
