from odoo import models, fields, api, _

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    lot_name_custom = fields.Char(string='Lot Name')

    def action_show_details(self):
        view = self.env.ref('bi_sale_discount_with_tax.view_stock_move_line_lots')
        return {
            'name': _('Lots'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.move.line',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
        }

    # def write(self, vals):
    #     res = super(StockMoveLine, self).write(vals)
    #     breaking_char = '\n'
    #     split_lines = []
    #     for move in self.picking_id.move_ids_without_package:
    #         if move.product_id.id == self.product_id.id:
    #             move_id = move.id
    #             break;
    #     if vals.get('lot_name_custom', False):
    #         if breaking_char in (self.lot_name_custom or ''):
    #             move_lines_commands = []
    #             split_lines = self.lot_name_custom.split(breaking_char)
    #             split_lines = list(filter(None, split_lines))
    #             move_line_vals = {
    #                 'picking_id': self.picking_id.id,
    #                 'location_dest_id': self.location_dest_id.id,
    #                 'location_id': self.location_id.id,
    #                 'product_id': self.product_id.id,
    #                 'product_uom_id': self.product_id.uom_id.id,
    #                 'qty_done': 1,
    #                 'product_uom_qty': 0,
    #                 'move_id': move_id,
    #             }
    #             # 'move_id': self.picking_id.move_ids_without_package.filtered(lambda move: move.product_id.id == self.product_id.id)
    #             lot_id = self.env['stock.production.lot'].search([('product_id', '=', self.product_id.id), ('name', '=', split_lines[0])])
    #             move_lines_commands.append((1, self.id, {'lot_id': lot_id.id, 'qty_done': 1,
    #                 'product_uom_qty': 0, 'move_id': move_id}))
    #             # quants = self.env['stock.quant']._update_reserved_quantity(
    #             #         self.product_id, self.location_id, 1, lot_id=lot_id,
    #             #         )
    #             for lot_name in split_lines[1:]:
    #                 lot_id = self.env['stock.production.lot'].search([('product_id', '=', self.product_id.id), ('name', '=', lot_name)])
    #                 if lot_id:
    #                     move_line_cmd = dict(move_line_vals, lot_id=lot_id.id)
    #                     move_lines_commands.append((0, 0, move_line_cmd))
    #                     # quants = self.env['stock.quant']._update_reserved_quantity(
    #                     #     self.product_id, self.location_id, 1, lot_id=lot_id,
    #                     # )
    #             self.picking_id.move_line_ids_without_package = move_lines_commands
    #     return res

class StockMove(models.Model):
    _inherit = "stock.move"

    lot_name_custom = fields.Char(string='Lot/Serial Number Name')

    def action_show_details_delivery_lots(self):
        view = self.env.ref('bi_sale_discount_with_tax.view_stock_move_lots')
        return {
            'name': _('Lots/Serial Numbers'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.move',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
        }


    def action_show_details(self):
        """ Returns an action that will open a form view (in a popup) allowing to work on all the
        move lines of a particular move. This form view is used when "show operations" is not
        checked on the picking type.
        """
        self.ensure_one()

        # If "show suggestions" is not checked on the picking type, we have to filter out the
        # reserved move lines. We do this by displaying `move_line_nosuggest_ids`. We use
        # different views to display one field or another so that the webclient doesn't have to
        # fetch both.
        if self.picking_id.picking_type_id.show_reserved:
            view = self.env.ref('bi_sale_discount_with_tax.view_stock_move_operations_custom_lot_serial')
        else:
            view = self.env.ref('stock.view_stock_move_nosuggest_operations')

        picking_type_id = self.picking_type_id or self.picking_id.picking_type_id
        return {
            'name': _('Detailed Operations'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.move',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': dict(
                self.env.context,
                show_owner=self.picking_type_id.code != 'incoming',
                # show_lots_m2o=self.has_tracking != 'none' and (picking_type_id.use_existing_lots or self.state == 'done' or self.origin_returned_move_id.id),  # able to create lots, whatever the value of ` use_create_lots`.
                show_lots_text=self.has_tracking != 'none' and picking_type_id.use_create_lots and not picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id,
                show_lots_custom_text=True,
                show_source_location=self.picking_type_id.code != 'incoming',
                show_destination_location=self.picking_type_id.code != 'outgoing',
                show_package=not self.location_id.usage == 'supplier',
                show_reserved_quantity=self.state != 'done' and not self.picking_id.immediate_transfer and self.picking_type_id.code != 'incoming'
            ),
        }

    def _generate_lot_serial_move_line_commands(self, lot_names, move_id, origin_move_line=None):
        """Return a list of commands to update the move lines (write on
        existing ones or create new ones).
        Called when user want to create and assign multiple serial numbers in
        one time (using the button/wizard or copy-paste a list in the field).

        :param lot_names: A list containing all serial number to assign.
        :type lot_names: list
        :param origin_move_line: A move line to duplicate the value from, default to None
        :type origin_move_line: record of :class:`stock.move.line`
        :return: A list of commands to create/update :class:`stock.move.line`
        :rtype: list
        """
        self.ensure_one()

        # Select the right move lines depending of the picking type configuration.
        move_lines = self.env['stock.move.line']
        move_lines = self.move_line_ids.filtered(lambda ml: not ml.lot_id and not ml.lot_name_custom)

        if origin_move_line:
            location_dest = origin_move_line.location_dest_id
        else:
            location_dest = self.location_dest_id._get_putaway_strategy(self.product_id)
        move_line_vals = {
            'picking_id': self.picking_id.id,
            'location_dest_id': location_dest.id or self.location_dest_id.id,
            'location_id': self.location_id.id,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_id.uom_id.id,
            'qty_done': origin_move_line.qty_done or 1,
            'product_uom_qty': 1,
            'move_id': move_id,
        }

        move_lines_commands = []
        for lot_name in lot_names[1:]:
            if move_lines:
                lot_id = self.env['stock.production.lot'].search([('product_id', '=', origin_move_line.product_id.id), ('name', '=', lot_name)])
                move_lines_commands.append((1, move_lines[0].id, {
                    'lot_id': lot_id,
                    'qty_done': 1,
                    'product_uom_qty': 1,
                }))
                move_lines = move_lines[1:]
            else:
                lot_id = self.env['stock.production.lot'].search([('product_id', '=', origin_move_line.product_id.id), ('name', '=', lot_name)])
                if lot_id:
                    move_line_cmd = dict(move_line_vals, lot_id=lot_id.id)
                    move_lines_commands.append((0, 0, move_line_cmd))
        return move_lines_commands

    @api.onchange('move_line_ids')
    def onchange_move_line_ids_lot_custom(self):
        breaking_char = '\n'
        split_lines = []
        for move in self.picking_id.move_ids_without_package:
            if move.product_id.id == self.product_id.id:
                move_id = move.id
                break;
        move_lines = self.move_line_ids
        for line in move_lines:
            if breaking_char in (line.lot_name_custom or ''):
                move_lines_commands = []
                split_lines = line.lot_name_custom.split(breaking_char)
                split_lines = list(filter(None, split_lines))
                lot_id = self.env['stock.production.lot'].search([('product_id', '=', line.product_id.id), ('name', '=', split_lines[0])])
                if lot_id:
                    line.lot_id = lot_id.id
                    line.qty_done = 1
                    line.product_uom_qty = 1
                    line.lot_name_custom = False
                    quants = self.env['stock.quant']._update_reserved_quantity(
                            self.product_id, self.location_id, 1, lot_id=lot_id,
                        )
                move_lines_commands = self._generate_lot_serial_move_line_commands(
                    split_lines,
                    move_id,
                    origin_move_line=line,
                )
                self.update({'move_line_ids': move_lines_commands})
                for lot_name in split_lines[1:]:
                    lot_id = self.env['stock.production.lot'].search([('product_id', '=', self.product_id.id), ('name', '=', lot_name)])
                    if lot_id:
                        quants = self.env['stock.quant']._update_reserved_quantity(
                                self.product_id, self.location_id, 1, lot_id=lot_id,
                            )
                if not line.lot_id:
                    line.unlink()
                move_lines_without_lots = self.move_line_ids.filtered(lambda self: not self.lot_id)
                move_lines_without_lots and move_lines_without_lots.unlink()
                break;


    def write(self, vals):
        res = super(StockMove, self).write(vals)
        if self._context.get('show_lots_custom_text'):
            self.move_line_ids.product_uom_qty = 1
            # self.picking_id.action_assign()
        return res
