# -*- coding: utf-8 -*-
{
    'name': 'Freight Extra Kareem',
    'version': '12.0.1.0',
    'category': 'kareem Freight Management',
    'depends': [
        'base', 'sale', 'mrp', 'purchase','manufacturing_furnature'
    ],
    'author': 'Emad Raafat Gad',
    # 'website': 'https://odoo-community.org/',
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/freight_order_data.xml',
        'views/frieght_port.xml',
        'views/freight_container.xml',
        'views/frieght_order.xml',
        'views/custom_clearance.xml',
        'views/order_track.xml',
        'views/product_template.xml',
        'views/freight_configuration.xml',
        'views/sale_order.xml',

    ],
    'demo': [
        # 'demo/patient.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 1,
}
