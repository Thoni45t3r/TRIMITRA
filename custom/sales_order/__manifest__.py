# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2020
#   @author Pranoto Tahrir Fathoni <Thoni.45t3r@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

{
    'name'          : 'Sale Order',
    'depends'       : ['base', 'sale', 'stock'],
    'version'       : '1.0.0.1',
    'category'      : 'PTF Module',
    'summary'       : """
                        Sale Order
                        """,
    'description'   : """
Order
========

Module Customization for Order.

Preference:
-----------

* Customize Sale Order 
                            """,
    'author'        : "Pranoto Tahrir Fathoni",
    'website'       : "",
    'license'       : 'AGPL-3',
    'data'          : [
                    'views/sale_order_views.xml',
                    ],
    'installable'   : True,
    'application'   : True,
}
