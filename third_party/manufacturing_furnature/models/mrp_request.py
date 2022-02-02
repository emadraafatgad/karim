from datetime import datetime

from odoo import api, models, fields


class NewManufacturingRequest(models.Model):
    _name = 'mrp.production.request'
    _rec_name = 'product_id'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char("Code", readonly=True, copy=False, default='New', track_visibility='onchange')
    product_id = fields.Many2one('product.product', readonly=True
                                  , required=True)
    quantity_qty = fields.Float(string="Product Quantity", readonly=True)
    bom_id = fields.Many2one('mrp.bom', readonly=True)
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', readonly=True)
    delivery_date = fields.Date(readonly=True)
    origin = fields.Char(string="Customer Name", readonly=True)
    state = fields.Selection([('draft', 'draft'), ('Confirmed', 'MRP Order'),('not','Not MRP'),
                              ('bom', 'Purchase Requested')], track_visibility='onchange',
                             default='draft', readonly=True)
    sale_order_id = fields.Many2one('sale.order', readonly=True)
    city_id = fields.Many2one('res.city', 'City', related='sale_order_id.city_id', store=True,track_visibility='onchange',)
    bom_line_ids = fields.One2many('mrp.request.line', 'request_id', readonly=True)
    paint_ids = fields.One2many('mrp.paint.request', 'request_id',track_visibility='onchange',)
    carpenter_ids = fields.One2many('mrp.carpenter.request', 'request_id',track_visibility='onchange',)
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
    ], string='Invoice Status', related='sale_order_id.invoice_status', store=True, readonly=True)
    payment_status = fields.Selection([('not', 'Not Paid'), ('partial', 'Partially Paid'), ('paid', 'Paid'), ],
                                      track_visibility='onchange', store=True,
                                      related='sale_order_id.payment_status')

    attachment = fields.Binary()
    note = fields.Text(track_visibility='onchange',readonly=True)
    mrp_routs_ids = fields.Many2many('mrp.checklist.line', domain="[('product_id','=',product_id)]")
    current_operation = fields.Many2one('rout.name',track_visibility='onchange')

    @api.multi
    def get_bom_line_ids(self):
        component_line = self.env['mrp.request.line']
        for line in self.bom_id.bom_line_ids:
            # print("line", line, line.product_id.id, line.product_qty, line.product_uom_id.id, self.id)
            component_line.create({
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'product_uom_id': line.product_uom_id.id,
                'request_id': self.id
            })

    # @api.model
    def get_request_attachments(self):
        print("=========-------------==========")
        attachments = self.env['ir.attachment'].search(
            [('res_model', '=', 'sale.order'), ('res_id', '=', self.sale_order_id.id)])
        print("attachement",attachments)
        if attachments:
            for attachment in attachments:
                values = {
                    'name': attachments.name,
                    'datas': attachments.datas,
                    'datas_fname': attachments.datas_fname,
                    'res_model': self._name,
                    'res_id': self.id,
                    'type': 'binary',  # override default_type from context, possibly meant for another model!
                }
                # print(values,"values")
                attachment = self.env['ir.attachment'].create(values)
                self.write({'attachment_id': attachment.id})

    def send_to_mrp(self):
        self.ensure_one()
        mo_production_id = self.env['mrp.production'].create({
            'name': 'New',
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom_id.id,
            'origin': self.origin,
            'sale_order_id': self.sale_order_id.id,
            'product_qty': self.quantity_qty,
            'bom_id': self.bom_id.id,
            'date_planned_start': self.delivery_date,
            'delivery_date': self.delivery_date,
            'company_id': self.env.user.company_id.id,
        })
        mo_production_id.onchange_picking_type()
        print("procurement_group_id", mo_production_id.procurement_group_id.name)
        mo_production_id._compute_picking_ids()
        self.state = 'Confirmed'

    @api.multi
    def create_purchase_request(self):
        self.ensure_one()
        if self.state == 'Confirmed':
            lines = []
            customer_add = False
            for line in self.bom_id.bom_line_ids:
                request_line = self.env['bom.purchase.request.line'].search([('product_id', '=', line.product_id.id),
                                                                             ('state', 'in', ['draft', 'to_approve'])])
                if request_line:
                    qty = request_line.product_qty
                    needed_qty = line.product_qty * self.quantity_qty
                    totol = qty + needed_qty
                    request_line.product_qty = totol
                    print(request_line.request_id, "bool")
                    if not customer_add:
                        request_line.request_id.materials_for = request_line.request_id.materials_for + self.origin + ' , '
                        customer_add = True
                else:
                    request = self.env['bom.purchase.request']
                    request_id = self.env['bom.purchase.request'].search([('approver_id', '=', self.env.user.id),
                                                                          ('sale_order', "=", False),
                                                                          ('state', 'in', ['draft', 'to_approve'])])
                    if request_id:
                        request = request_id
                        if not customer_add:
                            request_id.materials_for = request_id.materials_for + self.origin + ' , '
                        customer_add = True
                    else:
                        request_id = self.env['bom.purchase.request'].create({'approver_id': self.env.user.id,
                                                                              'user_id': self.env.user.id,
                                                                              'materials_for': self.origin + ' , '
                                                                              })
                        customer_add = True
                        request = request_id
                    request_line_id = self.env['bom.purchase.request.line'].create(
                        {
                            'product_id': line.product_id.id,
                            'name': line.product_id.display_name,
                            'product_qty': line.product_qty * self.quantity_qty,
                            'product_uom_id': line.product_uom_id.id,
                            'request_date': datetime.today(),
                            'request_id': request.id
                        })
        self.state = 'bom'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('mrp.production.requests') or 'New'
        result = super(NewManufacturingRequest, self).create(vals)
        return result


class ManufacturingRequestLine(models.Model):
    _name = 'mrp.request.line'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    request_id = fields.Many2one('mrp.production.request')
    product_id = fields.Many2one('product.product')
    virtual_available = fields.Float(string="Forcaste", related="product_id.virtual_available", store=True)
    product_qty = fields.Float(string="Quantity")
    product_total_qty = fields.Float(string="Total Quantity", compute="calc_total_product_lines", store=True)
    product_uom_id = fields.Many2one('uom.uom', string="Unit Of Measure")
    partner_id = fields.Many2one('res.partner', domain="[('supplier','=','True')]")
    delivery_date = fields.Date(sotre=True, related="request_id.delivery_date")
    origin = fields.Char(string="Customer Name", readonly=True, related="request_id.origin", store=True)
    state = fields.Selection([('draft', 'draft'), ('Confirmed', 'MRP Order'),
                              ('bom', 'Purchase Requested')], track_visibility='onchange',
                             related="request_id.state", store=True)
    quantity_qty = fields.Float(string="Product Quantity", related="request_id.quantity_qty", )

    @api.depends('request_id', 'product_qty')
    def calc_total_product_lines(self):
        for rec in self:
            # print("request_id", rec.request_id)
            # print("qty-qty-qty-qty")
            rec.product_total_qty = rec.product_qty * rec.quantity_qty
