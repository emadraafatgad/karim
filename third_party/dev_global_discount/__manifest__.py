# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################  
{
    "name": "Sale,Purchase & Invoice Discount with Accounting Entries",
    "category": 'Generic Modules/Sales Management',
    "version": '12.0.1.0',
    "sequence": 1,
    "summary": """
                  odoo Apps will set global Fixed/Percentage discount in Sale, Purchase, Invoice with accounting Entries.
        """,
    "description": """
        odoo Apps will set global Fixed/Percentage discount in Sale, Purchase, Invoice with accounting Entries.

Sale purchase invoice discount with accounting entries
Global sale purchase invoice discount
Global sale purchase discount odoo
Sale purchase invoice discount with accounting entries
Apply discount on total sales order
Apply discount on total Purchase order.
Apply discount on total Invoices.
Both Fixed and percentage method can be work out.
Discount account Setup & Generate Accounting Entries.
Sale invoice discount entries 
Purchase invoice discount entries
Sales invoice discount entries oddo
Purchase invoice entries oddo
Sale,Purchase & Invoice Discount with Accounting Entries & Limits
Create sales invoice discount entry
Create purchase invoice discount entry
Create sales invoice discount accounting entry
Create purchase invoice discount Accounting entry
Odoo Create sales invoice discount entry
Odoo Create purchase invoice discount entry
Odoo Create sales invoice discount accounting entry
Odoo Create purchase invoice discount Accounting entry
                                   
        
    """,
    'author': 'DevIntelle Consulting Service Pvt.Ltd', 
    'website': 'http://www.devintellecs.com',
    "depends": ['sale','account','purchase'],
    "images": ['images/main_screenshot.jpg'],
    "data": [
        'views/sale_order_view.xml',
        'views/account_account_view.xml',
        'views/account_invoice_view.xml',
        'views/purchase_order_view.xml',
        'views/discount_field_sale_report.xml',
        'views/discount_field_purchase_report.xml',
        'views/discount_field_invoice_report.xml',
        'wizard/discount_rate.xml',
        
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    'price':35.0,
    'currency':'EUR',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
