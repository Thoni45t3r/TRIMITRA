from odoo import api, fields, models, _
import time
import logging
_logger = logging.getLogger(__name__)

class sale_order(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    validated_id = fields.Many2one(
        string='Validated by',
        comodel_name='res.users',
        ondelete='restrict',
    )
    