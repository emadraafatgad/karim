from odoo import fields, models


class MrpCarpenterRequest(models.Model):
    _name = 'mrp.carpenter.request'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    product_id = fields.Many2one('product.product', string="Finished Product", track_visibility='onchange',
                                 domain="[('sale_ok','=',True)]", required=1)
    request_id = fields.Many2one('mrp.production.request', )
    customer = fields.Char(related='request_id.origin', track_visibility='onchange')
    delivery_date = fields.Date(track_visibility='onchange', related='request_id.delivery_date')
    operation_id = fields.Many2one('mrp.routing.workcenter', track_visibility='onchange',
                                   domain="[('operation_type','in',['carpenter'])]",
                                   required=True)
    worker_id = fields.Many2one('res.partner', states={'start': [('readonly', True)], 'cancel': [('readonly', True)],
                                                       'done': [('readonly', True)]})
    state = fields.Selection([('draft', 'draft'), ('start', 'Started'),
                              ('done', 'Done'), ('cancel', 'Cancel')], track_visibility='onchange')
    status = fields.Selection([('draft', 'draft'), ('progress', 'In progress'),
                               ('done', 'Done')], track_visibility='onchange', default='draft')

    def done_status(self):
        self.status = 'done'

    def inprogress_status(self):
        self.status = 'progress'

