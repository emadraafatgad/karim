from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    large_percentage = fields.Monetary(string='70 % Percentage', store=True, readonly=True,
                                       compute='_compute_division_amount',
                                       track_visibility='onchange')
    low_percentage = fields.Monetary(string='30 % Percentage', store=True, readonly=True,
                                     compute='_compute_division_amount',
                                     track_visibility='onchange')
    done_large_percentage = fields.Monetary(string='70 % Percentage Done', store=True, readonly=True,
                                            compute='_compute_division_amount',
                                            track_visibility='onchange')
    done_low_percentage = fields.Monetary(string='30 % Percentage Done', store=True, readonly=True,
                                          compute='_compute_division_amount',
                                          track_visibility='onchange')

    remaining_large_percentage = fields.Monetary(string='70 % Percentage Remaining', store=True, readonly=True,
                                                 compute='_compute_division_amount',
                                                 track_visibility='onchange')
    remaining_low_percentage = fields.Monetary(string='30 % Percentage Remaining', store=True, readonly=True,
                                               compute='_compute_division_amount',
                                               track_visibility='onchange')
    residual = fields.Monetary(store=True, readonly=True,compute='_compute_residual_amount',
                                               track_visibility='onchange')

    remaining = fields.Float()

    @api.depends('order_line','order_line.qty_invoiced')
    def _compute_residual_amount(self):
        for rec in self:
            paid = 0
            order_invoice = 0
            for line in rec.order_line:
                print("before down payment")
                if line.qty_invoiced and not line.product_uom_qty:
                    print("---------in down payment")
                    paid += line.price_unit
                if line.qty_invoiced and line.product_uom_qty:
                    order_invoice += line.price_unit
            print(paid)
            print(order_invoice)
            rec.residual = rec.disc_amount - paid - order_invoice - rec.sale_discount

    @api.depends('remaining')
    def _compute_division_amount(self):
        for rec in self:
            rec.get_invoice_status()
            rec.large_percentage = rec.disc_amount * .70
            rec.low_percentage = rec.disc_amount * .30
            rec.remaining_large_percentage = rec.disc_amount * .7
            rec.remaining_low_percentage = rec.disc_amount * .3
            net_paid = rec.disc_amount - rec.remaining
            print(net_paid,rec.disc_amount,rec.remaining)
            print("net")
            if net_paid <= rec.large_percentage and rec.state != 'draft':
                rec.done_large_percentage = net_paid
                rec.remaining_large_percentage = rec.large_percentage - net_paid
                rec.remaining_low_percentage = rec.disc_amount * .3
            elif net_paid > rec.large_percentage:
                rec.done_large_percentage = rec.large_percentage
                rec.done_low_percentage = net_paid - rec.large_percentage
                rec.remaining_low_percentage = rec.low_percentage - rec.done_low_percentage
                rec.remaining_large_percentage = 0
            else:
                rec.done_large_percentage = 0
                rec.done_low_percentage = 0

    @api.multi
    def button_dummy(self):
        self.supply_rate()
        return True
