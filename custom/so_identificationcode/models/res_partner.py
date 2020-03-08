from odoo import fields, models

class ResPartner(models.Model):

    _inherit = 'res.partner'

    identification_code = fields.Char(string="Identification Code")
    

