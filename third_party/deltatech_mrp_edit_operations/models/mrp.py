# ©  2015-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"



    """
    @api.onchange('move_raw_ids')
    def onchange_move_raw_product_id(self):
        for raw in self.move_raw_ids:
            raw.location_dest_id = raw.product_id.property_stock_production
            if raw.state == 'draft':
                raw.state = 'confirmed'
            if not raw.unit_factor:
                raw.unit_factor = 1.0
    """
