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

class SalesOrder(models.Model):
    _inherit    = ['sale.order.line']
    
    @api.depends('product_uom_qty', 'discount', 'discount2', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0) * (1 - (line.discount2 or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
    
    discount2 = fields.Float(string='Discount2 (%)', default=0.00)
    
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)