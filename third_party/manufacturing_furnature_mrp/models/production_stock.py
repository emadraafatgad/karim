from odoo import fields,api,models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import Warning


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def button_plan(self):
        """ Create work orders. And probably do stuff, like things. """
        for line in self:
            for rec in line.move_raw_ids:
                deff = rec.reserved_availability - rec.product_uom_qty
                if deff < 0:
                    print("not enough reserved qty", deff)
                    raise ValidationError(_('Not Enough reserved Qty.'))
                # production_def = rec.quantity_done - rec.product_uom_qty
                # if production_def > 0:
                #     raise Warning(_('This manufacturing order used More than planed'))
                # elif production_def < 0:
                #     raise Warning(_('This manufacturing order used Less than planed'))
        return super(MRPProduction,self).button_plan()

    @api.multi
    def button_mark_done(self):
        """ Create work orders. And probably do stuff, like things. """
        for line in self:
            for rec in line.move_raw_ids:
                production_def = rec.quantity_done - rec.product_uom_qty
                if production_def > 0:
                    line.create_po_with_difference(line,rec.product_id,production_def)
                    # raise Warning(_('This manufacturing order used More than planed'))
                elif production_def < 0:
                    raise Warning(_('This manufacturing order used Less than planed'))
        return super(MRPProduction,self).button_mark_done()

    def create_po_with_difference(self,objline,product_id,production_def):
        purchase_order_obj = self.env['purchase.order.line'].search([('product_id','=',product_id.id),
                                                                     ('state','=', 'draft')])
        if purchase_order_obj:
            for order_line in purchase_order_obj:
                print(order_line,"purchase_order_obj",order_line.state)
                qty = production_def + order_line.product_qty
                origin = order_line.order_id.origin + ', '+ objline.name if order_line.order_id.origin else objline.name
                print(origin,"origin",qty)
                order_line.order_id.origin = origin
                order_line.product_qty = qty
        else:
            objline.create_purchase_order(product_id,production_def)

    def create_purchase_order(self,product_id,product_qty):
        vendor_id = self.env['product.supplierinfo'].search([('product_tmpl_id','=',product_id.id)],limit=1)
        print(vendor_id.name)
        if vendor_id.name :
            po_obj  = self.env['purchase.order'].search([('partner_id','=',vendor_id.name.id),('state','=','draft')])
            if po_obj :
                self.create_po_order_line(self, product_id, product_qty, po_obj)
        else:
            purchase_obj = {
                'partner_id':vendor_id.name.id,
                'date_order':fields.Datetime.now()
            }
            purchase_create = self.env['purchase.order'].create(purchase_obj)
            print(purchase_obj)
            self.create_po_order_line(self, product_id, product_qty, purchase_create)

    def create_po_order_line(self,product_id,product_qty,purchase_create):
        order_line = {'product_id': product_id.id,
                      'name': _(str(product_id.name) + "This Material is needed for new Production"),
                      'product_qty': product_qty,
                      'price_unit': product_id.standard_price,
                      'order_id': purchase_create.id,
                      'product_uom': product_id.uom_po_id.id,
                      'date_planned': fields.Datetime.now()
                      }
        purchase_line = self.env['purchase.order.line'].create(order_line)
        print(purchase_line)
