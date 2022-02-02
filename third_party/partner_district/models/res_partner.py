# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    city_id = fields.Many2one('res.city', 'City')

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

