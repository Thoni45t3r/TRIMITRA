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
    'name'          : 'Shipment',
    'depends'       : ['base', 'sale', 'stock'],
    'version'       : '1.0.0.1',
    'category'      : 'PTF Module',
    'summary'       : """
                        Sales Shipment
                        """,
    'description'   : """
Shipment
========

Module Customization for Shipment.

Preference:
-----------

* Customize Sales Shipment 
                            """,
    'author'        : "Pranoto Tahrir Fathoni",
    'website'       : "",
    'license'       : 'AGPL-3',
    'data'          : [
                    'views/sales_shipment_views.xml',
                    'views/action_report.xml',
                    'report/report_sales_shipment.xml',
                    ],
    'installable'   : True,
    'application'   : True,
}
