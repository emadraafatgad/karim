from odoo import fields, models


class FreightPort(models.Model):
    _name = 'freight.container'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code')
    size = fields.Float('Size', required=True)
    size_uom_id = fields.Many2one('uom.uom', string="Size Uom")
    volume = fields.Float('Volume', required=True)
    volume_uom_id = fields.Many2one('uom.uom', string="Volume Uom")
    weight = fields.Float('Weight', required=True)
    weight_uom_id = fields.Many2one('uom.uom', string="Weight Uom")
    active = fields.Boolean(default=True)
    state = fields.Selection([('available','Available'),('reserve','Reserve')],default='available')


class FreightService(models.Model):
    _name = 'freight.service'

    name = fields.Char('Name',required=True)
    sale_price = fields.Float('Sale Price',required=True)
    line_ids = fields.One2many('freight.service.line','line_id')


class FreightServiceLine(models.Model):
    _name = 'freight.service.line'

    partner_id = fields.Many2one('res.partner',string='Vendor',required=True)
    sale = fields.Float('Sale Price')
    line_id = fields.Many2one('freight.service')