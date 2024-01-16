from odoo import fields, api, models


class ManufacturingOrder(models.Model):
    _inherit = 'mrp.production'

    sale_order_id = fields.Many2one('sale.order',)