# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

{
    'name': 'Sales Report By Saleperson',
    'category': 'sale',
    'version': '12.0.0.1',
    'summary': 'This module provides Sales Report By Saleperson.',
    'website':"sitaramsolutions.in",
    'author': 'Sitaram',
    "license": "OPL-1",
    'description': '''This module provides Sales Report By Saleperson.
                      With the help of this moudule you can print sales report with groupby sale person.
                      sale person groupby report.
                      sale report.
                      '''
                   ,
    'depends': ['base', 'sale_management'],
    'data': [
        'views/sale_view.xml',
        'report/saleperson_report.xml',
        'report/saleperson_temp.xml'
    ],
    'images': ['static/description/banner.png'],
    'auto_install': False,
    'installable': True,
    'application': False,
}
