# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2020
#   @author Pranoto Tahrir Fathoni <Thoni.45t3r@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

from odoo import api, fields, models, tools
from odoo.addons.jasper_reports import JasperDataParser
from odoo.addons.jasper_reports.JasperReports import jasper_report_config

class jasper_report_sales_shipment(JasperDataParser.JasperDataParser):
    def __init__(self, cr, uid, ids, data, context):
        super(jasper_report_sales_shipment, self).__init__(cr, uid, ids, data, context)

    def generate_data_source(self, cr, uid, ids, data, context):
        return 'parameters'

    def generate_parameters(self, cr, uid, ids, data, context):
        return {
            'id' : int(data.get('id', ids and ids[0] or False)),
        }


    def generate_properties(self, cr, uid, ids, data, context):
        return {}

    def generate_output(self,cr, uid, ids, data, context):
        return 'pdf'
    
    def generate_records(self, cr, uid, ids, data, context):
        return {}

jasper_report_config.ReportJasper('report.sales_shipment_report',  'stock.picking', parser=jasper_report_sales_shipment,)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
