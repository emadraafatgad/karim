# -*- coding: utf-8 -*-
# Copyright 2004-2009 Tiny SPRL
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Kareem',
    'version': '12.0.1.0.0',
    'category': 'manufacturing',
    'depends': [
        'base', 'sale', 'mrp', 'purchase', 'partner_district', 'mapol_check_mrp_product_quantity', 'stock',
        'delivery_carrier_info',
    ],
    'author': 'Emad Raafat Gad',
    'website': 'https://odoo-community.org/',
    'license': 'AGPL-3',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/mrp_operation_workcenter.xml',
        'views/package_size.xml',
        'views/mrp_packaging.xml',
        'views/mrp_paint_request.xml',
        'views/mrp_carpenter_request.xml',
        'views/paint_price_list.xml',
        'views/bill_of_matrial_type.xml',
        'views/komash_sale_order.xml',
        'views/sales_order_komash.xml',
        'views/mrp_rout_checklist.xml',
        'views/product_component_list.xml',
        'views/direct_labour_cost.xml',
        'views/purchase_product_available.xml',
        'views/direct_material_cost.xml',
        'views/mrp_request.xml',
        'views/mrp_request_line.xml',
        'views/stock_move_diffrance.xml',
        'views/mrp_monthly.xml',
        'views/do_produce.xml',
        'views/work_order_worker.xml',
        'views/purchase_requiest_vendor.xml',
        'views/mrp_request_report.xml',
        'reports/mrp_request_total_report.xml',
        'reports/purchase_report.xml',
        'reports/deliveryslip.xml',
        'reports/mrp_request_all_total_report.xml',
        'reports/mrp_request_mo_report.xml',
        'wizard/print_all_materials.xml',
        'wizard/print_mos_materials.xml',


    ],
    'demo': [
        # 'demo/patient.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 1,
}
