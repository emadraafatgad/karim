# -*- coding: utf-8 -*-
# Copyright 2004-2009 Tiny SPRL
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Kareem',
    'version': '12.0.1.0.0',
    'category': 'manufacturing',
    'depends': [
        'base', 'sale','mrp','purchase','mapol_check_mrp_product_quantity',
    ],
    'author': 'Emad Raafat Gad',
    'website': 'https://odoo-community.org/',
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/bill_of_matrial_type.xml',
        'views/komash_sale_order.xml',
        'views/sales_order_komash.xml',
        'views/product_component_list.xml',
        'views/direct_labour_cost.xml',
        'views/purchase_product_available.xml',
        'views/direct_material_cost.xml',
        'views/mrp_request.xml',
        'views/stock_move_diffrance.xml',
        'views/mrp_monthly.xml',
        'views/do_produce.xml',

    ],
    'demo': [
        # 'demo/patient.xml',
    ],
    'installable': True,
	'application': True,
	'auto_install': False,
	'sequence':1,
}
