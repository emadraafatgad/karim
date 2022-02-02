# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round


class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"
    _description = "Record Production"

    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'),default=1,readonly=1, required=True)