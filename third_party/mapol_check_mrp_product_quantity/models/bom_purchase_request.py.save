# -*- coding: utf-8 -*-

from odoo import api, fields, models, _ , SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class BOMPurchaseRequest(models.Model):

    _name = 'bom.purchase.request'
    _description = 'BOM Purchase Request'
    _inherit = ['mail.thread']
    
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('bom.purchase.request') or '/'
        return super(BOMPurchaseRequest, self).create(vals)
    
    @api.model
    def _get_default_requester(self):
        return self.env['res.users'].browse(self.env.uid)
    
    
    name = fields.Char('Request Reference', size=32, readonly=True,track_visibility='onchange')
    user_id = fields.Many2one('res.users',
                               'Requester',
                               required=True,
                               default=_get_default_requester,
                               track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Approver', required=True,
                                  track_visibility='onchange')
    
    note = fields.Text('Description')

    line_ids = fields.One2many('bom.purchase.request.line', 'request_id',
                               'Products to Purchase',
                               readonly=False,
                               copy=True,
                               track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'),
                            ('to_approve', 'To approve'),
                            ('approved', 'Approved'),
                            ('rejected', 'Rejected'),
                            ('done', 'Done')
                            ],string='Status',index=True,track_visibility='onchange',required=True,
                             copy=False,default='draft')
    
    
    @api.multi
    def make_to_draft(self):
        return self.write({'state': 'draft'})
    
    @api.multi
    def button_approve(self):
        return self.write({'state': 'to_approve'})
    
    @api.multi
    def set_approved(self):
        return self.write({'state': 'approved'})

    @api.multi
    def set_to_rejected(self):
        self.mapped('line_ids').do_cancel()
        return self.write({'state': 'rejected'})

    @api.multi
    def mark_done(self):
        return self.write({'state': 'done'})
    
    @api.multi
    def make_purchase_quotation(self):
        lines = []
        for line in self.line_ids:
#           taxes_id = self.env['account.fiscal.position'].map_tax(line.product_id.supplier_taxes_id).id
            product_line = (0, 0, {'product_id' : line.product_id.id,
                                   'state' : 'draft',
                                   'product_uom' : line.product_id.uom_po_id.id,
                                   'price_unit' : 0,
                                   'date_planned' :  datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
#                                    'taxes_id' : [(6,0,[taxes_id])],
                                   'product_qty' : line.product_qty,
                                   'name' : line.product_id.name
                                   })
            lines.append(product_line)
        view_id = self.env.ref('purchase.purchase_order_form')
        return {
            'name': _('New Purchase Quotation'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'view_id': view_id.id,
            'views': [(view_id.id, 'form')],
            'context': {
                'default_order_line': lines,'default_state': 'draft',}
        }


class BOMPurchaseRequestLine(models.Model):

    _name = "bom.purchase.request.line"
    _description = "BOM Purchase Request Line"
    _inherit = ['mail.thread']
    
    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=[('purchase_ok', '=', True)], required=True,
        track_visibility='onchange')
    name = fields.Char('Description', size=256,
                       track_visibility='onchange')
    product_uom_id = fields.Many2one('product.uom', 'Product Unit of Measure',
                                     track_visibility='onchange')
    product_qty = fields.Float(string='Product Quantity', track_visibility='onchange', digits=dp.get_precision('Product Unit of Measure'))
    request_id = fields.Many2one('bom.purchase.request',
                                 'Purchase Request',
                                 ondelete='cascade', readonly=True)
    request_date = fields.Date(string='Purchase Request Date', required=True,
                                track_visibility='onchange',
                                default=fields.Date.context_today)
    state = fields.Selection([('draft', 'Draft'),
                              ('to_approve', 'To approve'),
                              ('approved', 'Approved'),
                              ('rejected', 'Rejected'),
                              ('done', 'Done')
                              ], string='Status', index=True,related='request_id.state',
                             store=True)
    partner_id = fields.Many2one('res.partner',domain="[('supplier','=','True')]",string="Vendor",
                                 compute="get_vendor_pricelist",readonly=False)
    product_available = fields.Float(related='product_id.qty_available')
    product_reserved = fields.Float(related='product_id.outgoing_qty')
    net_available = fields.Float(compute='get_vendor_pricelist')


    @api.depends('product_id')
    def get_vendor_pricelist(self):
        for rec in self:
            print("vskvmdlskmd")
            vendor_list = self.env['product.supplierinfo'].search([('product_tmpl_id','=',rec.product_id.product_tmpl_id.id)],limit=1)
            print(vendor_list)
            if vendor_list:
                rec.partner_id = vendor_list.name
            qty_available = rec.product_id.qty_available
            outgoing = rec.product_id.outgoing_qty
            print(qty_available - outgoing)
            rec.net_available = qty_available - outgoing


    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            if self.product_id.code:
                name = '[%s] %s' % (name, self.product_id.code)
            if self.product_id.description_purchase:
                name += '\n' + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.name = name
