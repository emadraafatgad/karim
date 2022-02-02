from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = 'stock.picking'

    driver_id = fields.Many2one('res.partner', domain="[('supplier','=','True')]")
    delivery_date = fields.Date()
    driver_phone = fields.Char()
    phone = fields.Char(related='partner_id.phone')
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
    ], string='Invoice Status', related='sale_id.invoice_status', store=True, readonly=True)
