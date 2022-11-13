from odoo import fields, models, api, exceptions, _


class ComponentName(models.Model):
    _name = "component.name"

    name = fields.Char()

class ProductComponent(models.Model):
    _name = 'product.component.list'

    # component_id = fields.Selection([('1', 'Component 1'),
    #                                  ('2', 'Component 2'),
    #                                  ('3', 'Component 3'),
    #                                  ('4', 'Component 4'),
    #                                  ('5', 'Component 5'),
    #                                  ('6', 'Component 6'),
    #                                  ('7', 'Component 7'),
    #                                  ])

    component_id  = fields.Many2one('component.name')
    quantity = fields.Integer()
    internal_quantity = fields.Float(help="Bill Of Material Quantity", string="Quantity")
    # external_quantity = fields.Float(help="Bill Of Material Quantity")
    internal_component = fields.Many2one('product.product', string="Component")
    # external_component = fields.Many2one('product.product')
    component_line_id = fields.Many2one('sale.order.component.line',)


class SalesOrderComponentLine(models.Model):
    _name = 'sale.order.component.line'

    product_id = fields.Many2one('product.product')
    component_list_ids = fields.One2many('product.component.list','component_line_id')
    sale_order_id = fields.Many2one('sale.order')
    sale_order_line_id = fields.Many2one('sale.order.line')
    quantity = fields.Float()

    def add_list_of_records(self):
        sales_component = self.env['product.component.list']
        ids_list = []
        bom_id_base = self.env['mrp.bom'].search([('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
                                                  ('is_standard', '=', True)], )
        print(bom_id_base,)
        for line in bom_id_base.product_component_list_ids:
            print(line)
            sales_component.create({
                "component_id":line.component_id.id,
                "quantity":1,
                'internal_component':line.internal_component.id,
                'internal_quantity':line.internal_quantity,
                "component_line_id":self.id,
            })


class SalesOrderKomash(models.Model):
    _inherit = 'sale.order'

    product_component_ids = fields.One2many('sale.order.component.line', 'sale_order_id',
                                            copy=True, auto_join=True,)

    mrp_date = fields.Date(string="Delivery  Date",required=True)

    def product_component_form(self):
        component_line_obj = self.env['sale.order.component.line']
        for rec in self.order_line:
            component_line_id = component_line_obj.create({
                'sale_order_id':self.id,
                'product_id':rec.product_id.id,
            })
            component_line_id.add_list_of_records()


    def product_component_form2(self):
        self.ensure_one()
        view = self.env.ref('manufacturing_furnature.product_component_line_form')
        print(view,"10000000")
        ctx = dict()
        ctx.update({
            # 'default_order_from': self.partner_id.id,
            'default_sale_order_id': self.id,

        })
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'view_id':view.id,
            'res_model': 'sale.order.component.line',
            'target':'current',
            'type': 'ir.actions.act_window',
            'context':ctx,

        }

    def return_bill_material(self,final_product):
        vals = []
        for line in self.product_component_ids:
            if line.product_id == final_product:
                for l in line.component_list_ids:
                    vals.append({
                                'component_id':l.component_id.id,
                                'internal_component': l.internal_component.id,
                                'product_uom_id': l.internal_component.uom_id.id,
                                'internal_quantity': l.internal_quantity,})
        return vals

    def return_bill_material_bom(self,final_product):
        vals = []
        for line in self.product_component_ids:
            if line.product_id == final_product:
                for l in line.component_list_ids:
                    if l.internal_component.id:
                        vals.append({'product_id': l.internal_component.id,
                                     'product_uom_id': l.internal_component.uom_id.id,
                                     'product_qty': l.internal_quantity})
        return vals

    def return_bom_id(self, line):
        bom_id_base = self.env['mrp.bom'].search([('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                                                  ('is_standard','=',True)],)

        print(bom_id_base,"base standard")
        if bom_id_base:
            bom_id = self.env['mrp.bom'].create({
                'product_tmpl_id': bom_id_base.product_tmpl_id.id,
                'product_id':bom_id_base.product_id.id,
                'code': line.order_id.partner_id.name,
                'product_uom_id': line.product_uom.id,
                'routing_id':bom_id_base.routing_id.id,
                'product_qty': bom_id_base.product_qty,
                'company_id': self.company_id.id,
                })
            print(bom_id,"new bom")
            for dic in self.return_bill_material(line.product_id):
                print("dicdicdic")
                print(dic)
                bom_id.write({'product_component_list_ids': [(0, 0, dic)]})
                print("done products base")
            bom_id.write({'bom_line_ids':[(6, 0, self.return_base_bom_lines(bom_id,line))]})
            for dic in self.return_bill_material_bom(line.product_id):
                bom_id.write({'bom_line_ids': [(0, 0, dic)]})
                print("done sec add")
        else:
            raise exceptions.ValidationError(_("Please set a standard Bill Material Of %s" % line.product_id.name))
        print("booooom_id",bom_id)
        return bom_id

    def return_base_bom_lines(self,bom_id,line):
        bom_id_base = self.env['mrp.bom'].search([('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                                                  ('is_standard', '=', True)], )
        print("------------>", bom_id_base.id)
        if bom_id_base:
            lst = []
            for bom in bom_id_base.bom_line_ids:
                lst.append(self.env['mrp.bom.line'].create({
                    'product_id': bom.product_id.id,
                    'product_uom_id': bom.product_uom_id.id,
                    'product_qty': bom.product_qty,
                    # 'component_id': bom.component_id.id,
                    # 'type': bom.type,
                    'bom_id':bom_id.id

                }).id)
            return lst

    def get_labour_cost(self,line):
        # for rec in self:
        bom_id_base = self.env['mrp.bom'].search([('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                                                      ('is_standard', '=', True)], )
        labour_cost_list = []
        for rec in bom_id_base.direct_labour_cost_ids:
            labour_cost_list.append({
                'operation_id':rec.operation_id.id,
                'unit_cost':rec.unit_cost,
            })
            print(labour_cost_list)
        return labour_cost_list

    def add_labour_cost(self, line, mo_production_id):
        labor_cost_obj = self.env['direct.labour.cost']
        labour_cost_list = self.get_labour_cost(line)
        print("labout cost",labour_cost_list)
        for list in labour_cost_list:
            list['mo_id']=mo_production_id.id
            print(list)
            labor_cost_obj.create(list)

    def send_to_mrp(self):
        for line in self.order_line:
            print(self.id)
            check = self.env['mrp.production.request'].search([('sale_order_id','=',self.id),('product_id','=',line.product_id.id)])
            print(check,"check")
            if check:
                raise exceptions.ValidationError(_("You Alrady Sent The Request"))
            bom_id = self.return_bom_id(line)
            print("------<>",bom_id)
            mo_production_id = self.env['mrp.production.request'].create({
                'product_id': line.product_id.id,
                'note':line.name,
                'product_uom_id':line.product_id.uom_id.id,
                'origin':self.partner_id.name,
                'sale_order_id':self.id,
                'quantity_qty':line.product_uom_qty,
                'bom_id':bom_id.id,
                'date_planned_start':self.mrp_date,
                'delivery_date': self.mrp_date,
                'company_id':self.company_id.id,
            })
            mo_production_id.get_bom_line_ids()
            print(mo_production_id,"production")
            # self.add_labour_cost(line,mo_production_id)