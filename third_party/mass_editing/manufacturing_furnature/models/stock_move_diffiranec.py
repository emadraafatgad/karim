from odoo import fields , models, api


class StockMoveNotConsumed(models.Model):
    _inherit = 'stock.move'

    not_consumed = fields.Float(compute='cal_product_to_consumed')

    @api.depends('product_uom_qty','quantity_done')
    def cal_product_to_consumed(self):
        for rec in self:
            print(rec)
            if rec.product_uom_qty and rec.quantity_done:
                print(rec.product_uom_qty ,rec.quantity_done)
                not_consumed = rec.product_uom_qty - rec.quantity_done
                print(not_consumed,"not consumed")
                rec.not_consumed = not_consumed