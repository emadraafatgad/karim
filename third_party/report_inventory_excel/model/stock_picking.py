from odoo import fields, api, models
from datetime import datetime
from odoo import tools
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class stock_picking(models.Model):
    _inherit = "stock.picking"

    no_dokumen = fields.Char(string="No Dokumen")
    jenis_dokumen = fields.Selection([('Non BC', 'Non BC'), ('BC 2.3', 'BC 2.3'), ('BC 2.5', 'BC 2.5'), ('BC 2.6.2', 'BC 2.6.2'), ('BC 2.6.1', 'BC 2.6.1'), (
        'BC 2.7', 'BC 2.7'), ('BC 3.0', 'BC 3.0'), ('BC 3.3', 'BC 3.3'), ('BC 4.0', 'BC 4.0'), ('BC 4.1', 'BC 4.1')], 'Jenis Dokumen')
    tanggal_dokumen = fields.Date(
        'Tanggal Dokumen', default=lambda *a: datetime.today().date())
    # ada di modul purchase_stock
    # purchase_id = fields.Many2one('purchase.order', "Purchase Order")
    # ada di modul sale_stock
    # sale_id = fields.Many2one('sale.order', "Sale Order")
    currency_id = fields.Many2one('res.currency', "Currency",
                                  compute="_compute_currency", readonly=False, store=True)

    @api.depends('purchase_id', 'sale_id')
    def _compute_currency(self):
        for row in self:
            if row.sale_id:
                row.currency_id = row.sale_id.pricelist_id.currency_id

            if row.purchase_id:
                row.currency_id = row.purchase_id.currency_id
