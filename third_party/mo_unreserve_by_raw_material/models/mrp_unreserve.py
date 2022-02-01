import functools
from odoo import _, models, tools
import functools

from odoo import _, models, tools,exceptions


class MrpUnreserve(models.Model):
    _inherit = 'mrp.production'

    # def unreserve_all_lines(self):
    #     for line in self.move_raw_ids:
    #         line.action_unreserved_material()
    def action_force_assign_pickings(self):
        """ Unreserve other pickings in order to reserve pickings in self """
        link_template = '<a href="#" data-oe-model="%s" data-oe-id="%d">%s</a>'
        print(link_template)
        to_unreserve = self._force_assign_find_moves()
        print(to_unreserve,"***************************************")
        to_unreserve._do_unreserve()
        print(to_unreserve,'to_unreserve')
        self.message_post(body=_(
            'Unreserved picking(s) %s in order to assign this one'
        ) % ', '.join(to_unreserve.mapped('raw_material_production_id').mapped(
            lambda x: link_template % (x._name, x.id, x.name)
        )))
        rr = to_unreserve.mapped('raw_material_production_id')
        print(rr)
        for r in rr:
            r.message_post(body=_(
                'Unreserved this picking in order to assign %s'
            ) % ', '.join(self.mapped(
                lambda x: link_template % (x._name, x.id, x.name)
            )))
        return self.action_assign()

    def _force_assign_find_moves(self):
        print(""" Return moves to unreserve in order to reserve pickings in self """)
        location_id = self.env['stock.location'].search([('id','=',12)])
        location = location_id
        # location = self.mapped('location_src_id')
        print(location,"============")
        result = self.env['stock.move']
        assert len(location) == 1, 'Pickings need to be from the same location'
        float_compare = functools.partial(
            tools.float_compare,
            precision_digits=result._fields['product_qty'].digits,
        )
        for move in self.mapped('move_raw_ids'):
            print(move.product_id.name,"<====================>",move)
            demand = (
                    move.product_qty - move.reserved_availability -
                    move.availability
            )
            if float_compare(demand, 0) <= 0:
                continue
            candidates = self.env['stock.move'].search([
                ('id', 'not in', result.ids),
                ('raw_material_production_id', 'not in', self.ids),
                # ('raw_material_production_id.unreserve_visible', '=',True),
                ('location_id', '=', location.id),
                ('product_id', '=', move.product_id.id),
                ('state', 'in', ('partially_available', 'assigned')),
            ], order='write_date asc')
            print(candidates,"7777777777777777777777777777")
            for candidate in candidates:
                if float_compare(demand, 0) > 0:
                    result += candidate
                    print(result)
                    demand -= candidate.reserved_availability
                    print(demand,"demain")
                else:
                    break
            # if float_compare(demand, 0) > 0:
            #     raise exceptions.UserError(
            #         _('Cannot unreserve enough %s, missing quantity is %d') % (
            #             move.product_id.name, demand
            #         )
            #     )
        return result
