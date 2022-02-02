from odoo import fields, models, api


class StockMoveNotConsumed(models.Model):
    _inherit = 'stock.move.line'
    customer_name = fields.Char(related='move_id.customer_name',store=True)

class StockMoveNotConsumed(models.Model):
    _inherit = 'stock.move'

    not_consumed = fields.Float(compute='cal_product_to_consumed', store=True)
    to_consume = fields.Float(compute='cal_product_to_consume', store=True)
    customer_name = fields.Char(related='raw_material_production_id.origin',store=True)
    # customers_name = fields.Char(related='raw_material_production_id.origin')

    @api.depends('product_uom_qty', 'quantity_done')
    def cal_product_to_consumed(self):
        for rec in self:
            print(rec)
            if rec.product_uom_qty and rec.quantity_done:
                print(rec.product_uom_qty, rec.quantity_done)
                rec.customer_name = rec.created_production_id.origin
                not_consumed = rec.product_uom_qty - rec.quantity_done
                print(not_consumed, "not consumed")
                rec.not_consumed = not_consumed

    @api.depends('product_uom_qty', 'quantity_done')
    def cal_product_to_consume(self):
        for rec in self:
            print(rec.to_consume,"test to consume")
            if rec.product_uom_qty:
                if rec.to_consume == 0:
                    rec.to_consume = rec.product_uom_qty
                    print(rec.to_consume,"rec.to_consume")
                elif rec.to_consume > 0:
                    print("rec.to_consume",rec.to_consume)
            print(rec.to_consume, "last to_consume")
