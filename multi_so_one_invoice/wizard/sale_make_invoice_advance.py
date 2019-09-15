# -*- coding: utf-8 -*-
# Copyright (C) 2016-present  Technaureus Info Solutions(<http://www.technaureus.com/>).

import time

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        for line in res.invoice_line_ids:
            line.write({'so_line_id': so_line.id})
        return res
