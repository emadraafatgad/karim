# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_unreserved_material(self):
        if self.state not in ('done', 'cancel') and self.reserved_availability:
            self._do_unreserve()
