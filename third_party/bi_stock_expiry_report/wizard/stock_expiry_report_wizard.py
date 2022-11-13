# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
################################################################################

from odoo import models, fields, api, _
import io
from odoo.exceptions import except_orm
from datetime import datetime,date,timedelta
import collections
import base64
import time
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
try:
    import xlwt
except ImportError:
    xlwt = None

class stock_expiry_report_wizard(models.TransientModel):
    _name = 'stock.expiry.report.wizard'

    stock_expiry_days = fields.Integer(string="Generate Report For (Days)")
    include_expiry = fields.Boolean(string='Include Expiry Stock')
    report_type = fields.Selection([('all','All'),('location','Location'),('warehouse','Warehouse')],string='Report Type', default='all')
    location_ids = fields.Many2many('stock.location', 'location_wiz_rel','loc_id','wiz_id',string='Location')
    warehouse_ids = fields.Many2many('stock.warehouse', 'wh_wiz_rel_expiry', 'wh', 'wiz', string='Warehouse')
    
    def get_warehouse(self):
        if self.warehouse_ids:
            l1 = []
            l2 = []
            for i in self.warehouse_ids:
                obj = self.env['stock.warehouse'].search([('id', '=', i.id)])
                for j in obj:
                    l2.append(j.lot_stock_id.id)
            return l2
        return []

    def get_locations(self):
        if self.location_ids:
            l1 = []
            l2 = []
            for i in self.location_ids:
                obj = self.env['stock.location'].search([('id', '=', i.id)])
                for j in obj:
                    l2.append(j.id)
            return l2
        return []

    @api.multi  
    def print_expiry_report_pdf(self):
        datas = {
            'ids': self._ids,
            'model': 'stock.expiry.report.wizard',
            'stock_expiry_days':self.stock_expiry_days,
            'include_expiry':self.include_expiry,
            'report_type':self.report_type,
            'location_ids':self.get_locations(),
            'warehouse_ids':self.get_warehouse(),
            }
        return self.env.ref('bi_stock_expiry_report.report_expiry_print').report_action(self,data=datas)

    def get_stock_expiry_data(self):
        vals = {}
        lines = []
        loc_list = []
        ware_list = []
        lot_obj = self.env['stock.production.lot']
        quant_obj = self.env['stock.quant']
        product_ids = self.env['product.product'].search([])
        current_date = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        diff = (date.today() + timedelta(days=self.stock_expiry_days)).strftime(DEFAULT_SERVER_DATE_FORMAT)
        for product in product_ids:
            if self.report_type == 'location':
                for loc in self.location_ids:
                    loc_list.append(loc.id)
                quants = quant_obj.search([('product_id','=',product.id),('removal_date','<=',current_date),('location_id','in',loc_list)])
            if self.report_type == 'warehouse':
                for ware in self.warehouse_ids:
                    ware_list.append(ware.lot_stock_id.id)
                quants = quant_obj.search([('product_id','=',product.id),('removal_date','<=',current_date),('location_id','in',ware_list)])
            if self.report_type == 'all':
                quants = quant_obj.search([('product_id','=',product.id),('removal_date','<=',current_date)])
            if quants:
                for i in quants:
                    vals = {'name':i.product_id.name,
                            'lot_id':i.lot_id.name,
                            'quantity':i.quantity,
                            'remove_date':i.removal_date
                            }
                    lines.append(vals)
        return lines
            
    @api.multi  
    def print_expiry_excel_report(self):
        filename = 'Stock Expiry Report.xls'
        #get_warehouse = self.get_warehouse()
        #get_warehouse_name = self._get_warehouse_name()
        l1 = []
        #get_company = self.get_company()
        #get_currency = self.get_currency()
        days = str(self.stock_expiry_days) + 'Days'
        workbook = xlwt.Workbook()
        stylePC = xlwt.XFStyle()
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        fontP = xlwt.Font()
        fontP.bold = True
        fontP.height = 200
        stylePC.font = fontP
        stylePC.num_format_str = '@'
        stylePC.alignment = alignment
        style_title = xlwt.easyxf("font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center;pattern: pattern solid, fore_colour aqua;")
        style_table_header = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center")
        style = xlwt.easyxf("font:height 200; font: name Liberation Sans,color black;")
        worksheet = workbook.add_sheet('Sheet 1')
        worksheet.write_merge(0, 1, 0, 4, "Stock Expiry Report", style=style_title)
        worksheet.write_merge(2, 3, 0, 0, "Duration", style=style_table_header)
        worksheet.write_merge(2, 3, 1, 1, days, style=style_table_header)
        if self.include_expiry:
            worksheet.write_merge(2, 3, 3, 4, "Including Expiry Stock", style=style_table_header)
        worksheet.write(5, 0, 'No', style_table_header)
        worksheet.write(5, 1, 'Product Name', style_table_header)
        worksheet.write(5, 2, 'Product Lot', style_table_header)
        worksheet.write(5, 3, 'Quantity', style_table_header)
        worksheet.write(5, 4, 'Removal Date', style_table_header)
        get_line = self.get_stock_expiry_data()
        prod_row = 6
        prod_col = 0
        count = 1
        for each in get_line:
            worksheet.write(prod_row, prod_col, count, style)
            worksheet.write(prod_row, prod_col+1, each['name'], style)
            worksheet.write(prod_row, prod_col+2, each['lot_id'], style)
            worksheet.write(prod_row, prod_col+3, each['quantity'], style)
            worksheet.write(prod_row, prod_col+4, each['remove_date'], style)
            prod_row = prod_row + 1
            count = count+1



        """worksheet.write(3, 1, 'Start Date:', style_table_header)
        worksheet.write(4, 1, self.start_date)
        worksheet.write(3, 3, 'End Date', style_table_header)
        worksheet.write(4, 3, self.end_date)
        worksheet.write(3, 4, 'Company', style_table_header)
        worksheet.write(4, 4, get_company and get_company[0] or '',)
        worksheet.write(3, 6, 'Warehouse(s)', style_table_header)
        worksheet.write(3, 5, 'Currency', style_table_header)
        worksheet.write(4, 5, get_currency and get_currency[0] or '',)
        w_col_no = 7
        w_col_no1 = 8
        if get_warehouse_name:
               # w_col_no = w_col_no + 8
            worksheet.write(4, 6,get_warehouse_name, stylePC)
               # w_col_no1 = w_col_no1 + 9
        if self.display_sum:
            worksheet.write_merge(0, 0, 0, 5, "Inventory Valuation Summary Report", style=style_title)
            worksheet.write(6, 0, 'Category', style_table_header)
            worksheet.write(6, 1, 'Beginning', style_table_header)
            worksheet.write(6, 2, 'Internal', style_table_header)
            worksheet.write(6, 3, 'Received', style_table_header)
            worksheet.write(6, 4, 'Sales', style_table_header)
            worksheet.write(6, 5, 'Adjustment', style_table_header)
            worksheet.write(6, 6, 'Ending', style_table_header)
            worksheet.write(6, 7, 'Valuation', style_table_header)
            prod_row = 7
            prod_col = 0
            for i in get_warehouse:
                get_line = self.get_data()
                for each in get_line:
                    worksheet.write(prod_row, prod_col, each['category'], style)
                    worksheet.write(prod_row, prod_col+1, each['beginning'], style)
                    worksheet.write(prod_row, prod_col+2, each['internal'], style)
                    worksheet.write(prod_row, prod_col+3, each['incoming'], style)
                    worksheet.write(prod_row, prod_col+4, each['sale_value'], style)
                    worksheet.write(prod_row, prod_col+5, each['outgoing'], style)
                    worksheet.write(prod_row, prod_col+6, each['net_on_hand'], style)
                    worksheet.write(prod_row, prod_col+7, each['total_value'], style)
                    prod_row = prod_row + 1
                break
            prod_row = 6
            prod_col = 7
        else:
            worksheet.write_merge(0, 0, 0, 5, "Inventory Valuation Report", style=style_title)
            worksheet.write(6, 0, 'Default Code', style_table_header)
            worksheet.write(6, 1, 'Name', style_table_header)
            worksheet.write(6, 2, 'Category', style_table_header)
            worksheet.write(6, 3, 'Cost Price', style_table_header)
            worksheet.write(6, 4, 'Beginning', style_table_header)
            worksheet.write(6, 5, 'Internal', style_table_header)
            worksheet.write(6, 6, 'Received', style_table_header)
            worksheet.write(6, 7, 'Sales', style_table_header)
            worksheet.write(6, 8, 'Adjustment', style_table_header)
            worksheet.write(6, 9, 'Ending', style_table_header)
            worksheet.write(6, 10, 'Valuation', style_table_header)
            prod_row = 7
            prod_col = 0
            for i in get_warehouse:
                get_line = self.get_lines(i)
                for each in get_line:
                    print ("each------------------",each)
                    worksheet.write(prod_row, prod_col, each['sku'], style)
                    worksheet.write(prod_row, prod_col+1, each['name'], style)
                    worksheet.write(prod_row, prod_col+2, each['category'], style)
                    worksheet.write(prod_row, prod_col+3, each['cost_price'], style)
                    worksheet.write(prod_row, prod_col+4, each['beginning'], style)
                    worksheet.write(prod_row, prod_col+5, each['internal'], style)
                    worksheet.write(prod_row, prod_col+6, each['incoming'], style)
                    worksheet.write(prod_row, prod_col+7, each['sale_value'], style)
                    worksheet.write(prod_row, prod_col+8, each['outgoing'], style)
                    worksheet.write(prod_row, prod_col+9, each['net_on_hand'], style)
                    worksheet.write(prod_row, prod_col+10, each['total_value'], style)
                    prod_row = prod_row + 1
                break
            prod_row = 6
            prod_col = 7"""
        fp = io.BytesIO()
        workbook.save(fp)
        
        export_id = self.env['expiry.report.excel'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        res = {
                        'view_mode': 'form',
                        'res_id': export_id.id,
                        'res_model': 'expiry.report.excel',
                        'view_type': 'form',
                        'type': 'ir.actions.act_window',
                        'target':'new'
                }
        return res


class stock_expiry_excel(models.TransientModel):

    _name = "expiry.report.excel"


    excel_file = fields.Binary('Excel Report for Stock Expiry', readonly =True)
    file_name = fields.Char('Excel File', size=64)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:# 

