# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = "res.partner"

    city_id = fields.Many2one('res.city', 'City')

    @api.constrains('state_id','zip','city_id','country_id','street')
    def constrain_all_address(self):
        if self.company_id.id == 2:
            if not self.state_id or not self.zip or not self.city_id or not self.country_id or not self.street:
                raise ValidationError("Please Add  'street','State','Zip','City','Country'")

    @api.onchange('city_id')
    def _onchange_district(self):
        if self.city_id:
            self.state_id = self.city_id.district_id
            self.city = self.city_id.name
            if self.city_id.district_id:
                self.country_id = self.city_id.district_id.country_id
        else:
            self.city = False


class ResCity(models.Model):
    _name = "res.city"

    name = fields.Char('City')
    district_id = fields.Many2one('res.country.state', u'District')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

