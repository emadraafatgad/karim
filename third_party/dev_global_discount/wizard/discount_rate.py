from odoo import models, fields,api,_


class DiscountRate(models.TransientModel):
    _name = 'discount.rate'
    _description = 'Calculate discount rate'

    total_amount = fields.Float(compute='calc_sales_orders_rate')
    total_discount = fields.Float(compute='calc_sales_orders_rate')
    rate = fields.Float(compute='calc_sales_orders_rate')
    sales_count = fields.Integer(compute='calc_sales_orders_rate',digits=(16, 3),)
    date_from = fields.Date()
    date_to = fields.Date()

    @api.depends('date_from','date_to')
    def calc_sales_orders_rate(self):
        for rec in self:
            domain = []
            if rec.date_from or rec.date_to:
                if rec.date_from:
                    domain.append(('confirmation_date','>=',self.date_from))
                if rec.date_to:
                    domain.append(('confirmation_date','<=',self.date_to))
                orders = self.env['sale.order'].search(domain)
                total_amount = 0
                total_discount = 0
                counter = 0
                for line in orders:
                    counter = counter+1
                    if line.apply_discount:
                        total_amount = total_amount + line.amount_untaxed
                        total_discount += line.discount_from_lines
                    else:
                        if line.discount_type == 'amount':
                            total_amount += line.amount_untaxed + line.discount_rate
                            total_discount += line.discount_rate
                        elif line.discount_type == 'percent':
                            amount = line.amount_untaxed/(1-line.discount_rate/100)
                            total_amount += amount
                            total_discount += amount - line.amount_untaxed
                rec.total_discount = total_discount
                rec.total_amount = total_amount
                rec.sales_count = counter
                rec.rate = 100*total_discount/total_amount
