from odoo import api,models,fields, exceptions, _
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round

from itertools import groupby


# class BillOfMatirialType(models.Model):
#     _inherit = 'mrp.bom.line'
#
#     type = fields.Selection([("internal","internal"),('external','external')])
#
#     # component_id = fields.Selection([('1', 'internal Body'),
#     #                                  ('2', 'external Body'),
#     #                                  ('3', 'cord'),
#     #                                  ('4', 'Component 4'),
#     #                                  ('5', 'Component 5'),
#     #                                  ('6', 'Component 6'),
#     #                                  ('7', 'Component 7'),
#     #                                  ])
#     component_id = fields.Many2one('component.name')

class ProductListComponent(models.Model):
    _inherit = 'product.component.list'

    bom_id = fields.Many2one('mrp.bom')


class BillMateiralInherit(models.Model):
    _inherit = 'mrp.bom'

    is_standard = fields.Boolean(string="Standard")
    is_export = fields.Boolean(string="Export")
    product_component_list_ids = fields.One2many('product.component.list',"bom_id")

    @api.constrains("is_standard")
    def constrain_on_standard(self):
        bom_id = self.search([('product_tmpl_id', '=', self.product_tmpl_id.id), ('is_standard', '=', True)])
        if len(bom_id) > 1:
            raise exceptions.ValidationError(_("This product already has a standard Bill Material"))

    @api.constrains("is_export")
    def constrain_on_standard(self):
        bom_id =self.search([('product_tmpl_id','=',self.product_tmpl_id.id),('is_export','=',True)])
        if len(bom_id) > 1:
            raise exceptions.ValidationError(_("This product already has a == Export == Bill Material"))

