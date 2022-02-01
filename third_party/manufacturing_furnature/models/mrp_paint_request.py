from odoo import fields, models


class MrpPaintRequest(models.Model):
    _name = 'mrp.paint.request'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string="Finished Product", track_visibility='onchange',
                                 domain="[('sale_ok','=',True)]", required=1)
    color_id = fields.Many2one('product.product', track_visibility='onchange',
                               domain="[('purchase_ok','=',True),('mrp_product_type','=','paint')]", required=True)
    delivery_date = fields.Date(track_visibility='onchange', related='request_id.delivery_date')
    request_id = fields.Many2one('mrp.production.request', )
    state = fields.Selection([('draft', 'draft'), ('Confirmed', 'MRP Order'),
                              ('bom', 'Done')], track_visibility='onchange', related='request_id.state', store=True)
    status = fields.Selection([('draft', 'draft'),('progress','In progress'),
                               ('done', 'Done')], track_visibility='onchange', default='draft')

    def done_status(self):
        self.status = 'done'

    def inprogress_status(self):
        self.status = 'progress'

    operation_id = fields.Many2one('mrp.routing.workcenter', track_visibility='onchange',
                                   domain="[('operation_type','in',['paint'])]",
                                   required=True)
    customer = fields.Char(related='request_id.origin', track_visibility='onchange')

# class NewManufacturingRequest(models.Model):
#     _inherit = 'mrp.production.request'
#
#
