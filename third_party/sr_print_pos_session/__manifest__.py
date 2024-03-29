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
    'name': "Print POS Session Report",
    'version': "12.0.0.1",
    'summary': "",
    'category': 'Point Of Sale',
    "license": "OPL-1",
    'description': """
    """,
    'author': "Sitaram",
    'website': "sitaramsolutions.in",
    'depends': ['base', 'point_of_sale','sale_management'],
    'data': [
        'reports/pos_report.xml',
        'reports/pos_session_report_template.xml',
        'reports/pos_order_report_template.xml',
        'views/pos_filter_data.xml',
        'views/res_config_settings_views.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.png'],
    'live_test_url': 'https://youtu.be/xYuOpF4aZis',
    'installable': True,
    'application': False,
    'auto_install': False,
}
