# -*- coding: utf-8 -*-
# Copyright 2004-2009 Tiny SPRL
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Kareem Extra',
    'version': '12.0.1.0',
    'category': 'Manufacturing',
    'depends': [
        'base', 'sale','mrp','purchase','uom','hr','hr_attendance','hr_payroll',
    ],
    'author': 'Emad Raafat Gad',
    'website': 'https://odoo-community.org/',
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_package_line.xml',
        'views/mrp_package.xml',
        'views/work_order_employee.xml',
        'views/delivery_state.xml',
    ],
    'demo': [
        # 'demo/patient.xml',
    ],
    'installable': True,
	'application': True,
	'auto_install': False,
	'sequence':1,
}
