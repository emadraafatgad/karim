import logging

from odoo import models, fields
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ApplyDefaultPlan(models.TransientModel):
    _name = 'get.purchase.invoice'

    response_data = fields.Char(default="Are you sure to sync po with invoices !!!")

    # update_products = fields.Boolean()

    def get_all_invoices_purchase(self):
        purchase_orders = self.env['purchase.order'].search([])
        for order in purchase_orders:
            order._out_computetotal()
            order._out_computedue()
            order._out_computepaid()
            # order.out_action_amount_paid()
