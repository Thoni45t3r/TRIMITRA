from odoo import fields, models, api, _


class ResPartnerBank(models.Model):

    _inherit = 'res.partner'

    show_bank_in_sales_invoice = fields.Many2one(
        string='Show Bank in Sales Invoice',
        comodel_name='res.partner.bank',
        ondelete='restrict',
    )