# -*- coding: utf-8 -*-

{
    "name": "mroMaterial Planning before Production",
    'version': '12.0.2.0.0',
    "author" : "Mapol Business Solutions Pvt Ltd",
    "website": "http://www.mapolbs.com/",
    'images': ['static/description/icon.png'],
    'summary': "Module helps to plan for the material and its corresponding bill of material approval before proceeding the manufacturing order.",
    "category": "Manufacturing",
    "depends": [
        "mrp",
        "stock",
        "product",
        "purchase",
        "sale",
        "hr",
        "mapol_check_mrp_product_quantity"
    ],
    "license": "LGPL-3",
    "data": [
        'security/ir.model.access.csv',
        "views/mrp_view.xml",
        "views/machine_allocation_view.xml"
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
