from odoo import models, fields, api
from odoo import tools
import odoo.addons.decimal_precision as dp
import time
import logging
from odoo.tools.translate import _
#from odoo import netsvc
import datetime
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

STATES = [
    ('draft', 'Draft'),
    ('open', 'Open'),
    ('close', 'Done')
]

class alisan_inkaso(models.Model):
    _name = "alisan.inkaso"
    #_rec_name = 'name'
    #_description = 'Inkaso'

    state = fields.Selection(string="State", selection=STATES, required=True, default="draft")
    name = fields.Char('Number', help='Nomor Inkaso', states={'draft': [('readonly', False)]})
    salesperson = fields.Many2one('res.users', string="Salesperson")
    inkaso_invoice_ids = fields.One2many('alisan.inkaso_invoice', 'inkaso_id', states={'draft': [('readonly', False)]})

    currency_id = fields.Many2one('res.currency', string='Currency',readonly=True)
    line_sum = fields.Monetary('Total Invoice Amount', compute='compute_total')
    residual_line_sum = fields.Monetary('Total Sisa Amount', compute='compute_total')
    
    _sql_constraints = [('name_uniq', 'unique(name)', _('Nomor inkaso tidak boleh sama'))]

    @api.one
    def compute_total(self):
        for item in self.inkaso_invoice_ids:
            self.line_sum += item.invoice_amount
            self.residual_line_sum += item.invoice_residual

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default['name'] = '/'
        return super(alisan_inkaso, self).copy(default=default)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('alisan.inkaso')
        return super(alisan_inkaso, self).create(vals)
    
    @api.multi
    def action_cancel(self):
        self.write({'state': STATES[0][0]})
    
    @api.multi
    def action_done(self):
        self.write({'state': STATES[2][0]})
    
    @api.multi
    def action_confirm(self):
        self.write({'state': STATES[1][0]})
        

    
class alisan_inkaso_invoice(models.Model):
    _name = "alisan.inkaso_invoice"
    
    inkaso_id = fields.Many2one('alisan.inkaso', 'Inkaso', help='')
    invoice_id = fields.Many2one('account.invoice', 'Invoice', help='Invoice to be paid', domain=[('state', '=', 'open')])
    date_invoice = fields.Date(string='Invoice Date', readonly=True, related='invoice_id.date_invoice')
    date_due = fields.Date('Due Date', related='invoice_id.date_due', readonly=True, help='')
    partner_id = fields.Many2one('res.partner','Customer', related='invoice_id.partner_id', help='Customer',readonly=True)
    currency_id = fields.Many2one('res.currency', related='invoice_id.currency_id', string='Currency',readonly=True)
    
    invoice_amount = fields.Monetary('Total Amount', related='invoice_id.amount_total', help='Invoice to be paid', readonly=True)
    invoice_residual = fields.Monetary('Amount Due', related='invoice_id.residual', help='Amount to pay', readonly=True)
    
    category = fields.Char('Category Code', compute='_get_category', store=True)
    
    #cash = fields.Integer('cash', domain=[('state', '=', 'open')],readonly=True)
    #giro = fields.Integer('giro', domain=[('state', '=', 'open')],readonly=True)
    #total = fields.Integer('total', domain=[('state', '=', 'open')],readonly=True)

    @api.one
    @api.depends('invoice_id')
    def _get_category(self):
        self.category = ''
        catlist = []
        if self.invoice_id:
            inv = self.env['account.invoice'].search([('id','=',self.invoice_id.id)])
            for ln in inv.invoice_line_ids:
                cat = ln.product_id.categ_id.name
                if cat:
                    if cat not in catlist:
                        catlist.append(cat)
        if catlist:
            mystring = ','.join(catlist)
            self.category = mystring
            
        
