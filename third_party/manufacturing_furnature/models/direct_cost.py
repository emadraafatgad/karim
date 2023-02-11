from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


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
            line.total_cost = line.unit_cost * line.quantity


class DirectCost(models.Model):
    _name = "direct.material.cost"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    product_id = fields.Many2one('product.product', track_visibility='onchange')
    quantity = fields.Integer()
    unit_cost = fields.Float(compute='cal_total_cost', track_visibility='onchange', )
    total_cost = fields.Float(track_visibility='onchange')
    bom_id = fields.Many2one('mrp.bom', track_visibility='onchange', )
    mo_id = fields.Many2one('mrp.production', track_visibility='onchange', )

    @api.depends("product_id", 'quantity')
    def cal_total_cost(self):
        for line in self:
            line.unit_cost = line.product_id.standard_price
            line.total_cost = line.unit_cost * line.quantity


class BillMaterialDirectMaterialCost(models.Model):
    _inherit = 'mrp.bom'

    direct_material_cost_ids = fields.One2many('direct.material.cost', "bom_id")

    package_local_ids = fields.One2many("package.local", 'bom_id')
    total_cost = fields.Char(compute='calc_total_material_cost', store=True)

    @api.depends('direct_material_cost_ids', )
    def calc_total_material_cost(self):
        for line in self:
            cost = 0.0
            in_cost = 0.0
            for line in line.direct_material_cost_ids:
                in_cost += line.total_cost
            line.total_cost = cost


class MoMaterialCost(models.Model):
    _inherit = 'mrp.production'

    direct_material_cost_ids = fields.One2many('direct.labour.cost', "mo_id")
    package_local_ids = fields.One2many("package.local", 'mo_id')
    total_cost = fields.Char(compute='calc_total_direct_labour_cost', store=True)
    delivery_date = fields.Date()

    def confirm_work_orders(self):
        work_orders = self.env['mrp.workorder'].search([('production_id', '=', self.id), ('state', '!=', 'done')])
        print(work_orders)
        for work_order in work_orders:
            work_order.qty_producing = 1
            if work_order.state in ['pending', 'ready']:
                work_order.button_start()
            if work_order.state == 'progress':
                work_order.record_production()
            if work_order.state == 'done':
                pass

    def lock_unlock_done_mrp_move_qty(self):
        for line in self.move_raw_ids:
            print(line.product_id, line.state, line.is_lock)
            if line.state == 'done':
                line.write({'is_lock': True})
                print(line.is_lock)
    def unlock_done_mrp_move_qty(self):
        for line in self.move_raw_ids:
            print(line.product_id, line.state, line.is_lock)
            if line.state == 'done':
                line.write({'is_lock': False})
                print(line.is_lock)
    def action_toggle_is_locked(self):
        self.ensure_one()
        print("looooooooooooooooooooooooooooooooook")
        if self.env.user.has_group('manufacturing_furnature.group_unlock_permission'):
            self.is_locked = not self.is_locked
        elif self.state != 'done':
            self.is_locked = not self.is_locked
        elif not self.env.user.has_group('manufacturing_furnature.group_unlock_permission'):
            print("has group not")
            raise ValidationError("You Are Not Allowed to Update Quantity")
        return True

    @api.depends('direct_material_cost_ids')
    def calc_total_direct_labour_cost(self):
        for line in self:
            cost = 0.0
            for rec in line.direct_material_cost_ids:
                cost += rec.unit_cost
            line.total_cost = cost


class BomDirectCost(models.Model):
    _inherit = 'direct.labour.cost'

    bom_id = fields.Many2one('mrp.bom')


class MoDirectCost(models.Model):
    _inherit = 'direct.labour.cost'

    mo_id = fields.Many2one('mrp.production')
