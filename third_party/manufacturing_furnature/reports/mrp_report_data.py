from odoo import fields, models, api


class ReportMrpOperationReport(models.AbstractModel):
    _name = 'report.manufacturing_furnature.report_mrp_total_saleorder'
    _description = "Reprort for mrp"

    @api.model
    def _get_report_values(self, docids, data):
        print("================================")
        total = []
        print(self.env.context.get('active_id'))
        docs = self.env["mrp.production.request"].browse(docids[0])
        production_lines = self.env["mrp.request.line"].search([('request_id','=',docids[0])])
        print(production_lines,"production_line")
        products_total = {}
        for line in production_lines:
            if line.product_id.display_name in products_total:
                print(line.product_id.display_name)
                products_total[line.product_id.display_name] = products_total[line.product_id.display_name] + line.product_qty
            else:
                print(line.product_id.display_name)
                products_total[line.product_id.display_name] = line.product_qty
        print(products_total)
        protduct_name = []
        product_total = []
        for key , value in products_total.items():
            term = [key,value]
            protduct_name.append(term)
            # product_total.append(products_total[key])
        print(protduct_name)
        print(docs)

        print("======================================")
        return {
            'doc_ids': self.ids,
            'products_total': products_total,
            'materials_docs':protduct_name,
            'docs': docs,
        }
