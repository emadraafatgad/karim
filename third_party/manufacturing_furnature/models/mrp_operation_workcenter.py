from odoo import fields,models,api


class OperationWorkCenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    operation_type = fields.Selection([('paint', 'Painting'), ('upholstery', 'upholstery'),('carpainter','carpainter'),('others','Others')], default='others')