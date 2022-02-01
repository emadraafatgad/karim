# ©  2015-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models


class MRPComponentChange(models.TransientModel):
    _name = "mrp.operation.change"
    _description = "MRP Component Change "

    operation_id = fields.Many2one('mrp.routing.workcenter', 'Operation')

    # @api.model
    # def default_get(self, fields_list):
    #     defaults = super(MRPComponentChange, self).default_get(fields_list)
    #     active_id = self.env.context.get("active_id", False)
    #     move = self.env["stock.move"].browse(active_id)
    #     if move.state == "done":
    #         raise UserError(_("The stock movement status does not allow modification"))
    #     defaults["product_id"] = move.product_id.id
    #     defaults["product_uom_qty"] = move.product_uom_qty
    #     return defaults

    @api.multi
    def do_change(self):
        active_id = self.env.context.get("active_id", False)
        mrp_production = self.env['mrp.production'].browse(active_id)
        print(mrp_production)
        print(('raw_material_production_id', '=', mrp_production.id), ('operation_id', '=', self.operation_id.id))
        moves = self.env["stock.move"].search(
            [('raw_material_production_id', '=', mrp_production.id), ('operation_id', '=', self.operation_id.id)])
        for move in moves:
            print(move)
            for line in move.active_move_line_ids:
                line.write(
                    {
                        "qty_done": line.product_qty,
                        "state": "done",
                    }
                )
            move._action_done()
