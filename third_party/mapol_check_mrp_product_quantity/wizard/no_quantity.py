# -*- coding: utf-8 -*-

from odoo import fields, models, _


class NoQuantity(models.TransientModel):
    _name = 'no.quantity'
    _description = 'No Quantity'

    bom_check_id = fields.Many2one('bom.quantity.check')

    def availability_info(self):
        self.bom_check_id.write({'state': "deficient"})
        return
