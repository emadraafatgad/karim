# -*- coding: utf-8 -*-

{
    "name": "Report Excel Inventory",
    "version": "1.0",
    'depends': [
        'stock', 'auditlog', 'purchase_stock', 'sale_stock'
    ],
    "author": 'Serpent Consulting Services Pvt. Ltd., Ibrahim',
    "category": "Inventory",
    "description": """
        Module to print the reports Excel Inventory.
    """,
    "init_xml": [],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/inventory_report_mutasi_wizard_view.xml',
        'wizard/inventory_report_mutasi_wizard_preview_view.xml',
        'wizard/inventory_report_mutasi_sisa_wizard_view.xml',
        'wizard/inventory_report_mutasi_sisa_wizard_preview_view.xml',
        'wizard/inventory_report_mutasi_jadi_wizard_view.xml',
        'wizard/inventory_report_mutasi_jadi_wizard_preview_view.xml',
        'wizard/inventory_report_mutasi_mesin_wizard_view.xml',
        'wizard/inventory_report_mutasi_mesin_wizard_preview_view.xml',
        'wizard/inventory_report_wip_wizard_view.xml',
        'wizard/inventory_report_wip_wizard_preview_view.xml',
        'wizard/inventory_report_pengeluaran_wizard_view.xml',
        'wizard/inventory_report_pengeluaran_wizard_preview_view.xml',
        'wizard/inventory_report_penerimaan_wizard_view.xml',
        'wizard/inventory_report_penerimaan_wizard_preview_view.xml',
        'views/stock_picking_view.xml',
        'views/product_category_view.xml',
        'report/mutasi_report.xml',
        'views/menu_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
