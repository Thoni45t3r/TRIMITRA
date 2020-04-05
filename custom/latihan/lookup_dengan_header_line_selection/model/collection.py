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

class CollectionHeader(models.Model):
    _name = 'collection'
    
    state = fields.Selection(string="State", selection=STATES, required=True, default="draft")
    name = fields.Char('Number', help='Collection Number', states={'draft': [('readonly', False)]})
    salesperson = fields.Many2one('res.users', string="Salesperson")
    collection_invoice_ids = fields.One2many('collection_line', 'collection_id', states={'draft': [('readonly', False)]})
    collection_line_sum = fields.Integer('Total', compute='compute_total')
    
    #invoice_id = fields.Many2many('account.invoice', string='Select Invoice', help='Invoice to be paid', domain=[('state', '=', 'open')])
    
    _sql_constraints = [('name_uniq', 'unique(name)', _('Collection Number must no be same'))]

    def compute_total(self):
        for item in self.collection_invoice_ids:
            self.collection_line_sum += item.amount

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default['name'] = '/'
        return super(CoolectionHeader, self).copy(default=default)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('alisan.inkaso')
        return super(CollectionHeader, self).create(vals)
    
    @api.multi
    def action_cancel(self):
        self.write({'state': STATES[0][0]})
    
    @api.multi
    def action_done(self):
        self.write({'state': STATES[2][0]})
    
    @api.multi
    def action_confirm(self):
        for line in self.collection_invoice_ids:
            inv_obj = self.env["account.invoice"].search([("id", "=", line.invoice_id.id)])
            for inv in inv_obj:
                line.cash = line.invoice_amount - inv.residual
                line.invoice_residual = inv.residual
                _logger.info(line.invoice_amount)
                _logger.info(line.invoice_residual)
                _logger.info(line.cash)
                for giro_line in inv.giro_invoice_ids:
                    line.giro =+ giro_line.amount
                
        self.write({'state': STATES[1][0]})

    @api.onchange('invoice_id')
    def get_invoice_line(self):
        cust_lst = []
        for cl in self.invoice_id:
            cust_lst.append(cl.id)
        lines =[]
        inv_list = self.env["account.invoice"].search([("id", "in", cust_lst)])
        if inv_list:
            for val in inv_list:
                line_item = {
                              'invoice_id': val.id,
                              'invoice_amount': val.amount_total,
                              'invoice_residual': val.residual,
                              'partner_id': val.partner_id,
                              'date_due': val.date_due,
                        }
                lines += [line_item]
        self.update({'collection_invoice_ids': lines})

    @api.onchange('partner_id')   
    def onchange_customer(self):
        res = {}
        cust_lst = []

        for p in self.partner_id:
            inv_cpg_obj = self.env["account.invoice"].search([("partner_id.id", "=", p.id), ("state","=","open")])
            for inv in inv_cpg_obj:
                cust_lst.append(inv.id)
        if cust_lst:
            res = {
                   'domain': {'invoice_id': [('id', 'in', cust_lst)]},
            }
        else:
            res = {
                    'domain': {},
            }
        return res
        

class alisan_inkaso_invoice(models.Model):
    _name = 'collection_line'
    
    collection_id = fields.Many2one('collection', 'Collection Lines', help='')
    date_due = fields.Date('Due Date', help='')
    invoice_id = fields.Many2one('account.invoice', 'Invoice', help='Invoice to be paid', domain=[('state', '=', 'open')], readonly=True,)
    partner_id = fields.Many2one('res.partner','Customer', help='Customer',readonly=True)
    invoice_amount = fields.Integer('Total Amount', help='Invoice to be paid', domain=[('state', '=', 'open')] ,readonly=True)
    invoice_residual = fields.Integer('Amount Due', help='Amount to pay', domain=[('state', '=', 'open')],readonly=True)
    cash = fields.Integer('cash', domain=[('state', '=', 'open')],readonly=True)
    giro = fields.Integer('giro', domain=[('state', '=', 'open')],readonly=True)
    total = fields.Integer('total', domain=[('state', '=', 'open')],readonly=True)
