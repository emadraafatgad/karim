from odoo import fields, models


class FreightPort(models.Model):
    _name = 'freight.port'

    name = fields.Char('Name',required=True)
    code = fields.Char('Code')
    country_id = fields.Many2one('res.country', required=True)
    state_id = fields.Many2one('res.country.state',required=True, domain="[('country_id','=','country_id')]")
    land = fields.Boolean()
    air = fields.Boolean()
    water = fields.Boolean(default=True)
    active = fields.Boolean(default=True)


class FreightPricing(models.Model):
    _name = 'freight.price'

    name = fields.Char(required=True)
    volume = fields.Float('Volume Price', required=True)
    weight = fields.Float('Weight Price', required=True)


class FreightRoutes(models.Model):
    _name= 'freight.routes'

    name = fields.Char('Name',required=True)
    active = fields.Boolean(default=True)
    land_sale = fields.Float('Sale Price for land',required=True)
    air_sale = fields.Float('Sale Price for Air',required=True)
    water_sale = fields.Float('Sale Price for Water',required=True)