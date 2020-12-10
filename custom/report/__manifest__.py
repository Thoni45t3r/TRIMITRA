# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Report',
    'category': 'Base',
    'summary': 'Hidden',
    'description': """
Report
        """,
    'depends': ['base', 'web', 'base_setup'],
    'data': [
        'security/ir.model.access.csv',
        'views/ir_actions_report_views.xml',
    ],
    'qweb' : [
        'static/src/xml/*.xml',
    ],
    'auto_install': True,
}
