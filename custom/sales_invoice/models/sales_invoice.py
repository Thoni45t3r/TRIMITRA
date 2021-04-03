# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2020
#   @author Pranoto Tahrir Fathoni <Thoni.45t3r@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

from odoo import models, fields, api, _
from datetime import datetime

class SalesInvoice(models.Model):
    _inherit    = ['account.invoice']
    
    @api.multi
    def invoice_print(self):
       return self.env.ref('sales_invoice.report_sales_invoice').report_action(self)
       
    @api.multi
    def invoice_print_ppn(self):
       return self.env.ref('sales_invoice.report_sales_invoice_ppn').report_action(self)
       
    @api.multi
    def invoice_print_nonppn(self):
       return self.env.ref('sales_invoice.report_sales_invoice_nonppn').report_action(self)
           
class SalesInvoiceLine(models.Model):
    _inherit    = ['account.invoice.line']
    
    ppn = fields.Boolean(string='PPN')
    
    @api.depends('invoice_line_ids.price_subtotal')
    def _line_total(self):
        for invoice in self:
            line_total = 0.0
            for line in invoice.invoice_line_ids:
                line_total += line.price_subtotal
    