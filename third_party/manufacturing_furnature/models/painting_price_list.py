from odoo import fields,models,api


class PaintingPriceList(models.Model):
    _name = 'paint.price.list'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(default=True)
    active = fields.Boolean(default=True)
    operation_id = fields.Many2one('mrp.routing.workcenter', track_visibility='onchange',
                                   domain="[('operation_type','in',['paint'])]",
                                   required=True)
    worker_id = fields.Many2one('res.partner', domain="[('supplier','=','True')]", track_visibility='onchange', required=True)
    product_id = fields.Many2one('product.product',string="Finished Product", track_visibility='onchange', domain="[('sale_ok','=',True)]",required=True)
    color_id = fields.Many2one('product.product', track_visibility='onchange', domain="[('purchase_ok','=',True),('mrp_product_type','=','paint')]",required=True)
    cost = fields.Float(track_visibility='onchange')
    currency_id = fields.Many2one(
        'res.currency', 'Currency',track_visibility='onchange',
        default=lambda self: self.env.user.company_id.currency_id.id,
        required=True)