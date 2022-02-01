from odoo import fields, models, api


class MrpPackaging(models.Model):
    _name = 'mrp.packaging'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name',required=True, track_visibility="onchange")
    package_size = fields.Many2one('package.size', required=True)
    product_id = fields.Many2one('product.product', domain="[('sale_ok','=',True)]", track_visibility="onchange")
    cost = fields.Float()
    total_cost = fields.Float(compute='calculate_packaging_cost',track_visibility="onchange")
    packaging_line_ids = fields.One2many('mrp.packaging.line','mrp_packaging_id',track_visibility="onchange")
    # operation_id = fields.Many2one('mrp.routing.workcenter',required=True, string='Operation')
    operation_id = fields.Many2one('mrp.routing.workcenter', track_visibility='onchange',
                                   domain="[('operation_type','in',['others'])]",
                                   required=True)
    @api.depends('packaging_line_ids.cost')
    def calculate_packaging_cost(self):
        for rec in self:
            total = 0
            for line in rec.packaging_line_ids:
                total += line.cost
            rec.total_cost = total

    @api.multi
    def copy_data(self, default=None):
        if default is None:
            default = {}
        if 'packaging_line_ids' not in default:
            default['packaging_line_ids'] = [(0, 0, line.copy_data()[0]) for line in
                                     self.packaging_line_ids]
        return super(MrpPackaging, self).copy_data(default)


class MrpPackagingLine(models.Model):
    _name = 'mrp.packaging.line'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    product_id = fields.Many2one('product.product',track_visibility='onchange',required=True,domain="[('mrp_product_type','=','packaging')]")
    qty = fields.Float(track_visibility='onchange',required=True)
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure',track_visibility='onchange',compute='get_unit_of_measure',store=True)
    cost = fields.Float(compute='calculate_packaging_cost',required=True,track_visibility='onchange',sotre=True)
    unit_cost = fields.Float(track_visibility='onchange',required=True )
    currency_id = fields.Many2one('res.currency', track_visibility='onchange', string='Currency', readonly=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    mrp_packaging_id = fields.Many2one('mrp.packaging')

    @api.depends('product_id','qty','unit_cost')
    def calculate_packaging_cost(self):
        for rec in self:
                rec.cost = rec.unit_cost*rec.qty

    @api.depends('product_id')
    def get_unit_of_measure(self):
        for rec in self:
            rec.uom_id = rec.product_id.uom_id


class ProductionNames(models.Model):
    _name = 'package.size'

    name = fields.Char(string="Name",required=True)