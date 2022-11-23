# -*- coding: utf-8 -*-

import odoo.addons.decimal_precision as dp
from odoo import models, fields, api, _

class StockMove(models.Model):
    _inherit = 'stock.move'

    avarage_cost = fields.Float('Current Average Cost', compute="_get_avg_cost",store=True,
                                digits=dp.get_precision('Product Price'), help='Current Stock Average Cost')
    avarage_cost_qty = fields.Float('Current Average Cost', compute="_get_avg_cost", store=True,
                                digits=dp.get_precision('Product Price'), help='Current Stock Average Cost')

    @api.depends('product_id')
    def _get_avg_cost(self):
        for move in self:
            # print("okay")
            if move.product_id.standard_price:
                # print("oook")
                move.avarage_cost = move.product_id.standard_price
                move.avarage_cost_qty = move.product_id.standard_price*move.product_uom_qty


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    prod_std_cost = fields.Float(digits=dp.get_precision('Product Price'), string='Standard Cost', compute='calculate_planned_costs')
    cur_std_mat_cost = fields.Float(digits=dp.get_precision('Product Price'), string='Planned Material Cost', compute='calculate_planned_costs')
    mat_cost_unit = fields.Float(digits=dp.get_precision('Product Price'), string='Consumed Material Cost', compute='calculate_material_cost')
    lab_mac_cost = fields.Float(digits=dp.get_precision('Product Price'), string='Actual Labour Cost', compute='calculate_labour_cost')
    total_production_cost = fields.Float(digits=dp.get_precision('Product Price'), string='Actual Total Cost',  compute='calculate_total_cost')
    finished_product_price = fields.Float(digits=dp.get_precision('Product Price'),string="Actual Price",related='product_id.lst_price')
    profit_per = fields.Float(digits=dp.get_precision('Product Price'),string="Profit Percentage",compute='get_profit_percentage')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id.id)

    def calc_avaerage(self):
        for line in self.move_raw_ids:
            # print("ok")
            line._get_avg_cost()

    @api.multi
    def calculate_planned_costs(self):
        costmat = 0.0
        costlabmac = 0.0
        for production in self:
            product_id = production.product_id
            bom_id = production.bom_id
            result, result2 = bom_id.explode(product_id, 1)
            # print("result")
            # print(result,result2)
            for sbom, sbom_data in result2:
                # print("sbom")
                # print(sbom,sbom_data)
                costmat += sbom.product_id.standard_price * sbom_data['qty']
                # print(costmat)
            production.prod_std_cost = production.product_id.standard_price
            production.cur_std_mat_cost = costmat
        return True

    @api.multi
    def calculate_material_cost(self):
        matprice = 0.0
        matamount = 0.0
        planned_cost = False
        for production in self:
            for move in production.move_raw_ids:
                if not move.is_done:
                    planned_cost = True
            # if not planned_cost:
            for move in production.move_raw_ids:
                if move.state == 'done':
                    matamount += move.product_id.standard_price * move.product_uom_qty
            qty_produced = 0.0
            if production.qty_produced == 0.0:
                qty_produced = production.product_qty
            else:
                qty_produced = production.qty_produced
            matprice = matamount / qty_produced
        production.mat_cost_unit = matprice
        return True

    @api.multi
    def calculate_labour_cost(self):
        for production in self:
            labmacprice = 0.0
            labmacamount = 0.0
            if production.state == "cancel" or production.state == "confirmed" or production.state == "planned":
                planned_cost = True
            labor_costs = self.env['direct.labour.cost'].search([('product_id','=',production.product_id.id)])
            for labor in labor_costs:
                labmacprice += labor.labour_cost
            production.lab_mac_cost = labmacprice
            # print('==========-=========------=-=-==-=-=-=-=-=')
        return True

    @api.multi
    def calculate_total_cost(self):
        total_cost = 0.0
        # print('==========-=========------=-=-==-=-=-=-=-=')
        for production in self:
            # print('==========-=========------=-=-==-=-=-=-=-=')
            production.total_production_cost = production.mat_cost_unit + production.lab_mac_cost
            # print(total_cost)
        return True

    @api.multi
    def get_profit_percentage(self):
        for production in self:
            if production.total_production_cost:
                production.profit_per = 100*(production.finished_product_price / production.total_production_cost-1)