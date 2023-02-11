from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round
from odoo.addons import decimal_precision as dp

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    work_plan_ids = fields.One2many('work.order.plan','production_id')

    def workorders_plan_create(self):
        workorders = self.env['work.order.plan']
        # Initial qty producing
        for operation in self.routing_id.operation_ids:
            # create workorder
            workorder = workorders.create({
                # 'name': operation.name,
                'production_id': self.id,
                'workcenter_id': operation.workcenter_id.id,
                'operation_id': operation.id,
                'name': self.origin,
                'sale_order_id':self.sale_order_id.id,
                'state': len(workorders) == 0 and 'ready' or 'pending',
            })
            if workorders:
                workorders[-1].next_work_order_id = workorder.id
                # workorders[-1]._start_nextworkorder()
            workorders += workorder
        # return workorders

class WorkOrderPlan(models.Model):
    _name = 'work.order.plan'
    _description = 'Work Order Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Work Order',)

    workcenter_id = fields.Many2one(
        'mrp.workcenter', 'Work Center', required=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    production_id = fields.Many2one(
        'mrp.production', 'Manufacturing Order',
        index=True, ondelete='cascade', required=True, track_visibility='onchange',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    product_id = fields.Many2one(
        'product.product', 'Product',
        related='production_id.product_id', readonly=True,
        help='Technical: used in views only.', store=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Unit of Measure',
        related='production_id.product_uom_id', readonly=True,
        help='Technical: used in views only.')
    # is_first_wo = fields.Boolean(string="Is the first WO to produce",
    #                              compute='_compute_is_first_wo')

    # @api.multi
    # def _compute_is_first_wo(self):
    #     for wo in self:
    #         wo.is_first_wo = (wo.production_id.workorder_ids[0] == wo)

    state = fields.Selection([
        ('pending', 'Pending'),
        ('ready', 'Ready'),
        ('progress', 'In Progress'),
        ('done', 'Finished'),
        ('cancel', 'Cancelled')], string='Status',
        default='pending')
    # date_planned_start = fields.Datetime(
    #     'Scheduled Date Start',
    #     states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    # date_planned_finished = fields.Datetime(
    #     'Scheduled Date Finished',
    #     states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    date_start = fields.Datetime(
        'Effective Start Date',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    date_finished = fields.Datetime(
        'Effective End Date',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    #
    next_work_order_id = fields.Many2one('work.order.plan', "Next Work Order")
    production_date = fields.Datetime('Production Date', related='production_id.date_planned_start', store=True,
                                      readonly=False)

    worker_id = fields.Many2one('res.partner', track_visibility='onchange',
                                states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    color_id = fields.Many2one('product.product', track_visibility='onchange',
                               domain="[('purchase_ok','=',True),('mrp_product_type','=','paint')]",
                               states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    customer_id = fields.Many2one('res.partner',readonly=1)
    sale_order_id = fields.Many2one('sale.order',domain="[('partner_id','=',customer_id)]")
    worker_wage = fields.Float( track_visibility='onchange', store=True)
    operation_type = fields.Selection(
        [('paint', 'Painting'), ('upholstery', 'upholstery'), ('carpainter', 'carpainter'), ('others', 'Others')],
        track_visibility='onchange',
        related='operation_id.operation_type', store=True)
    operation_id = fields.Many2one(
        'mrp.routing.workcenter', 'Operation')

    @api.multi
    def button_pending(self):
        return self.write({'state': 'pending'})

    # @api.multi
    # def _start_nextworkorder(self):
    #     rounding = self.product_id.uom_id.rounding
    #     # if self.next_work_order_id.state == 'pending' and (
    #     #         (self.operation_id.batch == 'no' and
    #     #          float_compare(self.qty_production, self.qty_produced, precision_rounding=rounding) <= 0) or
    #     #         (self.operation_id.batch == 'yes' and
    #     #          float_compare(self.operation_id.batch_size, self.qty_produced, precision_rounding=rounding) <= 0)):
    #     #     self.next_work_order_id.state = 'ready'
    #
    @api.multi
    def button_start(self):
        self.ensure_one()
        # As button_start is automatically called in the new view
        if self.state in ('done', 'cancel'):
            return True
        # Need a loss in case of the real time exceeding the expected
        return self.write({'state': 'progress',
                           'date_start': datetime.now(),
                           })

    #
    @api.multi
    def button_finish(self):
        self.ensure_one()
        self.start_next_plan()
        return self.write({'state': 'done', 'date_finished': fields.Datetime.now()})

    def start_next_plan(self):
        print("iam in next plan")
        if self.next_work_order_id:
            self.next_work_order_id.state = "ready"
    #
    @api.multi
    def action_cancel(self):
        return self.write({'state': 'cancel'})

    #
    @api.multi
    def button_done(self):
        if any([x.state in ('done', 'cancel') for x in self]):
            raise UserError(_('A Manufacturing Order is already done or cancelled.'))
        return self.write({'state': 'done',
                           'date_finished': datetime.now()})

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
