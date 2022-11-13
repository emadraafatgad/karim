import functools
from odoo import _, models, tools
import functools

from odoo import _, models, tools,exceptions


class MrpUnreserve(models.Model):
    _inherit = 'mrp.production'

    # def unreserve_all_lines(self):
    #     for line in self.move_raw_ids:
    #         line.action_unreserved_material()
    # def action_force_assign_pickings(self):
    #     """ Unreserve other pickings in order to reserve pickings in self """
    #     link_template = '<a href="#" data-oe-model="%s" data-oe-id="%d">%s</a>'
    #     to_unreserve = self._force_assign_find_moves()
    #     # print(to_unreserve,"***************************************")
    #
    #     # self.message_post(body=_(
    #     #     'Unreserved picking(s) %s in order to assign this one'
    #     # ) % ', '.join(to_unreserve.mapped('raw_material_production_id').mapped(
    #     #     lambda x: link_template % (x._name, x.id, x.name)
    #     # )))
    #     # rr = to_unreserve.mapped('raw_material_production_id')
    #     # print(rr)
    #     # for r in rr:
    #     #     r.message_post(body=_(
    #     #         'Unreserved this picking in order to assign %s'
    #     #     ) % ', '.join(self.mapped(
    #     #         lambda x: link_template % (x._name, x.id, x.name)
    #     #     )))
    #     return self.action_assign()
    #
    # def _force_assign_find_moves(self):
    #     # print(""" Return moves to unreserve in order to reserve pickings in self """)
    #     location_id = self.env['stock.location'].search([('id','=',12)])
    #     location = location_id
    #     # location = self.mapped('location_src_id')
    #     # print(location,"============")
    #     result = self.env['stock.move']
    #     assert len(location) == 1, 'Pickings need to be from the same location'
    #     float_compare = functools.partial(
    #         tools.float_compare,
    #         precision_digits=result._fields['product_qty'].digits,
    #     )
    #     print("result",result)
    #     candidates = self.env['stock.move']
    #     for move in self.mapped('move_raw_ids'):
    #         if move.state in ['done','assigned']:
    #             continue
    #         demand = (
    #                 move.product_qty - move.reserved_availability -
    #                 move.availability
    #         )
    #         # if float_compare(demand, 0) <= 0:
    #         #     continue
    #         to_unreserve = self.env['stock.move'].search([
    #             # ('id', 'not in', result.ids),
    #             ('raw_material_production_id', 'not in', self.ids),
    #             # ('raw_material_production_id.unreserve_visible', '=',True),
    #             ('location_id', '=', location.id),
    #             ('product_id', '=', move.product_id.id),
    #             ('state', 'in', ['assigned', 'partially_available']),
    #         ],  order='create_date asc')
    #         print("----------to_unreserve-------------")
    #         counter = 0
    #         reserved_availability = 0
    #         for mov in to_unreserve:
    #             print("reserved_availability 1 ! ", reserved_availability)
    #             counter += 1
    #             print("reserved_availability 2 @ ", reserved_availability)
    #             print(mov.state)
    #             state_brfore = mov.state
    #             print(state_brfore)
    #             mov._do_unreserve()
    #             print(state_brfore,"==----------->",mov.state)
    #             if reserved_availability >= move.reserved_availability:
    #                 break
    #             reserved_availability += mov.reserved_availability
    #             if mov.state != state_brfore:
    #                 pass
    #         move.assign()
    #         print(to_unreserve)
    #     return True

    def action_force_assign_pickings(self):
        """ Unreserve other pickings in order to reserve pickings in self """
        link_template = '<a href="#" data-oe-model="%s" data-oe-id="%d">%s</a>'
        to_unreserve = self._force_assign_find_moves()
        to_unreserve._do_unreserve()
        # self.message_post(body=_(
        #     'Unreserved picking(s) %s in order to assign this one'
        # ) % ', '.join(to_unreserve.mapped('picking_id').mapped(
        #     lambda x: link_template % (x._name, x.id, x.name)
        # )))
        # to_unreserve.mapped('picking_id').message_post(body=_(
        #     'Unreserved this picking in order to assign %s'
        # ) % ', '.join(self.mapped(
        #     lambda x: link_template % (x._name, x.id, x.name)
        # )))
        return self.action_assign()

    def _force_assign_find_moves(self):
        """ Return moves to unreserve in order to reserve pickings in self """
        # location = self.mapped('location_id')
        result = self.env['stock.move']
        # assert len(location) == 1, 'Pickings need to be from the same location'
        float_compare = functools.partial(
            tools.float_compare,
            precision_digits=result._fields['product_qty'].digits,
        )
        # print(tools.float_compare,result._fields['product_qty'].digits,)
        # print(float_compare)
        for move in self.mapped('move_raw_ids'):
            demand = (
                move.product_qty - move.reserved_availability
            )
            print( move.product_id.name ,demand,"demand")
            if demand <= 0.0:
                print(demand, " float_compare(demand, 0) : --> ", float_compare(demand, 0))
                continue
            # if float_compare(demand, 0,precision_rounding=4) <= 0:
            #     print(demand, " float_compare(demand, 0) : --> ",float_compare(demand, 0))
            #     continue
            candidates = self.env['stock.move'].search([

                ('id', 'not in', result.ids),
                ('raw_material_production_id', 'not in', self.ids),
                ('location_id', '=', 12),
                ('product_id', '=', move.product_id.id),
                ('state', 'in', ('partially_available', 'assigned')),
            ], order='write_date asc')
            print(candidates)
            for candidate in candidates:
                # if float_compare(demand, 0,precision_rounding=4) > 0:
                if demand > 0.0:
                    result += candidate
                    demand -= candidate.reserved_availability
                else:
                    break
            # if float_compare(demand, 0) > 0:
            #     raise exceptions.UserError(
            #         _('Cannot unreserve enough %s, missing quantity is %d') % (
            #             move.product_id.name, demand
            #         )
            #     )
        return result