from datetime import datetime
from odoo.exceptions import ValidationError
from odoo import api, models, fields


class NewManufacturingRequest(models.Model):
    _name = 'mrp.production.request'
    _rec_name = 'product_id'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = "id DESC"

    name = fields.Char("Code", readonly=True, copy=False, default='New', track_visibility='onchange')
    product_id = fields.Many2one('product.product', readonly=True
                                 , required=True)
    quantity_qty = fields.Float(string="Product Quantity", readonly=True)
    bom_id = fields.Many2one('mrp.bom', readonly=True)
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', readonly=True)
    delivery_date = fields.Date(readonly=True)
    origin = fields.Char(string="Customer Name", readonly=True)
    state = fields.Selection([('draft', 'draft'), ('Confirmed', 'MRP Order'), ('not', 'Not MRP'),
                              ('bom', 'Purchase Requested')], track_visibility='onchange',
                             default='draft', readonly=True)
    for_export = fields.Boolean(default=False)
    mrp_operation_state = fields.Selection([('confirmed', 'Confirmed'), ('planned', 'Planned'),('progress', 'In Progress'), ('done', 'Not MRP'),
                                            ('cancel','Canceled')], track_visibility='onchange',
                             compute='get_mrp_state_from_mrp', readonly=True)
    so_number = fields.Char()
    is_shipped = fields.Boolean()

    def create_freight_order(self):
        for rec in self:
            if not rec.for_export or rec.is_shipped:
                continue
            open_freight = self.env['freight.order'].search([('state','=','draft')])
            if not open_freight:
                raise ValidationError('please create open freight')
            elif len(open_freight)>1:
                raise ValidationError('please add only one open freight')
            print(open_freight)
            print(open_freight.order_ids)
            print(open_freight.order_ids.mapped('purchase_id'))
            freight_line = open_freight.order_ids.filtered(lambda  l: not l.purchase_id)
            if not freight_line:
                raise ValidationError('Please add Line in freight for customize')
            print(freight_line)
            order_line = {
                'product_id': rec.product_id.id,
                'container_id': freight_line.container_id.id,
                'custom_or_stock':'custom',
                'quantity': rec.quantity_qty,
            }
            freight_line.container_line_ids =[(0,0,order_line)]





    def get_mrp_state_from_mrp(self):
        for rec in self:
            print('rec.sale_order_id')
            print(rec.sudo().sale_order_id.name)
            mrp = self.env['mrp.production'].sudo().search([('product_id','=',rec.product_id.id),('bom_id','=',rec.bom_id.id),('sale_order_id','=',rec.sale_order_id.id)],limit=1)
            print("mrp found")
            print(mrp)
            mapped_state = mrp.mapped('state')
            rec.mrp_operation_state = mrp.state
            # stat for stat in mapped_state if stat =='done':
            print('state',rec.mrp_operation_state)
    sale_order_id = fields.Many2one('sale.order', readonly=True,groups="base.group_user")
    city_id = fields.Many2one('res.city', 'City', related='sale_order_id.city_id', store=True,
                              track_visibility='onchange', )
    expected_delivery_date = fields.Date(track_visibility='onchange')
    payment_validate_date = fields.Date(track_visibility='onchange')
    latest_payment_date = fields.Date(readonly=1,track_visibility='onchange')
    bom_line_ids = fields.One2many('mrp.request.line', 'request_id', readonly=True)
    paint_ids = fields.One2many('mrp.paint.request', 'request_id', track_visibility='onchange', )
    carpenter_ids = fields.One2many('mrp.carpenter.request', 'request_id', track_visibility='onchange', )
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
    note = fields.Text(track_visibility='onchange', readonly=True)
    mrp_routs_ids = fields.Many2many('mrp.checklist.line', domain="[('product_id','=',product_id)]")
    current_operation = fields.Many2one('rout.name', track_visibility='onchange')
    called_or_not = fields.Boolean(track_visibility='onchange')
    is_late = fields.Boolean(compute="is_late_to_confirm",store=True)

    @api.depends('payment_validate_date','latest_payment_date')
    def is_late_to_confirm(self):
        for rec in self:
            if rec.payment_validate_date and rec.latest_payment_date:
                print((rec.payment_validate_date - rec.latest_payment_date))
                if (rec.payment_validate_date - rec.latest_payment_date).days <= -4:
                    rec.is_late = True

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

    def get_latest_payment_date(self):
        all_payments = self.env['account.payment'].search(
            [('partner_id', '=', self.sale_order_id.partner_id.id), ('payment_type', '=', 'inbound')],
            order="name DESC ,payment_date DESC",limit=1)
        if all_payments:
            self.latest_payment_date = all_payments.payment_date
        for line in all_payments:
            print(line.name,line.payment_date)

    # @api.model
    def get_request_attachments(self):
        print("=========-------------==========")
        attachments = self.env['ir.attachment'].search(
            [('res_model', '=', 'sale.order'), ('res_id', '=', self.sale_order_id.id)])
        print("attachement", attachments)
        if attachments:
            for attachment in attachments:
                values = {
                    'name': attachment.name,
                    'datas': attachment.datas,
                    'datas_fname': attachment.datas_fname,
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

class ManufacturingMaterials(models.Model):
    _name = 'mrp.production.material'
    _rec_name = 'product_id'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char("Code", readonly=True, copy=False, default='New', track_visibility='onchange')
    product_id = fields.Many2one('product.product', readonly=True
                                 , required=True)
    operation_id = fields.Many2one('mrp.routing.workcenter')
    quantity = fields.Float()
    bom_id = fields.Many2one('mrp.bom')