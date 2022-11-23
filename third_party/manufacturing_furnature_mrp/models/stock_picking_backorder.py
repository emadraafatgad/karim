from odoo import fields,api,models,_


class PurchaseOder(models.Model):
    _inherit = 'purchase.order'

    received_status = fields.Boolean()
    note = fields.Text()
    @api.multi
    def check_purchase_order_received(self):
        for rec in self:
            state = False
            for order_id in rec.order_line:
                if order_id.received_state :
                    state = True
            print(state,"======")
            rec.write({'received_status': state})
            print(rec.received_status,fields.Datetime.now())


    def update_note_with_discription(self):
        for rec in self:
            for line in rec.order_line:
                rec.note += line.name


class PurchaseOderLine(models.Model):
    _inherit = 'purchase.order.line'

    received_state = fields.Boolean(compute='update_parent_po',store=True)

    @api.depends('qty_received')
    def update_parent_po(self):
        for line in self:
            if line.qty_received:
                if line.product_qty > line.qty_received:
                    line.received_state = False
                else:
                    line.received_state = True
                    parent_order= self.env['purchase.order'].search([('id','=',line.order_id.id)])
                    print("parent ID ",parent_order)
                    parent_order.check_purchase_order_received()