from odoo import fields,models,api

class ProdcutTemplate(models.Model):
    _inherit = 'product.template'

    usa_price = fields.Float(string="USA Price")