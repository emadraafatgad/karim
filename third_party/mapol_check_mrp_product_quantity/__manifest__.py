# -*- coding: utf-8 -*-

{
    "name": "Bill of Materials Stock Check",
    'version': '12.0.2.0.0',
    "author" : "Mapol Business Solutions Pvt Ltd",
    "website": "http://mapolbs-opensource.com",
    'images': ['static/description/icon.png'],
    'summary': "Module helps us to check BOM product quantity before manufacturing",
    'category': 'Manufacturing',
    "depends": [
        "mrp",
        "stock",
        "product",
        "purchase"

    ],
    "license": "LGPL-3",
    "data": [
        'security/ir.model.access.csv',
        'security/bom_purchase_request_security.xml',
        'data/bom_check_sequence.xml',
        'data/bom_purchase_request_seq.xml',
        'wizard/available_quantity_views.xml',
        'wizard/partial_quantity_views.xml',
        'wizard/no_quantity_views.xml',
        "views/bom_quantity_check_view.xml",
        "views/bom_purchase_request_view.xml",
        "views/mrp_bom_views.xml"
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
