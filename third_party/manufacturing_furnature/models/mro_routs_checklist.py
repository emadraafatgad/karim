from odoo import fields, models


class MrpRoutsChecklist(models.Model):
    _name = 'mrp.routs.checklist'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    check_list_lines = fields.One2many('mrp.checklist.line', 'checklist_id')
    product_id = fields.Many2one('product.product', required=True)


class MrpCheckListLine(models.Model):
    _name = 'mrp.checklist.line'

    name = fields.Many2one('rout.name', required=True)
    checklist_id = fields.Many2one('mrp.routs.checklist')
    product_id = fields.Many2one('product.product', related='checklist_id.product_id', store=True)


class RoutName(models.Model):
    _name = 'rout.name'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True)
