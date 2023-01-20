from datetime import datetime

from odoo import exceptions
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    multi_line = fields.Boolean()


class ComponentName(models.Model):
    _name = "component.name"

    name = fields.Char()
    is_count = fields.Boolean()
    category_id = fields.Many2one('product.category', required=True)
    default_qty = fields.Float()
    s_product_id = fields.Many2one('product.product', string="Second Material")
    s_product_qty = fields.Float()
    f_product_id = fields.Many2one('product.product', string="Third Material")
    f_product_qty = fields.Float(string="Third Qty")
    operation_id = fields.Many2one('mrp.routing.workcenter', string='Operation To Consume')  # TDE FIXME: naming
    active = fields.Boolean(default=True)


class MrpPaintRequest(models.Model):
    _inherit = 'mrp.paint.request'
    component_line_id = fields.Many2one('sale.order.component.line')


class MrpPaintRequest(models.Model):
    _inherit = 'mrp.carpenter.request'
    component_line_id = fields.Many2one('sale.order.component.line')


class SalesOrderComponentLine(models.Model):
    _name = 'sale.order.component.line'

    product_id = fields.Many2one('product.product', required=True)
    packaging_id = fields.Many2one('mrp.packaging', domain="[('product_id','=',product_id)]")
    paint_ids = fields.One2many('mrp.paint.request', 'component_line_id')
    component_list_ids = fields.One2many('product.component.list', 'component_line_id')
    sale_order_id = fields.Many2one('sale.order')
    note = fields.Text()
    attachment = fields.Binary()
    sale_order_line_id = fields.Many2one('sale.order.line')
    mrp_send = fields.Boolean()
    mrp_package = fields.Boolean()
    product_qty = fields.Float()

    # mrp_product_qty = fields.Float(default=1,required=True)

    def add_list_of_records(self):
        sales_component = self.env['product.component.list']
        ids_list = []
        bom_id_base = self.env['mrp.bom'].search([('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
                                                  ('is_standard', '=', True)], )
        print(bom_id_base, )
        if len(bom_id_base) > 1:
            raise ValidationError("There is more than one standard bom for {}".format(self.product_id.display_name))

        for line in bom_id_base.product_component_list_ids:
            sales_component_id = sales_component.create({
                "component_id": line.component_id.id,
                "quantity": line.quantity,
                'internal_component': line.internal_component.id,
                'internal_quantity': line.internal_quantity,
                'operation_id': line.operation_id.id,
                "component_line_id": self.id, })
            sales_component_id.write({'internal_quantity': line.internal_quantity})

    def update_list_of_records(self):
        sales_component = self.env['product.component.list']
        ids_list = []
        bom_id_base = self.env['mrp.bom'].search([('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
                                                  ('is_standard', '=', True)], )
        print(bom_id_base, )
        for sales_component_id in self.component_list_ids:
            for line in bom_id_base.product_component_list_ids:
                print("==============================================================================")
                if sales_component_id.component_id.id == line.component_id.id:
                    print("Component Update")
                    sales_component_id.write({'internal_quantity': line.internal_quantity})
            print("*********************************************--------------------*****************")


class SalesOrderKomash(models.Model):
    _inherit = 'sale.order'

    product_component_ids = fields.One2many('sale.order.component.line', 'sale_order_id',
                                            copy=True, auto_join=True,
                                            states={'cancel': [('readonly', True)], 'done': [('readonly', True)]})
    mrp_send = fields.Selection([('Ready', 'Ready'), ('Sent', 'Sent')], track_visibility='onchange')
    po_send = fields.Selection([('Ready', 'Ready'), ('Sent', 'Sent')], default="Ready", track_visibility='onchange', )
    mrp_date = fields.Date(string="Delivery  Date", required=True, track_visibility='onchange', )
    to_date = fields.Date(string="TO  Date", required=True, track_visibility='onchange', )
    city_id = fields.Many2one('res.city', 'City', track_visibility='onchange', )
    phone = fields.Char(related='partner_id.phone', required=True, readonly=False, track_visibility='onchange', )

    # @api.multi
    # def action_cancel(self):
    #     now = fields.Datetime.now()
    #     for order in self:
    #
    #     return super(SalesOrderKomash, self).action_cancel()
    #
    @api.multi
    def action_unlock(self):
        mrp_req = self.env['mrp.production.request'].sudo().search(
            [('sale_order_id', '=', self.id), ('state', '!=', 'not')])
        if mrp_req:
            raise ValidationError('This order has Mrp Request Sent , please ask your manager to delete it first')
        order_invoices = self.env['account.invoice'].sudo().search([('origin', '=', self.name)])
        for inv in order_invoices:
            if inv.state in ['open', 'paid']:
                raise ValidationError(
                    'This order has Open or Paid Invoices , please ask your manager to delete drafts or cancel it')
            if inv.state == 'draft':
                raise ValidationError(
                    'This order has Draft Invoices , please ask your manager to delete drafts or cancel it')
        self.mrp_send = 'Ready'
        for variant in self.product_component_ids:
            variant.mrp_send = False
            variant.mrp_package = False
        self.write({'state': 'sale'})

    delivery_status = fields.Selection([('New', 'New'), ('Partial', 'Partial'), ('Done', 'Done')],
                                       compute='compute_delivered_qty', store=True)

    @api.depends('order_line.product_uom_qty', 'order_line.qty_delivered')
    def compute_delivered_qty(self):
        for record in self:
            qty_sum = sum(line.product_uom_qty for line in record.order_line)
            del_sum = sum(line.qty_delivered for line in record.order_line)
            if del_sum == 0:
                record['delivery_status'] = "New"
            elif qty_sum > del_sum:
                record['delivery_status'] = "Partial"
            else:
                record['delivery_status'] = "Done"

    def update_attachment_mrp(self):
        mrp_orders = self.env['mrp.production.request'].search([('sale_order_id', '=', self.id)])
        print(mrp_orders, "mrp_design")
        if mrp_orders:
            for mrp in mrp_orders:
                mrp.get_request_attachments()

    def po_send_button(self):
        counter = 0
        for line in self.order_line:
            if line.product_id and line.product_id.type == 'product':
                counter = counter + 1
                if line.product_id.bom_count == 0:
                    self.ensure_one()
                    if self.state in ['sale', 'done']:
                        lines = []
                        customer_add = False
                        request_line = self.env['bom.purchase.request.line'].search(
                            [('product_id', '=', line.product_id.id), ('name', '=', line.name),
                             ('state', 'in', ['draft', 'to_approve'])])
                        if request_line and not line.product_id.categ_id.multi_line:
                            print(request_line)
                            for req in request_line:
                                print(req.request_id.approver_id.name)
                                print(req.name)
                                if req.request_id.approver_id.id == self.env.user.id:
                                    request_line = req
                                    continue
                            qty = request_line.product_qty
                            needed_qty = line.product_uom_qty
                            totol = qty + needed_qty
                            print(totol, "total")
                            print(line.name)
                            print(line.product_id.display_name)
                            if line.product_id.display_name == line.name:
                                request_line.product_qty = totol
                                print(request_line.request_id, "bool")
                            else:
                                request = self.env['bom.purchase.request']
                                request_id = self.env['bom.purchase.request'].search(
                                    [('approver_id', '=', self.env.user.id),
                                     ('sale_order', '=', True),
                                     ('state', 'in', ['draft', 'to_approve'])])
                                if request_id:
                                    request = request_id
                                    if not customer_add:
                                        request_id.materials_for = request_id.materials_for + self.partner_id.name + ' , '
                                    customer_add = True
                                else:
                                    request_id = self.env['bom.purchase.request'].create(
                                        {'approver_id': self.env.user.id,
                                         'sale_order': True,
                                         'user_id': self.env.user.id,
                                         'materials_for': self.partner_id.name + ' , '
                                         })
                                    customer_add = True
                                    request = request_id
                                request_line_id = self.env['bom.purchase.request.line'].create(
                                    {
                                        'product_id': line.product_id.id,
                                        'name': line.name,
                                        'product_qty': line.product_uom_qty,
                                        'product_uom_id': line.product_uom.id,
                                        'request_date': datetime.today(),
                                        'request_id': request.id
                                    })
                            if not customer_add:
                                request_line.request_id.materials_for = request_line.request_id.materials_for + self.partner_id.name + ' , '
                                customer_add = True
                        else:
                            request = self.env['bom.purchase.request']
                            request_id = self.env['bom.purchase.request'].search(
                                [('approver_id', '=', self.env.user.id),
                                 ('sale_order', '=', True),
                                 ('state', 'in', ['draft', 'to_approve'])])
                            if request_id:
                                request = request_id
                                if not customer_add:
                                    request_id.materials_for = request_id.materials_for + self.partner_id.name + ' , '
                                customer_add = True
                            else:
                                request_id = self.env['bom.purchase.request'].create({'approver_id': self.env.user.id,
                                                                                      'sale_order': True,
                                                                                      'user_id': self.env.user.id,
                                                                                      'materials_for': self.partner_id.name + ' , '
                                                                                      })
                                customer_add = True
                                request = request_id
                            request_line_id = self.env['bom.purchase.request.line'].create(
                                {
                                    'product_id': line.product_id.id,
                                    'name': line.name,
                                    'product_qty': line.product_uom_qty,
                                    'product_uom_id': line.product_uom.id,
                                    'request_date': datetime.today(),
                                    'request_id': request.id
                                })
                        non_mrp_request = {
                            'product_id': line.product_id.id,
                            # 'name': line.name,
                            'quantity_qty': line.product_uom_qty,
                            'product_uom_id': line.product_uom.id,
                            'delivery_date': self.mrp_date,
                            'origin': self.partner_id.name,
                            'sale_order_id': self.id,
                            'note': line.name,
                            'state': 'not',
                        }
                        mrp_request = self.env['mrp.production.request'].create(non_mrp_request)
            else:
                continue
        self.po_send = 'Sent'

    def product_component_form(self):
        component_line_obj = self.env['sale.order.component.line']
        # self.product_component_ids = [(5, 0, 0)]
        for rec in self.order_line:
            product_flag = 0
            for line in self.product_component_ids:
                print(line.sale_order_line_id, " or ", rec.id)
                if line.product_id == rec.product_id:
                    if line.sale_order_line_id.id == rec.id:
                        # print(line.product_id.name, "==", rec.id)
                        product_flag = 1
                        break
                    elif not line.sale_order_line_id.id:
                        # print(line.product_id.name, "not found", rec.id)
                        line.sale_order_line_id = rec.id
                        product_flag = 1
                        break
                    elif line.sale_order_line_id.id != rec.id:
                        product_flag = 0
                        # print(line.product_id.name, "!=", rec.id)
                        break

            if not product_flag:
                bom_id_base = self.env['mrp.bom'].search([('product_tmpl_id', '=', rec.product_id.product_tmpl_id.id),
                                                          ('is_standard', '=', True)], )
                if bom_id_base:
                    component_line_id = component_line_obj.create({
                        'sale_order_id': self.id,
                        'sale_order_line_id': rec.id,
                        'product_qty': rec.product_uom_qty,
                        'product_id': rec.product_id.id,
                    })
                    component_line_id.add_list_of_records()
                    # print(component_line_id.product_id.name)
            self.mrp_send = 'Ready'

    def product_component_form2(self):
        self.ensure_one()
        view = self.env.ref('manufacturing_furnature.product_component_line_form')
        print(view, "10000000")
        ctx = dict()
        ctx.update({
            # 'default_order_from': self.partner_id.id,
            'default_sale_order_id': self.id,

        })
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'sale.order.component.line',
            'target': 'current',
            'type': 'ir.actions.act_window',
            'context': ctx,
        }

    def return_bill_material(self, final_product):
        vals = []
        for line in self.product_component_ids:
            if line.product_id == final_product and line.mrp_send == False:
                for l in line.component_list_ids:
                    vals.append({
                        'component_id': l.component_id.id,
                        'internal_component': l.internal_component.id,
                        'quantity': l.quantity,
                        'product_uom_id': l.internal_component.uom_id.id,
                        'internal_quantity': l.internal_quantity,
                        'operation_id': l.operation_id.id,
                    })

                break
            print(vals, "===============================", vals)
        return vals

    def return_bill_material_bom(self, final_product):
        vals = []
        for line in self.product_component_ids:
            if line.product_id == final_product and line.mrp_send == False:
                for l in line.component_list_ids:
                    if l.internal_component.id:
                        vals.append({'product_id': l.internal_component.id,
                                     'product_uom_id': l.internal_component.uom_id.id,
                                     'product_qty': l.internal_quantity * l.quantity,
                                     'operation_id': l.operation_id.id,
                                     })
                    if l.component_id.s_product_id:
                        vals.append({'product_id': l.component_id.s_product_id.id,
                                     'product_uom_id': l.component_id.s_product_id.uom_id.id,
                                     'product_qty': l.component_id.s_product_qty * l.quantity,
                                     'operation_id': l.operation_id.id,
                                     })
                    if l.component_id.f_product_id:
                        vals.append({'product_id': l.component_id.f_product_id.id,
                                     'product_uom_id': l.component_id.f_product_id.uom_id.id,
                                     'product_qty': l.component_id.f_product_qty * l.quantity,
                                     'operation_id': l.operation_id.id,
                                     })
                line.mrp_send = True
                break
        return vals

    def return_bill_material_packaging(self, final_product):
        vals = []
        for line in self.product_component_ids:
            if line.product_id == final_product and line.mrp_package == False:
                for l in line.packaging_id.packaging_line_ids:
                    if l.id:
                        vals.append({'product_id': l.product_id.id,
                                     'product_uom_id': l.uom_id.id,
                                     'product_qty': l.qty,

                                     'operation_id': line.packaging_id.operation_id.id,
                                     })
                        print(vals, "packaging")
                line.mrp_package = True
                break
        return vals

    def return_bom_id_base(self, line):
        bom_id_base = self.env['mrp.bom'].search([('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                                                  ('is_standard', '=', True)], )
        print(bom_id_base, "base standard")
        if bom_id_base:
            bom_id = self.env['mrp.bom'].create({
                'product_tmpl_id': bom_id_base.product_tmpl_id.id,
                'product_id': bom_id_base.product_id.id,
                'code': self.partner_id.name,
                'product_uom_id': line.product_id.uom_id.id,
                'routing_id': bom_id_base.routing_id.id,
                'product_qty': bom_id_base.product_qty,
                'company_id': self.company_id.id,
            })
            print(bom_id, "new bom")
            for dic in self.return_bill_material(line.product_id):
                bom_id.write({'product_component_list_ids': [(0, 0, dic)]})
                print("dic base", dic)
            bom_id.write({'bom_line_ids': [(6, 0, self.return_base_bom_lines(bom_id, line))]})
            for dic in self.return_bill_material_bom(line.product_id):
                bom_id.write({'bom_line_ids': [(0, 0, dic)]})
                print("done Bom", dic)
            for dic in self.return_bill_material_packaging(line.product_id):
                bom_id.write({'bom_line_ids': [(0, 0, dic)]})
                print("Done packaging", dic)
        else:
            raise exceptions.ValidationError(_("Please set a standard Bill Material Of %s" % line.product_id.name))
        # print("booooom_id", bom_id)
        return bom_id

    def return_base_bom_lines(self, bom_id, line):
        bom_id_base = self.env['mrp.bom'].search([('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                                                  ('is_standard', '=', True)], )
        # print("------------>", bom_id_base.id)
        if bom_id_base:
            lst = []
            for bom in bom_id_base.bom_line_ids:
                lst.append(self.env['mrp.bom.line'].create({
                    'product_id': bom.product_id.id,
                    'product_uom_id': bom.product_uom_id.id,
                    'product_qty': bom.product_qty,
                    'operation_id': bom.operation_id.id,
                    # 'type': bom.type,
                    'bom_id': bom_id.id
                }).id)
            return lst

    def get_labour_cost(self, line):
        # for rec in self:
        bom_id_base = self.env['mrp.bom'].search([('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                                                  ('is_standard', '=', True)], )
        labour_cost_list = []
        for rec in bom_id_base.direct_labour_cost_ids:
            labour_cost_list.append({
                'operation_id': rec.operation_id.id,
                'unit_cost': rec.unit_cost,
            })
            # print(labour_cost_list)
        return labour_cost_list

    def add_labour_cost(self, line, mo_production_id):
        labor_cost_obj = self.env['direct.labour.cost']
        labour_cost_list = self.get_labour_cost(line)
        # print("labout cost", labour_cost_list)
        for list in labour_cost_list:
            list['mo_id'] = mo_production_id.id
            # print(list)
            labor_cost_obj.create(list)

    def line_check_zero_qty(self, line):
        for rec in line.component_list_ids:
            if rec.internal_quantity == 0:
                raise ValidationError("You have zero qty in component lines please check Components items ")
        return True

    def send_to_mrp(self):
        for line in self.product_component_ids:
            check = self.env['mrp.production.request'].search(
                [('sale_order_id', '=', self.id), ('product_id', '=', line.product_id.id)])
            check_zero = self.line_check_zero_qty(line)
            if len(line.paint_ids) == 0:
                raise ValidationError("You have to select colors")
            if check_zero != True:
                return check_zero
            bom_id = self.return_bom_id_base(line)
            product_uom_qty = 0
            for order_line in self.order_line:
                if order_line.product_id == line.product_id and order_line.id == line.sale_order_line_id.id:
                    product_uom_qty = order_line.product_uom_qty
            mo_production_id = self.env['mrp.production.request'].create({
                'product_id': line.product_id.id,
                'product_uom_id': line.product_id.uom_id.id,
                'origin': self.partner_id.name,
                'sale_order_id': self.id,
                'note': line.note,
                'quantity_qty': product_uom_qty,
                'bom_id': bom_id.id,
                'attachment': line.attachment,
                'delivery_date': self.mrp_date,
                'company_id': self.company_id.id,
            })
            # mo_production_id.write({'note':})
            for paint in line.paint_ids:
                paint.request_id = mo_production_id
            carpenter_from_labour = self.env['direct.labour.cost'].search(
                [('product_id', '=', line.product_id.id), ('operation_type', '=', 'carpainter')])
            if carpenter_from_labour:
                carpenter_plan = self.env['mrp.carpenter.request'].create({
                    'product_id': line.product_id.id,
                    "operation_id": carpenter_from_labour.operation_id.id,
                    "worker_id": carpenter_from_labour.worker_id.id,
                    'state': 'draft',
                    'request_id': mo_production_id.id,
                })
            mo_production_id.get_bom_line_ids()
            self.mrp_send = 'Sent'
            self.state = 'done'


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_lines_discount = fields.Float(compute="compute_discount_lines_amount", store=True)
    total_untaxed_amount = fields.Float(string="Before Discount",compute="compute_discount_lines_amount", store=True)
    @api.depends("order_line.discount_amount")
    def compute_discount_lines_amount(self):
        for rec in self:
            amount = 0
            total = 0
            for line in rec.order_line:
                amount += line.discount_amount
                total += line.product_uom_qty*line.price_unit
            rec.total_lines_discount = amount
            rec.total_untaxed_amount = total



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount_amount = fields.Float()

    @api.onchange('discount_amount')
    def get_discount_amount_percentage(self):
        if self.discount_amount:
            total = self.product_uom_qty * self.price_unit
            discount = self.discount_amount / total
            self.discount = discount * 100

    @api.onchange('discount')
    def get_discount_percentage_amount(self):
        if self.discount:
            disc = self.discount / 100
            total = self.product_uom_qty * self.price_unit * disc
            # discount = self.discount_amount / total
            self.discount_amount = total

    @api.multi
    def write(self, values):
        if 'product_uom_qty' in values or 'price_unit' in values:
            if len(self.invoice_lines) > 0:
                for line in self.invoice_lines:
                    if line.invoice_id.state not in ['draft', 'cancel']:
                        raise ValidationError("you can't update quantity or unit price of not cancel items invoices")
        return super(SaleOrderLine, self).write(values)

    @api.multi
    def unlink(self):
        if len(self.invoice_lines) > 0:
            for line in self.invoice_lines:
                if line.invoice_id.state not in ['draft', 'cancel']:
                    raise ValidationError("you can't delete line with invoiced items")
        return super(SaleOrderLine, self).unlink()
