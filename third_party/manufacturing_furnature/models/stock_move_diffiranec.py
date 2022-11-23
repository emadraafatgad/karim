from odoo import fields, models, api


class StockMoveNotConsumed(models.Model):
    _inherit = 'stock.move.line'
    customer_name = fields.Char(related='move_id.customer_name', store=True)


class StockMoveNotConsumed(models.Model):
    _inherit = 'stock.move'

    not_consumed = fields.Float(compute='cal_product_to_consumed', store=True)
    to_consume = fields.Float(store=True)
    customer_name = fields.Char(related='raw_material_production_id.origin', store=True)

    # customers_name = fields.Char(related='raw_material_production_id.origin')

    @api.model_create_multi
    def create(self, vals_list):
        tracking = []
        for vals in vals_list:
            print("vals")
            print(vals)
            print("id")
            print(vals.get('id'))
            vals['to_consume'] = vals.get('product_uom_qty')
        res = super(StockMoveNotConsumed, self).create(vals_list)
        return res

    @api.depends('product_uom_qty', 'quantity_done','state')
    def cal_product_to_consumed(self):
        for rec in self:
            print("rec")
            print(rec.id)
            print(rec.product_id.name)
            print(rec.state)
            print(rec.product_id.name,"====",rec.product_uom_qty,"========",rec.quantity_done)
            if rec.product_uom_qty and rec.quantity_done :
                print(rec.product_uom_qty, rec.quantity_done)
                rec.customer_name = rec.created_production_id.origin
                not_consumed = rec.to_consume - rec.quantity_done
                print(not_consumed, "not consumed")
                rec.not_consumed = not_consumed

    def cal_material_to_consume(self):
        for rec in self:
            print(rec.to_consume,"test to consume")
            if rec.product_uom_qty:
                rec.to_consume = rec.product_uom_qty
