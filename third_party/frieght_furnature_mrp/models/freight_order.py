from werkzeug import urls
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    freight_id = fields.Many2one('freight.order')


class FreightOrder(models.Model):
    _name = 'freight.order'
    _description = 'Freight Order'

    name = fields.Char('Name', default='New', readonly=True)
    shipper_id = fields.Many2one('res.partner', 'Shipper', required=True,
                                 help="Shipper's Details")
    consignee_id = fields.Many2one('res.partner', 'Consignee',
                                   help="Details of consignee")
    type = fields.Selection([('import', 'Import'), ('export', 'Export')],
                            'Import/Export', required=True,
                            help="Type of freight operation")
    transport_type = fields.Selection([('land', 'Land'), ('air', 'Air'),
                                       ('water', 'Water')], "Transport", default='water',
                                      help='Type of transportation',
                                      required=True)
    land_type = fields.Selection([('ltl', 'LTL'), ('ftl', 'FTL')],
                                 'Land Shipping',
                                 help="Types of shipment movement involved in Land")
    water_type = fields.Selection([('fcl', 'FCL'), ('lcl', 'LCL')],
                                  'Water Shipping',
                                  help="Types of shipment movement involved in Water")
    order_date = fields.Date('Date', default=fields.Date.today(),
                             help="Date of order")
    loading_port_id = fields.Many2one('freight.port', string="Loading Port",
                                      required=True,
                                      help="Loading port of the freight order")
    discharging_port_id = fields.Many2one('freight.port',
                                          string="Discharging Port",
                                          required=True,
                                          help="Discharging port of freight order")
    state = fields.Selection([('draft', 'On Port'), ('submit', 'Departure'),
                              ('confirm', 'Arrived'),
                              ('invoice', 'Invoiced'), ('done', 'Done'),
                              ('cancel', 'Cancel')], default='draft')
    clearance = fields.Boolean("Clearance")
    clearance_count = fields.Integer(compute='compute_count')
    invoice_count = fields.Integer(compute='compute_count')
    bill_count = fields.Integer(compute='compute_bill_count')
    total_order_price = fields.Float('Total',
                                     compute='_compute_total_order_price')
    total_volume = fields.Float('Total Volume',
                                compute='_compute_total_order_price')
    total_weight = fields.Float('Total Weight',
                                compute='_compute_total_order_price')
    order_ids = fields.One2many('freight.order.line', 'order_id')
    route_ids = fields.One2many('freight.order.routes.line', 'route_id')
    total_route_sale = fields.Float('Total Sale',
                                    compute="_compute_total_route_cost")
    service_ids = fields.One2many('freight.order.service', 'line_id')
    total_service_sale = fields.Float('Service Total Sale',
                                      compute="_compute_total_service_cost")
    agent_id = fields.Many2one('res.partner', 'Agent', required=True,
                               help="Details of agent")
    expected_date = fields.Date('Expected Date')
    track_ids = fields.One2many('freight.track', 'track_id')
    po_count = fields.Integer(compute='compute_purchase_count')

    @api.multi
    def compute_purchase_count(self):
        for rec in self:
            purchase_orders = self.env['purchase.order'].sudo().search([('freight_id', '=', self.id)])
            if purchase_orders:
                rec.po_count = len(purchase_orders)

    def get_purchase_order(self):
        """Get custom clearance"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Order',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('freight_id', '=', self.id)],
            'context': "{'create': False}"
        }

    @api.multi
    def action_view_bills(self):
        action = self.env.ref('account.action_vendor_bill_template')
        result = action.read()[0]
        create_bill = self.env.context.get('create_bill', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'type': 'in_invoice',
            'default_freight_id': self.id,
            # 'default_company_id': self.company_id.id,
            # 'company_id': self.company_id.id,
        }
        # choose the view_mode accordingly
        if len(self.invoice_ids) > 1 and not create_bill:
            result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
        else:
            res = self.env.ref('account.invoice_supplier_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            # Do not set an invoice_id if we want to create a new bill.
            if not create_bill:
                result['res_id'] = self.invoice_ids.id or False
        return result

    @api.depends('order_ids.total_price', 'order_ids.volume',
                 'order_ids.weight')
    def _compute_total_order_price(self):
        """Computing the price of the order"""
        for rec in self:
            rec.total_order_price = sum(rec.order_ids.mapped('total_price'))
            rec.total_volume = sum(rec.order_ids.mapped('volume'))
            rec.total_weight = sum(rec.order_ids.mapped('weight'))

    @api.depends('route_ids.sale')
    def _compute_total_route_cost(self):
        """Computing the total cost of route operation"""
        for rec in self:
            rec.total_route_sale = sum(rec.route_ids.mapped('sale'))

    @api.depends('service_ids.total_sale')
    def _compute_total_service_cost(self):
        """Computing the total cost of services"""
        for rec in self:
            rec.total_service_sale = sum(rec.service_ids.mapped('total_sale'))

    @api.model
    def create(self, vals):
        """Create Sequence"""
        sequence_code = 'freight.order.sequence'
        vals['name'] = self.env['ir.sequence'].next_by_code(sequence_code)
        return super(FreightOrder, self).create(vals)

    def create_custom_clearance(self):
        """Create custom clearance"""
        clearance = self.env['custom.clearance'].create({
            'name': 'CC - ' + self.name,
            'freight_id': self.id,
            'date': self.order_date,
            'loading_port_id': self.loading_port_id.id,
            'discharging_port_id': self.discharging_port_id.id,
            'agent_id': self.agent_id.id,
        })
        result = {
            'name': 'action.name',
            'type': 'ir.actions.act_window',
            'views': [[False, 'form']],
            'target': 'current',
            'res_id': clearance.id,
            'res_model': 'custom.clearance',
        }
        self.clearance = True
        return result

    def get_custom_clearance(self):
        """Get custom clearance"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Custom Clearance',
            'view_mode': 'tree,form',
            'res_model': 'custom.clearance',
            'domain': [('freight_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def track_order(self):
        """Track the order"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Received/Delivered',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'freight.order.track',
            'context': {
                'default_freight_id': self.id
            }
        }

    def create_invoice(self):
        """Create invoice"""
        lines = []
        if self.order_ids:
            for order in self.order_ids:
                value = (0, 0, {
                    'name': order.product_id.name,
                    'price_unit': order.price,
                    'quantity': order.volume + order.weight,
                })
                lines.append(value)

        if self.route_ids:
            for route in self.route_ids:
                value = (0, 0, {
                    'name': route.operation_id.name,
                    'price_unit': route.sale,
                })
                lines.append(value)

        if self.service_ids:
            for service in self.service_ids:
                value = (0, 0, {
                    'name': service.service_id.name,
                    'price_unit': service.sale,
                    'quantity': service.qty
                })
                lines.append(value)

        invoice_line = {
            'move_type': 'out_invoice',
            'partner_id': self.shipper_id.id,
            'invoice_user_id': self.env.user.id,
            'invoice_origin': self.name,
            'ref': self.name,
            'invoice_line_ids': lines,
        }
        inv = self.env['account.move'].create(invoice_line)
        result = {
            'name': 'action.name',
            'type': 'ir.actions.act_window',
            'views': [[False, 'form']],
            'target': 'current',
            'res_id': inv.id,
            'res_model': 'account.move',
        }
        self.state = 'invoice'
        return result

    def action_cancel(self):
        """Cancel the record"""
        if self.state == 'draft' and self.state == 'submit':
            self.state = 'cancel'
        else:
            raise ValidationError("You can't cancel this order")

    def get_invoice(self):
        """View the invoice"""
        self.ensure_one()
        view = self.env.ref('account.invoice_tree_with_onboarding')
        return {
            'name': _('Invoice'),
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            # 'views': [(view.id, 'form'), ],
            'domain': [('freight_id', '=', self.id), ('type', '=', 'out_invoice')],
            'type': 'ir.actions.act_window',
            'context': "{'create': False}",
            'views': [(self.env.ref('account.invoice_tree').id, 'tree'),
                      (self.env.ref('account.invoice_form').id, 'form')]
        }

    invoice_ids = fields.Many2many('account.invoice')

    def compute_bill_count(self):
        for rec in self:
            bills = self.env['account.invoice'].search([('freight_id', '=', self.id), ('type', '=', 'in_invoice')])
            if bills:
                rec.bill_count = len(bills)

    @api.depends('name')
    def compute_count(self):
        """Compute custom clearance and account move's count"""
        for rec in self:
            if rec.env['custom.clearance'].search([('freight_id', '=', rec.id)]):
                rec.clearance_count = rec.env['custom.clearance'].search_count(
                    [('freight_id', '=', rec.id)])
            else:
                rec.clearance_count = 0
            if rec.env['account.invoice'].search([('origin', '=', rec.name)]):
                rec.invoice_count = rec.env['account.invoice'].search_count(
                    [('origin', '=', rec.name)])
            else:
                rec.invoice_count = 0

    def action_submit(self):
        """Submitting order"""
        for rec in self:
            rec.state = 'submit'
            # base_url = self.env['ir.config_parameter'].sudo().get_param(
            #     'web.base.url')
            # Urls = urls.url_join(base_url, 'web#id=%(id)s&model=freight.order&view_type=form' % {'id': self.id})
            #
            # mail_content = _('Hi %s,<br>'
            #                  'The Freight Order %s is Submitted'
            #                  '<div style = "text-align: center; '
            #                  'margin-top: 16px;"><a href = "%s"'
            #                  'style = "padding: 5px 10px; font-size: 12px; '
            #                  'line-height: 18px; color: #FFFFFF; '
            #                  'border-color:#875A7B;text-decoration: none; '
            #                  'display: inline-block; margin-bottom: 0px; '
            #                  'font-weight: 400;text-align: center; '
            #                  'vertical-align: middle; cursor: pointer; '
            #                  'white-space: nowrap; background-image: none; '
            #                  'background-color: #875A7B; '
            #                  'border: 1px solid #875A7B; border-radius:3px;">'
            #                  'View %s</a></div>'
            #                  ) % (rec.agent_id.name, rec.name, Urls, rec.name)
            # email_to = self.env['res.partner'].search([
            #     ('id', 'in', (self.shipper_id.id, self.consignee_id.id,
            #                   self.agent_id.id))])
            # for mail in email_to:
            #     main_content = {
            #         'subject': _('Freight Order %s is Submitted') % self.name,
            #         'author_id': self.env.user.partner_id.id,
            #         'body_html': mail_content,
            #         'email_to': mail.email
            #     }
            #     mail_id = self.env['mail.mail'].create(main_content)
            #     mail_id.mail_message_id.body = mail_content
            #     mail_id.send()

    def action_confirm(self):
        """Confirm order"""
        for rec in self:
            clearance = self.env['custom.clearance'].search([
                ('freight_id', '=', self.id)])
            if clearance:
                if clearance.state == 'confirm':
                    rec.state = 'confirm'
                    # base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    # Urls = urls.url_join(base_url, 'web#id=%(id)s&model=freight.order&view_type=form' % {'id': self.id})
                    # mail_content = _('Hi %s,<br> '
                    #                  'The Freight Order %s is Confirmed '
                    #                  '<div style = "text-align: center; '
                    #                  'margin-top: 16px;"><a href = "%s"'
                    #                  'style = "padding: 5px 10px; '
                    #                  'font-size: 12px; line-height: 18px; '
                    #                  'color: #FFFFFF; border-color:#875A7B; '
                    #                  'text-decoration: none; '
                    #                  'display: inline-block; '
                    #                  'margin-bottom: 0px; font-weight: 400;'
                    #                  'text-align: center; '
                    #                  'vertical-align: middle; '
                    #                  'cursor: pointer; white-space: nowrap; '
                    #                  'background-image: none; '
                    #                  'background-color: #875A7B; '
                    #                  'border: 1px solid #875A7B; '
                    #                  'border-radius:3px;">'
                    #                  'View %s</a></div>'
                    #                  ) % (rec.agent_id.name, rec.name,
                    #                       Urls, rec.name)
                    # email_to = self.env['res.partner'].search([
                    #     ('id', 'in', (self.shipper_id.id,
                    #                   self.consignee_id.id, self.agent_id.id))])
                    # for mail in email_to:
                    #     main_content = {
                    #         'subject': _('Freight Order %s is Confirmed') % self.name,
                    #         'author_id': self.env.user.partner_id.id,
                    #         'body_html': mail_content,
                    #         'email_to': mail.email
                    #     }
                    #     mail_id = self.env['mail.mail'].create(main_content)
                    #     mail_id.mail_message_id.body = mail_content
                    #     mail_id.send()
                elif clearance.state == 'draft':
                    raise ValidationError("the custom clearance ' %s ' is "
                                          "not confirmed" % clearance.name)
            else:
                raise ValidationError("Create a custom clearance for %s" % rec.name)

            for line in rec.order_ids:
                line.container_id.state = 'reserve'

    def action_done(self):
        """Mark order as done"""
        for rec in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            Urls = urls.url_join(base_url, 'web#id=%(id)s&model=freight.order&view_type=form' % {'id': self.id})

            mail_content = _('Hi %s,<br>'
                             'The Freight Order %s is Completed'
                             '<div style = "text-align: center; '
                             'margin-top: 16px;"><a href = "%s"'
                             'style = "padding: 5px 10px; font-size: 12px; '
                             'line-height: 18px; color: #FFFFFF; '
                             'border-color:#875A7B;text-decoration: none; '
                             'display: inline-block; '
                             'margin-bottom: 0px; font-weight: 400;'
                             'text-align: center; vertical-align: middle; '
                             'cursor: pointer; white-space: nowrap; '
                             'background-image: none; '
                             'background-color: #875A7B; '
                             'border: 1px solid #875A7B; border-radius:3px;">'
                             'View %s</a></div>'
                             ) % (rec.agent_id.name, rec.name, Urls, rec.name)
            email_to = self.env['res.partner'].search([
                ('id', 'in', (self.shipper_id.id, self.consignee_id.id,
                              self.agent_id.id))])
            for mail in email_to:
                main_content = {
                    'subject': _('Freight Order %s is completed') % self.name,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': mail_content,
                    'email_to': mail.email
                }
                mail_id = self.env['mail.mail'].create(main_content)
                mail_id.mail_message_id.body = mail_content
                mail_id.send()
            self.state = 'done'

            for line in rec.order_ids:
                line.container_id.state = 'available'


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    freight_id = fields.Many2one('freight.order')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    freight_id = fields.Many2one('freight.order')


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    freight_id = fields.Many2one('freight.order.line')


class FreightOrderLine(models.Model):
    _name = 'freight.order.line'

    order_id = fields.Many2one('freight.order')
    container_id = fields.Many2one('freight.container', string='Container', required=True,
                                   domain="[('state', '=', 'available')]")
    product_id = fields.Many2one('product.product', string='Goods')
    billing_type = fields.Selection([('weight', 'Weight'),
                                     ('volume', 'Volume')], default='volume', string="Billing On")
    pricing_id = fields.Many2one('freight.price', string='Pricing', required=True)
    price = fields.Float('Unit Price', required=True, )
    total_price = fields.Float('Total Price', required=True, )
    volume = fields.Float('Volume', required=True, )
    weight = fields.Float('Weight', )
    actual_volume = fields.Float(compute='compute_actual_total_volume', store=True)
    items_count = fields.Float(compute='compute_actual_total_volume', store=True)
    container_line_ids = fields.One2many('freight.container.line', 'container_order_id')
    po_line_id = fields.Many2one('purchase.order.line')
    purchase_id = fields.Many2one('purchase.order')
    invoice_id = fields.Many2one('account.invoice')
    custom_or_stock = fields.Selection([('custom', 'Customize'), ('stock', 'For Stock')], default='stock',
                                       required=True)

    def create_invoice_from_freight_line(self):
        current_company = self.env.user.company_id
        companies = self.env['res.company'].sudo().search([('id', '!=', current_company.id)], limit=1)
        created_invoice = self.env['account.invoice'].create({
            'partner_id': companies.partner_id.id,
            'company_id': current_company.id,
            'date_invoice': fields.Date.today(),
            'freight_id': self.order_id.id,
            'origin': self.order_id.name,
            'type': 'out_invoice',
            # 'partner_ref': self.container_id.name,
        })
        print('created_invoice', created_invoice)
        self.invoice_id = created_invoice.id
        order_list = []
        for line in self.container_line_ids.filtered(lambda l: l.custom_or_stock == 'custom'):
            if line.product_id.property_account_income_id.id:
                income_account = line.product_id.property_account_income_id.id
            elif line.product_id.categ_id.property_account_income_categ_id.id:
                income_account = line.product_id.categ_id.property_account_income_categ_id.id
            order_line = {
                'product_id': line.product_id.id,
                # 'freight_id': line.id,
                'account_id': income_account,
                'name': line.product_id.name,
                'quantity': line.quantity,
                'company_id': companies.id,
                'invoice_id': created_invoice.id,
                'uom_id': line.product_id.uom_po_id.id,
                'price_unit': line.product_id.usa_price,
            }
            order_list.append(order_line)
            print(order_line)
            invoice_line = self.env['account.invoice.line'].sudo().create(order_line)
        # created_invoice = self.env['account.invoice'].create({
        #     'partner_id': companies.partner_id.id,
        #     'company_id': current_company.id,
        #     'date_invoice': fields.Date.today(),
        #     'freight_id': self.order_id.id,
        #     'origin': self.order_id.name,
        #     'invoice_line_ids': [(0, 0, vals) for vals in order_list],
        # })
        # print('created_invoice', created_invoice)
        # print('created_invoice', created_invoice)
        # self.invoice_id = created_invoice.id

    def create_purchase_order_from_invoice(self):
        current_company = self.env.user.company_id
        companies = self.env['res.company'].sudo().search([('id', '!=', current_company.id)], limit=1)
        print(companies.name)
        warhouse_id = self.env['stock.warehouse'].sudo().search([('company_id', '=', companies.id)], limit=1)
        print(warhouse_id)
        print(warhouse_id.name)
        if not warhouse_id:
            raise ValidationError('no warehouse')
        picking_type_id = self.env['stock.picking.type'].sudo().search(
            [('warehouse_id', '=', warhouse_id.id), ('code', '=', 'incoming')])
        print(picking_type_id)
        if not picking_type_id:
            raise ValidationError('not picking')
        created_purchase = self.env['purchase.order'].sudo().create({
            'partner_id': current_company.partner_id.id,
            'company_id': companies.id,
            'order_date': fields.Date.today(),
            'picking_type_id': picking_type_id.id,
            'freight_id': self.order_id.id,
            'origin': self.order_id.name,
            'partner_ref': self.container_id.name,
        })
        self.purchase_id = created_purchase.id
        for line in self.container_line_ids:
            order_line = {
                'product_id': line.product_id.id,
                # 'freight_id': line.id,
                'name': line.product_id.name,
                'product_qty': line.quantity,
                'company_id': companies.id,
                'order_id': created_purchase.id,
                'date_planned': fields.Date.today(),
                'product_uom': line.product_id.uom_po_id.id,
                'price_unit': line.product_id.usa_cost,
            }
            purchase_order_line = self.env['purchase.order.line'].sudo().create(order_line)

    @api.depends('container_line_ids.total_volume', 'container_line_ids.quantity')
    def compute_actual_total_volume(self):
        for record in self:
            totalvol = 0
            items_count = 0
            for line in record.container_line_ids:
                totalvol += line.total_volume
                items_count += line.quantity
            record.actual_volume = totalvol
            record.items_count = items_count

    @api.constrains('weight')
    def _check_weight(self):
        """Checking the weight of containers"""
        for rec in self:
            if rec.container_id and rec.billing_type:
                if rec.billing_type == 'weight':
                    if rec.container_id.weight < rec.weight:
                        raise ValidationError(
                            'The weight is must be less '
                            'than or equal to %s' % (rec.container_id.weight))

    @api.onchange('container_id')
    def get_new_containter_volume(self):
        if self.container_id and self.container_id.volume:
            self.volume = self.container_id.volume

    @api.constrains('volume')
    def _check_volume(self):
        """Checking the volume of containers"""
        for rec in self:
            if rec.container_id and rec.billing_type:
                if rec.billing_type == 'volume':
                    if rec.container_id.volume < rec.volume:
                        raise ValidationError(
                            'The volume is must be less '
                            'than or equal to %s' % (rec.container_id.volume))

    @api.onchange('pricing_id', 'billing_type')
    def onchange_price(self):
        """Calculate the weight and volume of container"""
        for rec in self:
            if rec.billing_type == 'weight':
                rec.volume = 0.00
                rec.price = rec.pricing_id.weight
            elif rec.billing_type == 'volume':
                rec.weight = 0.00
                rec.price = rec.pricing_id.volume

    @api.onchange('pricing_id', 'billing_type', 'volume', 'weight')
    def onchange_total_price(self):
        """Calculate sub total price"""
        for rec in self:
            if rec.billing_type and rec.pricing_id:
                if rec.billing_type == 'weight':
                    rec.total_price = rec.weight * rec.price
                elif rec.billing_type == 'volume':
                    rec.total_price = rec.volume * rec.price


class FreightContainerLine(models.Model):
    _name = 'freight.container.line'

    order_id = fields.Many2one('freight.order', related='container_order_id.order_id')
    container_order_id = fields.Many2one('freight.order.line')
    container_id = fields.Many2one('freight.container', string='Container', required=True,
                                   domain="[('state', '=', 'available')]")
    product_id = fields.Many2one('product.product', required=True, domain="([('sale_ok','=',True)])")
    quantity = fields.Float(required=True)
    product_volume = fields.Float(compute="get_product_volume_uint_total")
    total_volume = fields.Float(compute="get_product_volume_uint_total", store=True)
    stock_move_id = fields.Many2one('stock.move')
    custom_or_stock = fields.Selection([('custom', 'Customize'), ('stock', 'For Stock')], default='stock')

    @api.depends('product_id', 'quantity')
    def get_product_volume_uint_total(self):
        for rec in self:
            rec.product_volume = rec.product_id.volume
            rec.total_volume = rec.product_id.volume * rec.quantity if rec.quantity and rec.product_id.volume else rec.product_id.volume


class FreightOrderRouteLine(models.Model):
    _name = 'freight.order.routes.line'

    route_id = fields.Many2one('freight.order')
    operation_id = fields.Many2one('freight.routes', required=True)
    source_loc = fields.Many2one('freight.port', 'Source Location')
    destination_loc = fields.Many2one('freight.port', 'Destination Location')
    transport_type = fields.Selection([('land', 'Land'), ('air', 'Air'),
                                       ('water', 'Water')], "Transport",
                                      required=True)
    sale = fields.Float('Sale')

    @api.onchange('operation_id', 'transport_type')
    def _onchange_operation_id(self):
        """calculate the price of route operation"""
        for rec in self:
            if rec.operation_id and rec.transport_type:
                if rec.transport_type == 'land':
                    rec.sale = rec.operation_id.land_sale
                elif rec.transport_type == 'air':
                    rec.sale = rec.operation_id.air_sale
                elif rec.transport_type == 'water':
                    rec.sale = rec.operation_id.water_sale


class FreightOrderServiceLine(models.Model):
    _name = 'freight.order.service'

    line_id = fields.Many2one('freight.order')
    clearance_id = fields.Many2one('custom.clearance')
    service_id = fields.Many2one('freight.service', required=False)
    product_id = fields.Many2one('product.product', string="Service",
                                 domain="[('type','=','service'),('can_be_expensed','=',True)]", required=True)
    partner_id = fields.Many2one('res.partner', domain="[('supplier','=','True')]", string="Vendor")
    qty = fields.Float('Quantity')
    cost = fields.Float('Cost')
    sale = fields.Float('Sale')
    total_sale = fields.Float('Total Cost')

    @api.onchange('product_id', 'partner_id')
    def _onchange_partner_id(self):
        """Calculate the price of services"""
        for rec in self:
            if rec.product_id:
                rec.cost = rec.product_id.lst_price
                if rec.partner_id:
                    if rec.service_id.line_ids:
                        for service in rec.service_id.line_ids:
                            if rec.partner_id == service.partner_id:
                                rec.sale = service.sale
                            else:
                                rec.sale = rec.service_id.sale_price
                    # else:
                # else:
                #     rec.sale = rec.service_id.sale_price

    @api.onchange('qty', 'sale')
    def _onchange_qty(self):
        """Calculate the subtotal of route operation"""
        for rec in self:
            rec.total_sale = rec.qty * rec.cost


class Tracking(models.Model):
    _name = 'freight.track'

    source_loc = fields.Many2one('freight.port', 'Source Location')
    destination_loc = fields.Many2one('freight.port', 'Destination Location')
    transport_type = fields.Selection([('land', 'Land'), ('air', 'Air'),
                                       ('water', 'Water')], "Transport")
    track_id = fields.Many2one('freight.order')
    date = fields.Date('Date')
    type = fields.Selection([('received', 'Received'),
                             ('delivered', 'Delivered')], 'Received/Delivered')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    export = fields.Boolean('For Export', default=False)
    freight_send = fields.Boolean()
    def create_freight_order(self):
        for rec in self.order_line:
            open_freight = self.env['freight.order'].search([('state','=','draft')],limit=1)
            if not open_freight:
                raise ValidationError('please create open freight')
            elif len(open_freight)>1:
                raise ValidationError('please add only one open freight')
            print(open_freight)
            freight_line = open_freight.order_ids.filtered(lambda  l: not l.purchase_id)
            if not freight_line:
                raise ValidationError('Please add Line in freight for customize')
            print(freight_line)
            order_line = {
                'product_id': rec.product_id.id,
                'container_id': freight_line.container_id.id,
                'custom_or_stock':'stock',
                'quantity': rec.product_uom_qty,
            }
            freight_line.container_line_ids =[(0,0,order_line)]
        self.freight_send = True