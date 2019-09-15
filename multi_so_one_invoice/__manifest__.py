# -*- coding: utf-8 -*-
# Copyright (C) 2016-present  Technaureus Info Solutions(<http://www.technaureus.com/>).

{
    'name': 'Single Invoice for Multiple Sales Orders',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'sequence': 1,
    'summary': 'Single Invoice for Multiple Sales Orders',
    'description': """
Manage multiple sales order of same customer in one invoice
===========================================================

This application allows you to create a single invoice for multiple sales orders of same customer.

    """,
    'website': 'http://www.technaureus.com/',
    'author': 'Technaureus Info Solutions Pvt. Ltd.',
    'depends': ['sale_management'],
    'price': 25,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'data': [
        'views/invoice_view.xml',
    ],
    'demo': [],
    'css': [],
    'images': ['images/multi_so_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'live_test_url': 'https://www.youtube.com/watch?v=rIxbD_GSjL8&t=46s'
}
