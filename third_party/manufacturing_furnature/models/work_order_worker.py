import logging

from odoo import _
from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, pycompat
from odoo.addons import decimal_precision as dp

class WorkOrderWorker(models.Model):
    _inherit = 'mrp.workorder'

    @api.onchange('worker_id')
    def work_order_domain(self):
        if self.worker_id and self.product_id:
            pass

    @api.onchange('component_id')
    def _get_category_domain(self):
        for rec in self:
            return {'domain': {'internal_component': [('categ_id', '=', rec.component_id.category_id.id),
                                                      ('mrp_product_type', '=', 'fabric')]}}

    worker_id = fields.Many2one('res.partner', track_visibility='onchange',
                                states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    color_id = fields.Many2one('product.product', track_visibility='onchange',domain="[('purchase_ok','=',True),('mrp_product_type','=','paint')]",
                                states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    worker_wage = fields.Float(compute="get_employee_wage_from_bom", track_visibility='onchange', store=True)
    operation_type = fields.Selection([('paint', 'Painting'), ('upholstery', 'upholstery'),('carpainter','carpainter'), ('others', 'Others')],
                                      track_visibility='onchange',
                                      related='operation_id.operation_type', store=True)

    @api.depends('worker_id', 'color_id')
    def get_employee_wage_from_bom(self):
        for work_order in self:
            product = work_order.production_id.product_id
            bom_obj = self.env['mrp.bom'].search([('product_tmpl_id', '=', product.product_tmpl_id.id), ('is_standard', '=', True)], limit=1)
            print(bom_obj, "bom_onje")
            print([('worker_id', '=', work_order.worker_id.id),
                   ('product_id', '=', work_order.product_id.id),
                   ('color_id', '=', work_order.color_id.id),
                   ('operation_id', '=', work_order.operation_id.id)])
            print(work_order.operation_id.operation_type)
            print(work_order.operation_id)
            if work_order.operation_id.operation_type == 'paint':
                paint_obj = self.env['paint.price.list'].search([('worker_id', '=', work_order.worker_id.id),
                                                                 ('product_id', '=', work_order.product_id.id),
                                                                 ('color_id', '=', work_order.color_id.id),
                                                                 ('operation_id', '=', work_order.operation_id.id)])
                if paint_obj:
                    print(paint_obj, "PAintcost", paint_obj.cost)
                    work_order.worker_wage = paint_obj.cost
            elif work_order.operation_id.operation_type != 'paint':
                print("iam in upholsetry worder")
                upholstery_obj = self.env['direct.labour.cost'].search([
                    ('product_id', '=', work_order.product_id.id),
                    ('operation_id', '=', work_order.operation_id.id)])
                print('iam in upholsetry',upholstery_obj)
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
            print("Bom Id")

    @api.multi
    def record_production(self):
        self.record_update_product_cost()
        done_button = super(WorkOrderWorker, self).record_production()

        # if not self.worker_id and self.operation_type != 'others':
        #     raise ValidationError(
        #         _('You must Select An Employee For That Order'))
        # elif self.worker_id and self.operation_type != 'others':
        #     bill_id = self.env['account.invoice'].create({
        #         'type': 'in_invoice',
        #         # 'currency_id':self.user_id.company_id.currency_id.id,
        #         'partner_id': self.worker_id.id,
        #         'origin': self.name,
        #         'account_id': self.worker_id.property_account_receivable_id.id,
        #     })
        #     self.env['account.invoice.line'].create({
        #         'name': self.name,
        #         'account_id': self.product_id.property_account_expense_id.id,
        #         'quantity': 1,
        #         'price_unit': self.worker_wage,
        #         'invoice_id': bill_id.id
        #     })
        #     if bill_id:
        #         bill_id.action_invoice_open()
        self.production_id.post_inventory()
        self.production_id.change_price()
        return done_button

    def record_update_product_cost(self):
        for rec in self:
            print("rec.move_raw_ids")
            # print(rec.move_raw_ids)
            for move in rec.move_raw_ids:
                print(move.product_id.name,"==**===========**=")
                domain = [('product_id', '=', move.product_id.id), ('state', 'in', ('purchase', 'done'))]
                purchase_order_line_ids = self.env['purchase.order.line'].sudo().search(domain,  limit=1,
                                                                                        order='create_date desc')
                # print(purchase_order_line_ids)
                # print(purchase_order_line_ids.price_unit)
                product_or_template = move.product_id.product_tmpl_id
                print(product_or_template.name)
                print(move.product_id.standard_price , purchase_order_line_ids.price_unit)
                cost = purchase_order_line_ids.price_unit if purchase_order_line_ids.price_unit > 0 else 1

                diff = move.product_id.standard_price -  cost
                prec = self.env['decimal.precision'].precision_get('Product Price')
                if not float_is_zero(diff, precision_digits=prec):
                    # raise UserError(_("No difference between the standard price and the new price."))
                # if move.product_id.standard_price != purchase_order_line_ids.price_unit:
                    counterpart_account_id = product_or_template.property_account_expense_id or product_or_template.categ_id.property_account_expense_categ_id
                    move.product_id.do_change_standard_price(cost, counterpart_account_id.id)

    @api.multi
    def button_start(self):
        button_start = super(WorkOrderWorker, self).button_start()
        assigned = True
        for line in self.move_raw_ids:
            if line.state not in ['assigned','done','cancel']:
                assigned = False
        if not assigned:
            raise ValidationError(
                _('Material is not Available'))

        # if not self.worker_id and self.operation_type != 'others':
        #     raise ValidationError(
        #         _('You must Select An Employee For That Order'))

        return button_start
