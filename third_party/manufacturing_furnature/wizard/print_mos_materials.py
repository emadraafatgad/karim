from odoo import fields, models, api
from odoo.exceptions import ValidationError

class PrintMosMaterials(models.TransientModel):
    _name = 'mos.all.materials'

    mos_ids = fields.Many2many('mrp.production')

    @api.multi
    def print_mos_material(self):
        if self.mos_ids:
            production_list = []
            products_dict = {}
            product_list = []
            for mo_operation in self.mos_ids:
                production_list.append(mo_operation.name)
                print("request-----------------------------------------------------------------------------")
                print(mo_operation)
                for product_line in mo_operation.move_raw_ids:
                    # print("============filtered_product=====", product_line)
                    if not product_line.product_id.id in products_dict:
                        products_dict[product_line.product_id.id] = [product_line.product_id.name,product_line.product_uom_qty]
                    else:
                        print("products_dict[product_line.product_id] + product_line.product_uom_qty")
                        print(products_dict[product_line.product_id.id][1] + product_line.product_uom_qty)
                        products_dict[product_line.product_id.id][1] = products_dict[
                                                                     product_line.product_id.id][1] + product_line.product_uom_qty
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
                'products_qty': product_list,
                'request_list': production_list,

            }
            print(datas)
            return self.env.ref('manufacturing_furnature.action_report_mrp_all_mos').report_action([], data=datas)
