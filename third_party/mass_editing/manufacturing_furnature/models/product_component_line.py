from odoo import fields,api,models

class ProductListComponent(models.Model):
    _inherit = 'product.component.list'

    product_id = fields.Many2one('product.product')



class ProductComponentLine(models.Model):
    _inherit = 'product.product'

    product_component_list_ids = fields.One2many('product.component.list',"product_id")
