from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoiced_amount = fields.Float()
    paid_amount = fields.Float()
    due_amount = fields.Float()
    payment_status = fields.Selection([('not', 'Not Paid'), ('partial', 'Partially Paid'), ('paid', 'Paid'), ],
                                      track_visibility='onchange',
                                      default='not')

    def get_invoice_status(self):
        invoiecs = self.env['account.invoice'].search([])
        for invoice in invoiecs:
            invoice.compute_sale_order_amount()
