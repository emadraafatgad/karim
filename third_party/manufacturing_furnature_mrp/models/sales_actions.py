from odoo import fields,models,api,_
from datetime import datetime
from odoo.exceptions import Warning


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_cancel(self):
        now = fields.Datetime.now()
        for line in self:
            print(now,line.confirmation_date)
            duration = now - line.confirmation_date
            print(duration.days,"days")
            if duration.days > 7:
                raise Warning(_("This Sales Order Can't be Canceled Exeed More Than 7 Days "))
        return super(SaleOrder, self).action_cancel()