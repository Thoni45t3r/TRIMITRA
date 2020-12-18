# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = 'stock.move.line'

    volume = fields.Float(related='product_id.volume', store=True, readonly=False)
    volume_total = fields.Float('Volume total',compute='_compute_volume_total')
    weight = fields.Float(related='product_id.weight', store=True, readonly=False)
    weight_total = fields.Float('Weight total',compute='_compute_weight_total')


    def _compute_volume_total(self):
        for move in self:
            move.volume_total = move.product_id.volume * move.product_uom_qty
    
    def _compute_weight_total(self):
        for move in self:
            move.weight_total = move.product_id.weight * move.product_uom_qty

