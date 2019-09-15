# -*- coding: utf-8 -*-
# Copyright (C) 2016-present  Technaureus Info Solutions(<http://www.technaureus.com/>).

from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res['so_line_id'] = self.id
        return res
