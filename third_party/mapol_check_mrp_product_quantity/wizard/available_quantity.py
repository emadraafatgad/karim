# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import UserError


class AvailableQuantity(models.TransientModel):
    _name = 'available.quantity'
    _description = 'Available Quantity'

    bom_check_id = fields.Many2one('bom.quantity.check')

    def availability_info(self):
        self.bom_check_id.write({'state': "available"})
        return
