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

class SalesShipment(models.Model):
    _inherit    = ['stock.picking']
    
    @api.multi
    def shipment_print(self):
       return self.env.ref('sales_shipment.report_sales_shipment').report_action(self)