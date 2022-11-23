from odoo import fields, api, models, _


class PurchaseOder(models.Model):
    _inherit = 'purchase.order'

    note = fields.Text()

    def update_note_with_description(self):
        for rec in self:
            for line in rec.order_line:
                if not rec.note:
                    rec.note = "---note---\n"
                rec.note += line.product_id.name + " ----> " + line.name+"\n"

    @api.multi
    def button_confirm(self):
        for order in self:
            res = super(PurchaseOder, self).button_confirm()
            if order.note:
                for picking in order.picking_ids:
                    picking.note = order.note
        return res
