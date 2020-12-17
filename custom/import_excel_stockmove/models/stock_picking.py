# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    fleet_id = fields.Many2one('fleet.vehicle', 'Vehicle')
    driver_name = fields.Char(related='fleet_id.driver_id.name', store=True, readonly=True)
    picking_code = fields.Selection([('incoming', 'Vendors'), ('outgoing', 'Customers'), ('internal', 'Internal')], 'Type of Operation', related='picking_type_id.code', store=True, readonly=True)
