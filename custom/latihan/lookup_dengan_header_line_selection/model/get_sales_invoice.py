from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SalesInvoiceHeaderTemp(models.TransientModel):
    _name = 'sales_invoice_header'
    _description = 'Search form for Open Sales Invoice'

    salesperson = fields.Many2many('res.users', string="Salesperson")
    partner_id = fields.Many2many('res.partner', string="Customer")
    inkaso_invoice_ids = fields.One2many('sales_invoice_line', 'line_id')

    @api.multi
    def search_sales_invoice(self):
        if (not self.partner_id) and (not self.salesperson):
            raise UserError(_("Please filter based on customer or salesperson"))

        inv = self.env["account.invoice"].search([('state', '=', 'open'),('type','=','out_invoice')])
        if not inv:
            raise UserError(_("There is not sales invoice with open status"))
        invfilter = []
        if self.partner_id or self.salesperson:
            for p in self.partner_id:
                inv2 = inv.search([('partner_id','=',p.id)])
                if inv2:
                    for doc in inv2:
                        invfilter.append(doc)
            for p in self.salesperson:
                inv2 = inv.search([('user_id','=',p.id)])
                if inv2:
                    for doc in inv2:
                        invfilter.append(doc)
        else:
            invfilter = inv #self.env["account.invoice"].search([('state', ''='', 'open'),('type','=','out_invoice')])

        if not invfilter:
            raise UserError(_("There is not sales invoice with open status"))

        invoice_ids = [(0, 0,{"invoice_id": doc.id,}) for doc in invfilter]
        self.inkaso_invoice_ids.unlink()
        self.inkaso_invoice_ids = invoice_ids
        
        return {"type": "ir.actions.do_nothing",}


class SalesInvoiceLineTemp(models.TransientModel):
    _name = 'sales_invoice_line'

    line_id = fields.Many2one('sales_invoice_header', 'Line')
    invoice_id = fields.Many2one('account.invoice', 'Invoice', help='Invoice to be paid', domain=[('state', '=', 'open')], readonly=True,)
    
    partner_id = fields.Many2one('res.partner',
                                string='Partner', readonly=True, 
                                related='invoice_id.partner_id')
    date_invoice = fields.Date(string='Invoice Date',
        readonly=True, related='invoice_id.date_invoice')
    number = fields.Char(related='invoice_id.move_id.name', readonly=True)

    # commercial_partner_id
    # reference
    # name
    # journal_id
    # company_id
    # user_id
    # date_due
    # origin
    # amount_untaxed_invoice_signed
    # amount_tax_signed
    # amount_total_signed
    # residual_signed
    # currency_id
    # company_currency_id
    # state
    # type