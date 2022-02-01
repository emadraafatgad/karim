# -*- coding: utf-8 -*-
# module template
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Partner District',
    'version': '12.0',
    'category': 'Tools',
    'license': 'AGPL-3',
    'author': "Odoo Tips",
    'website': 'https://www.facebook.com/OdooTips/',
    'depends': ['base', 'sale', 'sale_management', 'sales_team'
                ],

    'images': ['images/main_screenshot.png'],
    'data': [
             'security/ir.model.access.csv',
             'views/res_partner_view.xml',
             ],
    'installable': True,
    'application': True,
}
