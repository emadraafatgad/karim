from odoo import fields, models


class FreightConfiguration(models.Model):
    _name = 'freight.configuration'
    _rec_name = 'egypt_company'

    egypt_company = fields.Many2one('res.company')
    usa_company = fields.Many2one('res.company')
