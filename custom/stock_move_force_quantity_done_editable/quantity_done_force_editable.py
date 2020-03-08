from odoo import api, fields, models, _

class ForceQtyDoneEditable(models.Model):

    _inherit = 'stock.move'

    # ********************* Inherit ************************
    @api.multi
    @api.depends('state', 'picking_id', 'product_id')
    def _compute_is_quantity_done_editable(self):
        for move in self:
            move.is_quantity_done_editable = True
    # ********************* End of Inherit ************************