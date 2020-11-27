# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Raja Ongkir",
    'description': "Check online shipping cost through Raja Ongkir",
    'category': 'Warehouse',
    'version': '1.0',
    'depends': ['delivery', 'mail'],
    'data': [
        'data/delivery_rjo_data.xml',
        'views/delivery_rjo_view.xml',
    ],
}
