# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from datetime import datetime
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = "mrp.production"
    
    machine_id = fields.Many2one('machine.allocation',string="Machine")
    total_hours = fields.Float('Total Hours')
    
    @api.multi
    def write(self, vals):
        res = super(MrpProduction, self).write(vals)
        if 'machine_id' and 'total_hours' in vals:
            mrp_ids = self.search([('state', '!=', 'done')])
            count = 0
            datetime = self.date_planned_start
            date = datetime.strftime('%Y-%m-%d')
            for rec in mrp_ids:
                if rec.machine_id.id == self.machine_id.id:
                    if date == str(self.machine_id.date):
                        count += rec.total_hours
            if count > self.machine_id.total_hours_per_day:
                raise ValidationError(_("Total hours for the machine exceeds."))
        return res
    
    @api.multi
    def create_purchase_request(self):
        self.ensure_one()
        lines = []
        for line in self.move_raw_ids:
            if line.product_uom_qty != line.reserved_availability:
                product_line = (0, 0, {'product_id' : line.product_id.id,
                                       'name' : line.product_id.name,
                                       'product_qty' : line.product_uom_qty,
                                       'request_date' : datetime.today(),
                                       })
                lines.append(product_line)
        view_ref = self.env['ir.model.data'].get_object_reference('mapol_check_mrp_product_quantity', 'view_bom_purchase_request_form')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'bom.purchase.request',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'context': {'default_line_ids': lines,
                        'default_approver_id': self.user_id.id},
            'nodestroy': True,
        }
                    

# class NewManufacturingRequest(models.Model):
#     _inherit = 'mrp.production.request'
#
#     @api.multi
#     def create_purchase_request(self):
#         self.ensure_one()
#         lines = []
#         for line in self.bom_id.bom_line_ids:
#             if line.product_uom_qty != line.reserved_availability:
#                 product_line = (0, 0, {'product_id': line.product_id.id,
#                                        'name': line.product_id.name,
#                                        'product_qty': line.product_uom_qty,
#                                        'request_date': datetime.today(),
#                                        })
#                 lines.append(product_line)
#         view_ref = self.env['ir.model.data'].get_object_reference('mapol_check_mrp_product_quantity',
#                                                                   'view_bom_purchase_request_form')
#         view_id = view_ref and view_ref[1] or False,
#         return {
#             'type': 'ir.actions.act_window',
#             'res_model': 'bom.purchase.request',
#             'view_type': 'form',
#             'view_mode': 'form',
#             'view_id': view_id,
#             'target': 'current',
#             'context': {'default_line_ids': lines,
#                         'default_approver_id': self.user_id.id},
#             'nodestroy': True,
#         }
