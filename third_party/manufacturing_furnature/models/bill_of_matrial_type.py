from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductListComponent(models.Model):
    _inherit = 'product.component.list'

    bom_id = fields.Many2one('mrp.bom')


class BillMaterialInherit(models.Model):
    _inherit = 'mrp.bom'

    is_standard = fields.Boolean(string="Standard")
    is_export = fields.Boolean(string="Export")
    product_component_list_ids = fields.One2many('product.component.list', "bom_id")

    # bom_cost = fields.Float(compute='_compute_total_cost', string="Total Material Cost", default=0.0)
    #
    # @api.depends('move_raw_ids.product_id')
    # def _compute_total_cost(self):
    #     material_total = 0.0
    #     for line in self.move_raw_ids:
    #         material_total += line.produc
    #     self.bom_total_material_cost = material_total

    @api.constrains("is_standard")
    def constrain_on_standard(self):
        bom_id = self.search([('product_tmpl_id', '=', self.product_tmpl_id.id), ('is_standard', '=', True)])
        if len(bom_id) > 1:
            raise ValidationError(_("This product already has a standard Bill Material"))

    @api.constrains("is_export")
    def constrain_on_standard(self):
        bom_id = self.search([('product_tmpl_id', '=', self.product_tmpl_id.id), ('is_export', '=', True)])
        if len(bom_id) > 1:
            raise ValidationError(_("This product already has a == Export == Bill Material"))

    @api.multi
    def copy_data(self, default=None):
        if default is None:
            default = {}
        if 'product_component_list_ids' not in default:
            default['product_component_list_ids'] = [(0, 0, line.copy_data()[0]) for line in
                                             self.product_component_list_ids]
        return super(BillMaterialInherit, self).copy_data(default)
