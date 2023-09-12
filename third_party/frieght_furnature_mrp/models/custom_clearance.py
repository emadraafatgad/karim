###################################################################################
###################################################################################
from werkzeug import urls
from odoo import api, fields, models, _


class CustomClearance(models.Model):
    _name = 'custom.clearance'
    _description = 'Custom Clearance'

    name = fields.Char('Name', compute='_compute_name')
    freight_id = fields.Many2one('freight.order', required=True)
    date = fields.Date('Date')
    agent_id = fields.Many2one('res.partner', 'Agent', required=True)
    loading_port_id = fields.Many2one('freight.port', string="Loading Port")
    discharging_port_id = fields.Many2one('freight.port',
                                          string="Discharging Port")
    line_ids = fields.One2many('custom.clearance.line', 'line_id')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),
                              ('done', 'Done')], default='draft')
    total_service_sale = fields.Float('Service Total Sale',
                                      compute="_compute_total_service_cost")

    service_ids = fields.One2many('freight.order.service', 'clearance_id')

    @api.depends('service_ids.total_sale')
    def _compute_total_service_cost(self):
        """Computing the total cost of services"""
        for rec in self:
            rec.total_service_sale = sum(rec.service_ids.mapped('total_sale'))

    @api.depends('freight_id')
    def _compute_name(self):
        """Compute the name of custom clearance"""
        for rec in self:
            if rec.freight_id:
                rec.name = 'CC - ' + str(rec.freight_id.name)
            else:
                rec.name = 'CC - '

    @api.onchange('freight_id')
    def _onchange_freight_id(self):
        """Getting default values for loading and discharging port"""
        for rec in self:
            rec.date = rec.freight_id.order_date
            rec.loading_port_id = rec.freight_id.loading_port_id
            rec.discharging_port_id = rec.freight_id.discharging_port_id
            rec.agent_id = rec.freight_id.agent_id

    def create_bills(self):
        print("""Create invoice""")
        if self.service_ids:
            vendors = self.service_ids.mapped('partner_id')
            print('vendors')
            print(vendors)
            for vendor in vendors:
                service_ids = self.service_ids.filtered(lambda s: s.partner_id == vendor)
                print('service_ids', service_ids)
                lines = []
                for service in service_ids:
                    if service.product_id.property_account_income_id.id:
                        expense_account = service.product_id.property_account_expense_id.id
                    elif service.product_id.categ_id.property_account_income_categ_id.id:
                        expense_account = service.product_id.categ_id.property_account_expense_categ_id.id
                    value = (0, 0, {
                        'name': service.product_id.name,
                        'product_id': service.product_id.id,
                        'account_id': expense_account,
                        'price_unit': service.cost,
                        'quantity': service.qty
                    })
                    lines.append(value)
                invoice_line = {
                    'type': 'in_invoice',
                    'partner_id': vendor.id,
                    'date_invoice': fields.Date.today(),
                    # 'freight_id': self.order_id.id,
                    'origin': self.name,
                    'invoice_line_ids': lines,
                }
                inv = self.env['account.invoice'].create(invoice_line)
            # result = {
            #     'name': 'action.name',
            #     'type': 'ir.actions.act_window',
            #     'views': [[False, 'tree']],
            #     'target': 'current',
            #     'res_id': inv.id,
            #     'res_model': 'account.invoice',
            # }
            # self.state = 'invoice'

    def action_confirm(self):
        """Send mail to inform agents to custom clearance is confirmed"""
        for rec in self:
            rec.name = 'CC' \
                       ' - ' + rec.freight_id.name
            rec.state = 'confirm'
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            Urls = urls.url_join(base_url, 'web#id=%(id)s&model=custom.clearance&view_type=form' % {'id': self.id})
            Urls_ = urls.url_join(base_url,
                                  'web#id=%(id)s&model=freight.order&view_type=form' % {'id': self.freight_id.id})

            mail_content = _('Hi %s,<br>'
                             'The Custom Clearance %s is confirmed'
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
                             ) % (rec.agent_id.name, rec.name, Urls,
                                  rec.name, Urls_, self.freight_id.name)
            main_content = {
                'subject': _('Custom Clerance For %s') % self.freight_id.name,
                'author_id': self.env.user.partner_id.id,
                'body_html': mail_content,
                'email_to': rec.agent_id.email,
            }
            mail_id = self.env['mail.mail'].create(main_content)
            mail_id.mail_message_id.body = mail_content
            mail_id.send()

    def action_revision(self):
        """Creating custom revision"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Received/Delivered',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'custom.clearance.revision.wizard',
            'context': {
                'default_custom_id': self.id
            }
        }

    def get_revision(self):
        """Getting details of custom revision"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Custom Revision',
            'view_mode': 'tree,form',
            'res_model': 'custom.clearance.revision',
            'domain': [('clearance_id', '=', self.id)],
            'context': "{'create': False}"
        }


class CustomClearanceLine(models.Model):
    _name = 'custom.clearance.line'
    _description = 'Custom Clearance Line'

    name = fields.Char('Document Name')
    document = fields.Binary(string="Documents", store=True, attachment=True)
    line_id = fields.Many2one('custom.clearance')


class CustomClearanceRevision(models.Model):
    _name = 'custom.clearance.revision'
    _description = 'Custom Clearance Revision'

    name = fields.Char('Name')

    name = fields.Char()
    reason = fields.Text()
    clearance_id = fields.Many2one('custom.clearance')
