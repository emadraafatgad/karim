from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BOMPurchaseRequest(models.Model):
    _inherit = 'bom.purchase.request'

    @api.model
    def _get_default_picking_type(self):
        return self.env['stock.picking.type'].search([
            ('barcode', '=', 'WH-RECEIPTS'),
            ('warehouse_id.company_id', 'in',
             [self.env.context.get('company_id', self.env.user.company_id.id), False])],
            limit=1).id
    sale_order = fields.Boolean()
    materials_for = fields.Char(readonly=True)
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        default=_get_default_picking_type, required=True)

    @api.multi
    def make_purchase_quotation(self):
        lines = []

        for line in self.line_ids:
            #           taxes_id = self.env['account.fiscal.position'].map_tax(line.product_id.supplier_taxes_id).id
            if line.partner_id:
                po_obj = self.env['purchase.order'].search(
                    [('partner_id', '=', line.partner_id.id), ('state', '=', 'draft')],limit=1)
                print(po_obj, "PO Object")
                if po_obj:
                    po_id = po_obj
                else:
                    purchase_obj = {
                        'partner_id': line.partner_id.id,
                        'date_order': fields.Datetime.now(),
                        'picking_type_id': self.picking_type_id.id
                    }
                    purchase_create = self.env['purchase.order'].create(purchase_obj)
                    print(purchase_obj)
                    po_id = purchase_create
                self.env['product.supplierinfo']
                supplier_info = self.env['product.supplierinfo'].sudo().search([
                    ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                    ('name','=',line.partner_id.id)
                ])
                order_line = {
                          'product_id': line.product_id.id,
                          'name': line.name,
                          'product_qty': line.product_qty,
                          'price_unit': supplier_info.price,
                          'order_id': po_id.id,
                          'product_uom': line.product_id.uom_po_id.id,
                          'date_planned': fields.Datetime.now()
                              }
                print("==============================****************************")
                print(order_line)
                purchase_line = self.env['purchase.order.line'].create(order_line)
                print({
                          'product_id': purchase_line.product_id.id,
                          'name': _(str(purchase_line.product_id.name) + "This Material is needed for new Production"),
                          'product_qty': purchase_line.product_qty,
                          'price_unit': purchase_line.product_id.standard_price,
                          'product_uom': purchase_line.product_id.uom_po_id.id,
                          'date_planned': fields.Datetime.now()
                              })
                # purchase_line.onchange_product_id()
                # purchase_line.write({'product_qty': purchase_line.product_qty})

                print("*****************************************************************")
                self.state = "done"
            else:
                raise ValidationError(
                    _('You must Select A Vendor To Each Line'))

        # view_id = self.env.ref('purchase.purchase_order_form')
        # return {
        #     'name': _('New Purchase Quotation'),
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'purchase.order',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'target': 'new',
        #     'view_id': view_id.id,
        #     'views': [(view_id.id, 'form')],
        #     'context': {
        #         'default_order_line': lines, 'default_state': 'draft', }
        # }
