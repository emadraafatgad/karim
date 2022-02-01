# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.addons import decimal_precision as dp

class BomQuantityCheck(models.Model):
    _name = "bom.quantity.check"
    _description = 'BOM Quantity Check'
    
    @api.multi
    def write(self, vals):
        res = super(BomQuantityCheck, self).write(vals)
        if 'product_qty' in vals:
            bom_id = self.env['mrp.bom'].search([('id', '=', self.bom_id.id)],limit=1)
            bom_id.total_product_qty = self.product_qty
        return res
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('bom.quantity.check') or '/'
        vals['is_check_button'] = True
        bom_id = self.env['mrp.bom'].search([('id', '=', vals.get('bom_id'))],limit=1)
        bom_id.total_product_qty = vals.get('product_qty')
        return super(BomQuantityCheck, self).create(vals)
    
    @api.model
    def _get_default_picking_type(self):
        return self.env['stock.picking.type'].search([
            ('code', '=', 'mrp_operation'),
            ('warehouse_id.company_id', 'in', [self.env.context.get('company_id', self.env.user.company_id.id), False])],
            limit=1).id
    
    @api.model
    def _get_default_manufacturer(self):
        return self.env['res.users'].browse(self.env.uid)
    
    
    name = fields.Char(string='Reference', readonly=True, copy=False)
    production_id = fields.Many2one('mrp.production',string='MRP Orders')
    product_id = fields.Many2one('product.product',
                                 domain=[('type', 'in', ['product', 'consu'])],
                                 required=True,
                                 string='Product')
    product_qty = fields.Float('Quantity to produce',
                               default=1.0, digits=dp.get_precision('Product Unit of Measure'),
                               required=True, track_visibility='onchange')
    bom_id = fields.Many2one('mrp.bom',string="Bill of Material")
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        default=_get_default_picking_type, required=True)
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get('mrp.production'),
        required=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure')
    user_id = fields.Many2one('res.users',
                               'Manufacturer',
                               track_visibility='onchange',
                               default=_get_default_manufacturer, required=True)
    is_check_button = fields.Boolean('Is button visible?')
    bom_line_ids = fields.One2many('mrp.bom.line', 'check_bom_id', 'BoM Lines', copy=True)
    state = fields.Selection(
            [('draft', 'Draft'),
             ('available', 'Available'),
             ('partially_available', 'Partially Available'),
             ('deficient', 'Deficient'),
             ('in_progress', 'In Progress'),
             ('done', 'Done')], string='State', readonly=True, default='draft', track_visibility='onchange')
    
    

    @api.onchange('product_id', 'picking_type_id', 'company_id')
    def onchange_product_id(self):
        if not self.product_id:
            self.bom_id = False
        else:
            bom = self.env['mrp.bom']._bom_find(product=self.product_id, picking_type=self.picking_type_id, company_id=self.company_id.id)
            if bom.type == 'normal':
                self.bom_id = bom.id
                self.product_qty = self.bom_id.product_qty
                self.product_uom_id = self.bom_id.product_uom_id.id
            else:
                self.bom_id = False
                self.product_uom_id = self.product_id.uom_id.id
            return {'domain': {'product_uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id)]}}
            
    
    @api.multi
    def check_bom_status(self):
        for bom in self:
            bom_line_ids = bom.bom_id.bom_line_ids
            if bom.bom_id:
                if all([bom_lines.calc_product_qty <= bom_lines.product_id.qty_available for bom_lines in bom_line_ids]):
                    view = self.env.ref('mapol_check_mrp_product_quantity.view_available_quantity')
                    wiz = self.env['available.quantity'].create({'bom_check_id': bom.id})
                    return {
                        'name': _('BOM Quantity status'),
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'available.quantity',
                        'views': [(view.id, 'form')],
                        'view_id': view.id,
                        'target': 'new',
                        'res_id': wiz.id,
                        'context': self.env.context,
                    }
                elif any([bom_lines.calc_product_qty <= bom_lines.product_id.qty_available for bom_lines in bom_line_ids]):   
                    view = self.env.ref('mapol_check_mrp_product_quantity.view_partial_quantity')
                    wiz = self.env['partial.quantity'].create({'bom_check_id': bom.id})
                    return {
                        'name': _('BOM Quantity status'),
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'partial.quantity',
                        'views': [(view.id, 'form')],
                        'view_id': view.id,
                        'target': 'new',
                        'res_id': wiz.id,
                        'context': self.env.context,
                    }
                else:
                    view = self.env.ref('mapol_check_mrp_product_quantity.view_no_quantity')
                    wiz = self.env['no.quantity'].create({'bom_check_id': bom.id})
                    return {
                        'name': _('BOM Quantity status'),
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'no.quantity',
                        'views': [(view.id, 'form')],
                        'view_id': view.id,
                        'target': 'new',
                        'res_id': wiz.id,
                        'context': self.env.context,
                    }
        return
    
    @api.multi
    def create_purchase_request(self):
        self.ensure_one()
        self.write({'state': "in_progress"})
        view_ref = self.env['ir.model.data'].get_object_reference('mapol_check_mrp_product_quantity', 'view_bom_purchase_request_form')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'bom.purchase.request',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }
    
    @api.multi
    def create_manufacture_order(self):
        self.ensure_one()
        self.write({'state': "in_progress"})
        view_ref = self.env['ir.model.data'].get_object_reference('mrp', 'mrp_production_form_view')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'context': {'default_product_uom_qty': self.product_qty,'default_product_id': self.product_id.id},
            'nodestroy': True,
        }
        
    @api.multi
    def move_done(self):
        self.write({'state': "done"})
    
    
    
    
    
