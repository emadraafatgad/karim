# -*- coding: utf-8 -*-
# Part of AktivSoftware See LICENSE file for full
# copyright and licensing details.
{
    'name': "Unreserved Components in MRP Orders",

    'summary': """
            This Module is used to unreserve Raw Materials in the MRP. """,

    'description': """
        This Module is use to Unreserve Specific Raw Material in the MRP
    """,
    'author': "Aktiv Software",
    'website': "http://www.aktivsoftware.com",
    'license': "OPL-1",
    'version': '12.0.1.0.0',
    # 'price': 8.00,
    # 'currency': "EUR",
    'depends': ['mrp'],
    # always loaded
    'data': [
        'views/mrp_production_view.xml',
    ],
    'images': [
        'static/description/banner.jpg',
    ],
    'auto_install': False,
    'installable': True,
    'application': False
    # only loaded in demonstration mode
}
