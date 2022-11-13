from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('residual')
    def compute_sale_order_amount(self):
        for rec in self:
            sale_order = self.env['sale.order'].search([('name', '=', rec.origin)], limit=1)
            sale_order.compute_sale_order_amount()