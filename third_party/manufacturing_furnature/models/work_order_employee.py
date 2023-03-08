import pytz
import sys
import datetime
import logging
import binascii
from datetime import date, datetime, time

from struct import unpack
from odoo import api, fields, models
from odoo import _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class WorkOrderEmployee(models.Model):
    _inherit = 'mrp.workorder'

    worker_id = fields.Many2one('res.partner', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    worker_wage = fields.Float(compute="get_employee_wage_from_bom", store=True)

    @api.depends('worker_id')
    def get_employee_wage_from_bom(self):
        for work_order in self:
            product = work_order.production_id.product_id.id
            bom_obj = self.env['mrp.bom'].search([('product_id', '=', product), ('is_standard', '=', True)], limit=1)
            print(bom_obj, "bom_onje")
            if work_order.operation_id.operation_type == 'paint':
                paint_obj = self.env['paint.price.list'].search([('worker_id', '=', work_order.worker_id.id),
                                                                 ('product_id', '=', work_order.product_id.id),
                                                                 ('operation_id', '=', work_order.operation_id.id)])
                if paint_obj:
                    print(paint_obj, "PAintcost", paint_obj.cost)
                    work_order.worker_wage = paint_obj.cost
            elif work_order.operation_id.operation_type == 'upholstery':
                print("iam in upholsetry")
                upholstery_obj = self.env['direct.labour.cost'].search([
                    ('product_id', '=', work_order.product_id.id),
                    ('operation_id', '=', work_order.operation_id.id)])
                if upholstery_obj.labour_cost:
                    work_order.worker_wage = upholstery_obj.labour_cost
                    print("upholstery_obj", upholstery_obj.labour_cost)
            # bom_id = work_order.production_id.product_id
            # for labors in bom_obj.direct_labour_cost_ids:
            #     if labors.operation_id == work_order.operation_id:
            #         print(" i found it ")
            #         work_order.employee_wage = labors.labour_cost
            #     else:
            #         work_order.employee_wage = 0.0
            # print("Bom Id")

    @api.multi
    def record_production(self):
        if not self.worker_id:
            raise ValidationError(_('You must Select An Employee For That Order'))
        self.record_update_product_cost()
        done_button = super(WorkOrderEmployee, self).record_production()
        self.production_id.post_inventory()
        self.production_id.change_price()
        return done_button

    def record_update_product_cost(self):
        for rec in self:
            print("rec.move_raw_ids")
            print(rec.move_raw_ids)
            for move in rec.move_raw_ids:
                print(move)
                domain = [('product_id', '=', move.producut_id.id), ('state', '=', ('purchase', 'done'))]
                purchase_order_line_ids = self.env['purchase.order.line'].sudo().search(domain,  limit=1,
                                                                                        order='create_date desc')
                product_or_template = move.product_id.product_tmpl_id
                counterpart_account_id = product_or_template.property_account_expense_id or product_or_template.categ_id.property_account_expense_categ_id
                rec.product_id.do_change_standard_price(purchase_order_line_ids.price_unit, counterpart_account_id.id)

    @api.multi
    def change_price(self):
        """ Changes the Standard Price of Product and creates an account move accordingly. """
        self.ensure_one()
        product_or_template = self.product_id.product_tmpl_id
        counterpart_account_id = product_or_template.property_account_expense_id or product_or_template.categ_id.property_account_expense_categ_id
        self.product_id.do_change_standard_price(self.total_production_cost, counterpart_account_id.id)

