from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount Type',
                                     readonly=True, states={'draft': [('readonly', False)]}, default='percent')
    discount_rate = fields.Float('Discount Amount', digits=(16, 2), readonly=True)
    amount_discount = fields.Monetary(string='Discount', store=True, readonly=True,
                                      track_visibility='always')
    # large_percentage = fields.Monetary(string='70 % Percentage', store=True, readonly=True,
    #                                    compute='_compute_division_amount',
    #                                    track_visibility='onchange')
    # low_percentage = fields.Monetary(string='30 % Percentage', store=True, readonly=True,
    #                                  compute='_compute_division_amount',
    #                                  track_visibility='onchange')
    # done_large_percentage = fields.Monetary(string='70 % Percentage Done', store=True, readonly=True,
    #                                         compute='_compute_division_amount',
    #                                         track_visibility='onchange')
    # done_low_percentage = fields.Monetary(string='30 % Percentage Done', store=True, readonly=True,
    #                                       compute='_compute_division_amount',
    #                                       track_visibility='onchange')
    #
    # remaining_large_percentage = fields.Monetary(string='70 % Percentage Remaining', store=True, readonly=True,
    #                                              compute='_compute_division_amount',
    #                                              track_visibility='onchange')
    # remaining_low_percentage = fields.Monetary(string='30 % Percentage Remaining', store=True, readonly=True,
    #                                            compute='_compute_division_amount',
    #                                            track_visibility='onchange')
    # residual = fields.Monetary(store=True, readonly=True,compute='_compute_residual_amount',
    #                                            track_visibility='onchange')
    #
    # @api.depends('order_line','order_line.qty_invoiced')
    # def _compute_residual_amount(self):
    #     for rec in self:
    #         paid = 0
    #         for line in rec.order_line:
    #             print("before down payment")
    #             if line.qty_invoiced and not line.product_uom_qty:
    #                 print("---------in down payment")
    #                 paid += line.price_unit
    #         print(paid)
    #         rec.residual = rec.amount_untaxed - paid
    #
    # @api.depends('residual')
    # def _compute_division_amount(self):
    #     for rec in self:
    #         rec.large_percentage = rec.amount_untaxed * .70
    #         rec.low_percentage = rec.amount_untaxed * .30
    #         rec.remaining_large_percentage = rec.amount_untaxed * .7
    #         rec.remaining_low_percentage = rec.amount_untaxed * .3
    #         net_paid = rec.amount_untaxed - rec.residual
    #         print(net_paid)
    #         if net_paid <= rec.large_percentage and rec.state != 'draft':
    #             rec.done_large_percentage = net_paid
    #             rec.remaining_large_percentage = rec.large_percentage - net_paid
    #             rec.remaining_low_percentage = rec.amount_untaxed * .3
    #         elif net_paid > rec.large_percentage:
    #             rec.done_large_percentage = rec.large_percentage
    #             rec.done_low_percentage = net_paid - rec.large_percentage
    #             rec.remaining_low_percentage = rec.low_percentage - rec.done_low_percentage
    #             rec.remaining_large_percentage = 0
    #         else:
    #             rec.done_large_percentage = 0
    #             rec.done_low_percentage = 0

    # @api.onchange('discount_type', 'discount_rate', 'invoice_line_ids')
    # def supply_rate(self):
    #     for inv in self:
    #         if inv.discount_type == 'percent':
    #             for line in inv.invoice_line_ids:
    #                 line.discount = inv.discount_rate
    #         else:
    #             total = discount = 0.0
    #             for line in inv.invoice_line_ids:
    #                 total += (line.quantity * line.price_unit)
    #             if inv.discount_rate != 0:
    #                 discount = (inv.discount_rate / total) * 100
    #             else:
    #                 discount = inv.discount_rate
    #             for line in inv.invoice_line_ids:
    #                 line.discount = discount

    # @api.multi
    # def compute_invoice_totals(self, company_currency, invoice_move_lines):
    #     total = 0
    #     total_currency = 0
    #     for line in invoice_move_lines:
    #         if self.currency_id != company_currency:
    #             currency = self.currency_id.with_context(
    #                 date=self.date or self.date_invoice or fields.Date.context_today(self))
    #             line['currency_id'] = currency.id
    #             line['amount_currency'] = currency.round(line['price'])
    #             line['price'] = currency.compute(line['price'], company_currency)
    #         else:
    #             line['currency_id'] = False
    #             line['amount_currency'] = False
    #             line['price'] = line['price']
    #         if self.type in ('out_invoice', 'in_refund'):
    #             total += line['price']
    #             total_currency += line['amount_currency'] or line['price']
    #             line['price'] = - line['price']
    #         else:
    #             total -= line['price']
    #             total_currency -= line['amount_currency'] or line['price']
    #     return total, total_currency, invoice_move_lines

    @api.multi
    def button_dummy(self):
        self.supply_rate()
        return True
