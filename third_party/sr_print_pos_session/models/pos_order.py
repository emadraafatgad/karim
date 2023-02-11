from odoo import fields, api, models

class ResCompany(models.Model):
    _inherit = "res.company"

    pos_sale_note = fields.Text(string='Default Terms and Conditions', translate=True)
class PostOrder(models.Model):
    _inherit = 'pos.order'
    def _default_note(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'sale.use_sale_note') and self.env.user.company_id.pos_sale_note or ''

    order_note = fields.Text('Terms and conditions', default=_default_note)
    city_id = fields.Many2one('res.city', 'City',)
    delivery_date = fields.Date(string="Delivery Date")
    is_delivered = fields.Boolean()

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_sale_note = fields.Text(related='company_id.pos_sale_note', string=" Pos Terms & Conditions", readonly=False)
    pos_use_sale_note = fields.Boolean(
        string='Default Terms & Conditions',
        oldname='default_use_sale_note',
        config_parameter='sale.use_sale_note')
