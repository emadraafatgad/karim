from odoo import fields, models, api, exceptions, _


class ManufacturingFinishedProduct(models.Model):
    _name = "mrp.package"

    name = fields.Char()
    parent = fields.Many2one('mrp.package')
    package_line_ids = fields.One2many('mrp.package.line','package_id')


class ManufacturingFinishedProductLine(models.Model):
    _name = 'mrp.package.line'

    product_id = fields.Many2one('product.product')
    quantity = fields.Float()
    uom = fields.Many2one('uom.uom')
    package_id = fields.Many2one('mrp.package')


class ProductPackaging(models.Model):
    _inherit = 'product.product'

    package_ids = fields.Many2many('mrp.package')
