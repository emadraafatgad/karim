# -*- encoding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = "product.product"

    avarage_cost = fields.Float('Current Average Cost', compute="_get_avg_cost",
                                digits=dp.get_precision('Product Price'), help='Current Stock Average Cost')

    def get_compute_stock_value(self):
        for product in self:
            # all_pro = self.env['product.product'].search([('type','=','product')])
            # for all in all_pro:
            #     all._compute_stock_value()
            product._compute_stock_value()

    @api.multi
    def _get_avg_cost(self):
        for prod in self:
            prod._compute_stock_value()
            print(prod.stock_value)
            print(prod.qty_available)
            # if not prod.standard_price:
            #     prod.avarage_cost = prod.stock_value/prod.qty_available if prod.qty_available else 0.0
            # else:
            #     prod.avarage_cost = prod.standard_price / prod.qty_available if prod.qty_available else 0.0


class ProductTemplate(models.Model):
    _inherit = "product.template"

    avarage_cost = fields.Float('Current Average Cost', compute="_get_avg_cost",
                                digits=dp.get_precision('Product Price'))
    show_current_avarage_cost = fields.Boolean(compute='_compute_show_current_avarage_cost')

    def _compute_show_current_avarage_cost(self):
        module_id = self.env['ir.module.module'].sudo().search(
            [('name', '=', 'wh_enhancement_privileges'), ('state', '=', 'installed')], limit=1)
        show_field = True
        if module_id:
            show_field = self.env.user.has_group('wh_enhancement_privileges.group_allow_product_cost')
        for rec in self:
            rec.show_current_avarage_cost = show_field

    @api.multi
    def _get_avg_cost(self):
        products = self.env['product.product'].search([('product_tmpl_id', 'in', self.ids)])
        dic = {}
        for prod in products:
            if prod.product_tmpl_id.id not in dic:
                dic[prod.product_tmpl_id.id] = {'cost': 0.0, 'count': 0}
            dic[prod.product_tmpl_id.id]['cost'] += prod.stock_value
            dic[prod.product_tmpl_id.id]['count'] += prod.qty_available
        for record in self:
            average_cost = 0.0
            if record.id in dic:
                average_cost = dic[record.id]['cost'] / dic[record.id]['count'] if dic[record.id]['count'] else 0.0
            record.avarage_cost = average_cost
