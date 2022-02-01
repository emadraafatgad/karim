from odoo import fields,api,models


class ProductComponent(models.Model):
    _name = 'product.component.list'

    @api.onchange('component_id')
    def _get_category_domain(self):
        for rec in self:
            return {'domain':{'internal_component': [('categ_id','=',rec.component_id.category_id.id),('mrp_product_type','=','fabric')]}}

    component_id = fields.Many2one('component.name',string="Part Name",required=True)
    category_id = fields.Many2one('product.category',related='component_id.category_id',store=True)
    is_count = fields.Boolean(related='component_id.is_count',store=True)
    quantity = fields.Integer(string="Count", default=1)
    internal_quantity = fields.Float(help="Bill Of Material Quantity",compute='component_id_get',store=True,readonly=False, string="QTY")
    internal_component = fields.Many2one('product.product',domain="[('categ_id','=',category_id),('mrp_product_type','=','fabric')]",
                                         string="Material")
    operation_id = fields.Many2one('mrp.routing.workcenter', compute='component_id_get', store=True, readonly=False,
                                    string='Operation To Consume')# TDE FIXME: naming
    component_line_id = fields.Many2one('sale.order.component.line',)
    note = fields.Char()

    @api.depends('component_id')
    def component_id_get(self):
        for rec in self:
            # print("=========componetn_id=========")
            if not rec.internal_quantity:
                rec.internal_quantity = rec.component_id.default_qty
                # print(rec.component_id.default_qty)
            if  rec.component_id.operation_id:
                rec.operation_id = rec.component_id.operation_id
                # print(rec.component_id.)


class ProductListComponent(models.Model):
    _inherit = 'product.component.list'

    product_id = fields.Many2one('product.product')


class ProductKomah(models.Model):
    _inherit = 'product.product'

    is_komash = fields.Boolean()
    mrp_product_type = fields.Selection([('paint','Paint'),('packaging','Packaging'),('fabric','fabric')],
                                        default='fabric')
    package_size = fields.Many2one('package.size')