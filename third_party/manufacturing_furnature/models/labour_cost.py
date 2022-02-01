from odoo import fields, models, api, exceptions, _


class ComponentName(models.Model):
    _name = "operation.name"

    name = fields.Char()


class DirectLabourCost(models.Model):
    _name = 'direct.labour.cost'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = 'product_id'

    operation_id = fields.Many2one('mrp.routing.workcenter',track_visibility='onchange', required=True)
    operation_type = fields.Selection([('paint', 'Painting'), ('upholstery', 'upholstery'),('carpainter','carpainter'),('others','Others')],track_visibility='onchange',
                                      related='operation_id.operation_type')
    labour_cost = fields.Float(track_visibility='onchange',required=True)
    worker_id = fields.Many2one('res.partner', track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee', track_visibility='onchange')

    product_id = fields.Many2one('product.product', track_visibility='onchange', domain="[('sale_ok','=',True)]",required=True, string="Finished Product")
    unit_cost = fields.Float(string="Cost", track_visibility='onchange')


class BillMaterialLabourCost(models.Model):
    _inherit = 'mrp.bom'

    direct_labour_cost_ids = fields.One2many('direct.labour.cost',"bom_id")

    total_cost = fields.Float(compute='calc_total_direct_labour_cost',store=True)

    @api.depends('direct_labour_cost_ids.labour_cost')
    def calc_total_direct_labour_cost(self):
        print("-==-=--=--=-=-=-=----=--=-1")
        for line in self:
            print("=======================2")
            line.total_cost = sum([p.total_cost for p in line.labour_cost])
            print(line.total_cost)
            # cost= 0.0
            # for rec in line.direct_labour_cost_ids:
            #     cost += rec.labour_cost
            #     print(cost)
            # line.total_cost = cost


class MoLabourCost(models.Model):
    _inherit = 'mrp.production'

    direct_labour_cost_ids = fields.One2many('direct.labour.cost',"mo_id")

    total_cost = fields.Char(compute='calc_total_direct_labour_cost',store=True)

    @api.depends('direct_labour_cost_ids')
    def calc_total_direct_labour_cost(self):
        for line in self:
            line.total_cost = sum([p.total_cost for p in line.labour_cost])
            print(line.total_cost)
            # cost= 0.0
            # for rec in line.direct_labour_cost_ids:
            #     cost += rec.unit_cost
            # line.total_cost = cost


class BomLabourCost(models.Model):
    _inherit = 'direct.labour.cost'

    bom_id = fields.Many2one('mrp.bom')


class MOLabourCost(models.Model):
    _inherit = 'direct.labour.cost'

    mo_id = fields.Many2one('mrp.production')