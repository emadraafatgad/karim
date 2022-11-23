from odoo import fields, models, api
from odoo.exceptions import ValidationError

class PrintAllMaterials(models.TransientModel):
    _name = 'order.all.materials'

    sale_order_id = fields.Many2one('sale.order')
    sale_order_ids = fields.Many2many('sale.order')

    @api.multi
    def print_sale_order_material(self):
        if self.sale_order_id:
            mrp_request_objs = self.env['mrp.production.request'].search([('sale_order_id', '=', self.sale_order_id.id)])
        elif self.sale_order_ids:
            mrp_request_objs = self.env['mrp.production.request'].search([('sale_order_id', 'in', self.sale_order_ids.ids)])
        else:
            raise ValidationError("Please Select one at least sales order")
        request_list = []
        products_dict = {}
        product_list = []
        for request in mrp_request_objs:
            request_list.append(request.name)
            print("request-----------------------------------------------------------------------------")
            print(request)
            for product_line in request.bom_line_ids:
                # print("============filtered_product=====", product_line)
                if not product_line.product_id.id in products_dict:
                    products_dict[product_line.product_id.id] = [product_line.product_id.name,product_line.product_total_qty]
                else:
                    print("products_dict[product_line.product_id] + product_line.product_total_qty")
                    print(products_dict[product_line.product_id.id][1] + product_line.product_total_qty)
                    products_dict[product_line.product_id.id][1] = products_dict[
                                                                 product_line.product_id.id][1] + product_line.product_total_qty
                print("products_dict")
                print(products_dict)
                print("products_dict")
        product_list = []
        print("products_dictproducts_dictproducts_dict")
        print("products_dictproducts_dictproducts_dict------------------------------------------------------------------")
        print(products_dict)
        for line in products_dict:
            vali = products_dict[line]
            product_list.append(vali)
        datas = {
            'order_no': {'name':self.sale_order_id.name,'partner_id':self.sale_order_id.partner_id.name,"mrp_date":self.sale_order_id.mrp_date},
            'products_qty': product_list,
            'request_list': request_list,

        }
        print(datas)
        return self.env.ref('manufacturing_furnature.action_report_mrp_total_all_saleorder').report_action([],
                                                                                                           data=datas)
