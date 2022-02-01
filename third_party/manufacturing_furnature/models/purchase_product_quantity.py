from odoo import fields,models, api


class PurchaseProductQuantutyAvailable(models.Model):
    _inherit = "purchase.order.line"

    product_quantity = fields.Integer(compute='get_available_quantity',string="Forecasted Quantity")

    @api.depends('product_id','product_qty')
    def get_available_quantity(self):
        for line in self:
            # print(line.product_id.name,line.product_id.qty_available)
            line.product_quantity = line.product_id.virtual_available
