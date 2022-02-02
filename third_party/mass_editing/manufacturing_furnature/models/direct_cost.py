from odoo import models, fields, api, _


class PackageForFinalProduct(models.Model):
    _name = "package.local"

    product_id = fields.Many2one('product.product')
    quantity = fields.Integer()
    unit_cost = fields.Float(compute='cal_total_cost')
    total_cost = fields.Float()
    bom_id = fields.Many2one('mrp.bom')
    mo_id = fields.Many2one('mrp.production')

    @api.depends("product_id", 'quantity')
    def cal_total_cost(self):
        for line in self:
            line.unit_cost = line.product_id.standard_price
            line.total_cost = line.unit_cost*line.quantity

class DirectCost(models.Model):
    _name = "direct.material.cost"

    product_id = fields.Many2one('product.product')
    quantity = fields.Integer()
    unit_cost = fields.Float(compute='cal_total_cost')
    total_cost = fields.Float()
    bom_id = fields.Many2one('mrp.bom')
    mo_id = fields.Many2one('mrp.production')

    @api.depends("product_id", 'quantity')
    def cal_total_cost(self):
        for line in self:
            line.unit_cost = line.product_id.standard_price
            line.total_cost = line.unit_cost*line.quantity


class BillMaterialDirectMaterialCost(models.Model):
    _inherit = 'mrp.bom'

    direct_material_cost_ids = fields.One2many('direct.material.cost',"bom_id")

    package_local_ids = fields.One2many("package.local", 'bom_id')
    total_cost = fields.Char(compute='calc_total_material_cost',store=True)

    @api.depends('direct_material_cost_ids',)
    def calc_total_material_cost(self):
        for line in self:
            cost= 0.0
            in_cost = 0.0
            for line in line.direct_material_cost_ids:
                in_cost += line.total_cost
            line.total_cost = cost


class MoMaterialCost(models.Model):
    _inherit = 'mrp.production'

    direct_material_cost_ids = fields.One2many('direct.labour.cost',"mo_id")
    package_local_ids = fields.One2many("package.local", 'mo_id')
    total_cost = fields.Char(compute='calc_total_direct_labour_cost',store=True)
    delivery_date = fields.Date()

    @api.depends('direct_material_cost_ids')
    def calc_total_direct_labour_cost(self):
        for line in self:
            cost= 0.0
            for rec in line.direct_material_cost_ids:
                cost += rec.unit_cost
            line.total_cost = cost


class BomDirectCost(models.Model):
    _inherit = 'direct.labour.cost'

    bom_id = fields.Many2one('mrp.bom')


class MODrirectCost(models.Model):
    _inherit = 'direct.labour.cost'

    mo_id = fields.Many2one('mrp.production')

