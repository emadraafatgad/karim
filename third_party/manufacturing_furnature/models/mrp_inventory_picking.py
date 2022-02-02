from odoo import fields, api ,models


class InventoryPickingComponent(models.Model):
    _inherit = 'mrp.request'

    order = fields.Integer()