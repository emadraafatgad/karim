# -*- coding: utf-8 -*-

from odoo import fields, models, _


class PartialQuantity(models.TransientModel):
    _name = 'partial.quantity'
    _description = 'Partial Quantity'

    bom_check_id = fields.Many2one('bom.quantity.check')

    def availability_info(self):
        self.bom_check_id.write({'state': "partially_available"})
        return
