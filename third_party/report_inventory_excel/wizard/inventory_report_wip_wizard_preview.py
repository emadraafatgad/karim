# -*- coding: utf-8 -*-

import base64
import locale
import xlwt

from datetime import datetime
from dateutil.relativedelta import relativedelta
from io import StringIO, BytesIO

from odoo import tools
from odoo.exceptions import Warning
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from . import xls_format


class InventoryPreviewReportWizard(models.TransientModel):
    _inherit = 'inventory.export.wip.report.wizard'

    date_start = fields.Date(
        'Date Start', default=lambda *a: datetime.today().date() + relativedelta(day=1))
    date_end = fields.Date(
        'Date End', default=lambda *a: datetime.today().date() + relativedelta(day=31))
    location_ids = fields.Many2many('stock.location', 'ms_stock_card_locaton_rel', 'stock_card_id',
                                    'location_id', 'Lokasi', copy=False, domain=[('usage', '=', 'internal')])
    categ_ids = fields.Many2many('product.category', 'ms_stock_card_categ_rel', 'stock_card_id',
                                 'categ_id', 'Kategori Produk', copy=False)
    product_ids = fields.Many2many('product.product', 'ms_stock_card_product_rel', 'stock_card_id',
                                   'product_id', 'Produk', copy=False, domain=[('type', '=', 'product')])

    @api.onchange('date_start', 'date_end')
    def onchange_date(self):
        """
        This onchange method is used to check end date should be greater than 
        start date.
        """
        if self.date_start and self.date_end and \
                self.date_start > self.date_end:
            raise Warning(_('End date must be greater than start date'))

    @api.multi
    def get_result(self):
        cr, uid, context = self.env.args
        if context is None:
            context = {}
        context = dict(context)
        data = self.read()[0]

        start_date = data.get('date_start', False)
        end_date = data.get('date_end', False)
        if start_date and end_date and end_date < start_date:
            raise Warning(_("End date should be greater than start date!"))
        res_user = self.env["res.users"].browse(uid)

        # Create Inventory Export report in Excel file.
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')
        font = xlwt.Font()
        font.bold = True
        header = xlwt.easyxf('font: bold 1, height 280')
        # start_date = datetime.strptime(str(context.get("date_from")), DEFAULT_SERVER_DATE_FORMAT)
        # start_date_formate = start_date.strftime('%d/%m/%Y')
        # end_date = datetime.strptime(str(context.get("date_to")), DEFAULT_SERVER_DATE_FORMAT)
        # end_date_formate = end_date.strftime('%d/%m/%Y')
        # start_date_to_end_date = tools.ustr(start_date_formate) + ' To ' + tools.ustr(end_date_formate)

        style = xlwt.easyxf('align: wrap yes')
        worksheet.row(0).height = 500
        worksheet.row(1).height = 500
        for x in range(0, 41):
            worksheet.col(x).width = 6000
        borders = xlwt.Borders()
        borders.top = xlwt.Borders.MEDIUM
        borders.bottom = xlwt.Borders.MEDIUM
        border_style = xlwt.XFStyle()  # Create Style
        border_style.borders = borders
        border_style1 = xlwt.easyxf('font: bold 1')
        border_style1.borders = borders
        style = xlwt.easyxf('align: wrap yes', style)

        ids_location = []
        ids_categ = []
        ids_product = []
        where_end_date_awal = " sm.date is null "
        where_start_date = " 1=1 "
        if start_date:
            where_start_date = " sm.date + interval '7 hour' >= '%s 00:00:00' " % start_date
            where_end_date_awal = " sm.date + interval '7 hour' < '%s 00:00:00' " % start_date
        where_end_date = " 1=1 "
        if end_date:
            where_end_date = " sm.date + interval '7 hour' <= '%s 23:59:59'" % end_date
        where_location = " 1=1 "
        if ids_location:
            where_location = """(sm.location_id in %s 
            or sm.location_dest_id in %s)""" % (str(tuple(ids_location)).replace(',)', ')'),
                                                str(tuple(ids_location)).replace(',)', ')'))
        where_categ = " 1=1 "
        if ids_categ:
            where_categ = "pt.categ_id in %s" % str(
                tuple(ids_categ)).replace(',)', ')')
        where_product = " 1=1 "
        if ids_product:
            where_product = "pp.id in %s" % str(
                tuple(ids_product)).replace(',)', ')')
        query = """
                SELECT pp.default_code as kode_barang, pt.name as nama_barang, uu.name as satuan, sml.qty_done, sml.state, sm.name
                FROM stock_move sm 
                    LEFT JOIN product_product pp ON pp.id=sm.product_id
                    LEFT JOIN uom_uom uu ON uu.id=sm.product_uom
                    LEFT JOIN product_template pt ON pt.id=pp.product_tmpl_id
                    INNER JOIN stock_move_line sml ON sm.id=sml.move_id
                    where """ + where_start_date + """ and """ + where_end_date + """
                    -- AND sm.state = 'assigned' and qty_done = 0 and sm.raw_material_production_id is not null
                    AND sml.state = 'assigned' and sm.production_id is not null
                    AND sml.qty_done != 0
                    ORDER BY sm.id DESC
            """
        list_data = []
        company = self.env.user.company_id.name
        start_date_format = start_date.strftime('%d/%m/%Y')
        end_date_format = end_date.strftime('%d/%m/%Y')

        self._cr.execute(query)
        vals = self._cr.fetchall()

        no = 1
        for val in vals:
            list_data.append({
                'kode_barang': val[0],
                'nama_barang': val[1],
                'satuan': val[2],
                'jumlah': val[3],
                'keterangan': val[5]
            })
            no += 1
        hasil = list_data
        return hasil

    @api.multi
    def print_inventory_preview_report(self):
        return self.env.ref('report_inventory_excel.report_inventory_wip').report_action(self)
