# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import api, fields, models


class SaleSalespersonReport(models.TransientModel):
    _name = 'sale.salesperson.report'

    start_date = fields.Datetime('Start Date', required=True)
    end_date = fields.Datetime(string="End Date", required=True)
    user_ids = fields.Many2many('res.users', string="Salesperson")

    @api.multi
    def print_salesperson_vise_report(self):
        sale_orders = self.env['sale.order'].search([])
        groupby_dict = {}
        for user in self.user_ids:
            filtered_order = list(filter(lambda x: x.user_id == user, sale_orders))
            print ("============filtered_order=====",type(self.start_date),)
            filtered_by_date = list(
                filter(lambda x: x.date_order >= self.start_date and x.date_order <= self.end_date, filtered_order))
            groupby_dict[user.name] = filtered_by_date
        print ("===========groupby_dict",groupby_dict)
        final_dict = {}
        for user in groupby_dict.keys():
            temp = []
            for order in groupby_dict[user]:
                temp_2 = []
                temp_2.append(order.name)
                temp_2.append(order.date_order)
                temp_2.append(order.amount_total)
                temp.append(temp_2)
            final_dict[user] = temp
        datas = {
            'ids': self,
            'model': 'sale.salesperson.report',
            'form': final_dict,
            'start_date': self.start_date,
            'end_date': self.end_date,

        }
        return self.env.ref('sr_sales_report_saleperson_groupby.action_report_sales_saleperson_wise').report_action([],
                                                                                                                    data=datas)
