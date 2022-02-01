from odoo import fields, api,models


class NewManufacturingRequest(models.Model):
    _name = 'mrp.production.request'
    _rec_name = 'bom_id'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    product_id = fields.Many2one('product.product')
    quantity_qty = fields.Float(string="Product Quantity")
    bom_id = fields.Many2one('mrp.bom')
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure')
    delivery_date = fields.Date()
    origin = fields.Char(string="Customer Name")
    state = fields.Selection([('draft','draft'),('Confirmed','MRP Order'),('bom','Bom Requested')], track_visibility='onchange', default='draft')
    sale_order_id = fields.Many2one('sale.order')
    bom_line_ids = fields.Many2many('mrp.bom.line',compute="get_bom_line_ids" ,domain="[('bom_id','=',bom_id)]")

    @api.depends('bom_id')
    def get_bom_line_ids(self):
        for rec in self:
            ids=[]
            for line in rec.bom_id.bom_line_ids:
                ids.append(line.id)
            print(ids,"ids")
            rec.bom_line_ids= ids


    def send_to_mrp(self):
        mo_production_id = self.env['mrp.production'].create({
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom_id.id,
            'origin': self.origin,
            'sale_order_id': self.sale_order_id.id,
            'product_qty': self.quantity_qty,
            'bom_id': self.bom_id.id,
            'date_planned_start': self.delivery_date,
            'delivery_date': self.delivery_date,
            'company_id': self.env.user.company_id.id,
        })
        self.state = 'Confirmed'

    @api.multi
    def create_purchase_request(self):
        self.ensure_one()
        if self.state == 'Confirmed':
            lines = []
            purchase_req = self.env['bom.purchase.request'].search([('state','in',['draft','to_approve'])])
            if purchase_req:
                for line in self.bom_id.bom_line_ids:
                    request_line = self.env['bom.purchase.request.line'].search([('product_id','=',line.product_id.id),
                                                                                  ('state','in',['draft','to_approve'])])
                    if request_line:
                        qty= request_line.product_qty
                        needed_qty = line.product_qty
                        totol = qty+needed_qty
                        request_line.product_qty = totol
            self.state = 'bom'