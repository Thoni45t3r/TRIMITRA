# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    best_before_date = fields.Datetime(related='lot_id.use_date', store=True, readonly=False)
    volume = fields.Float(related='product_id.volume', store=True, readonly=False)
    volume_total = fields.Float('Volume total',compute='_compute_volume_total')
    weight = fields.Float(related='product_id.weight', store=True, readonly=False)
    weight_total = fields.Float('Weight total',compute='_compute_weight_total')


    def _compute_volume_total(self):
        for quant in self:
            quant.volume_total = quant.product_id.volume * quant.quantity
    
    def _compute_weight_total(self):
        for quant in self:
            quant.weight_total = quant.product_id.weight * quant.quantity

