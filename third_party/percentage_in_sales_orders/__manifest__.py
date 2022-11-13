# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: fasluca(<https://www.cybrosys.com>)

###################################################################################

{
    'name': 'Percentage In Sales Orders',
    'version': '12.0.1.1.0',
    'category': 'Sales Management',
    'summary': "Discount Percentage",
    'author': 'emad',
    'company': 'emad',
    'website': 'http://www.cybrosys.com',
    'description': """

=======================

""",
    'depends': ['sale',
                'account'
                ],
    'data': [
        'views/sale_view.xml',

    ],
    'demo': [
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
}
