# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'
    
    calc_product_qty = fields.Float(
        'Total Quantity', compute='compute_total_bom_qty',
        digits=dp.get_precision('Product Unit of Measure'))
    check_bom_id = fields.Many2one('bom.quantity.check',"BOM quantity check")
    
    
    @api.one
    @api.depends('product_id', 'bom_id')
    def compute_total_bom_qty(self):
        if not self.product_id:
            self.calc_product_qty = 0
        else:
            self.calc_product_qty = self.bom_id.total_product_qty * self.product_qty
 


class MrpBom(models.Model):
    _inherit = 'mrp.bom'
    
    total_product_qty = fields.Float(
        'Total Quantity',
        digits=dp.get_precision('Unit of Measure'))
    
               
            
            