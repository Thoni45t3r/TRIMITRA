# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools
from odoo.exceptions import MissingError, UserError, ValidationError
from odoo.tools.safe_eval import safe_eval, test_python_expr


class ir_actions_report(models.Model):
    _inherit = 'ir.actions.report'
    
    usage = fields.Char(string='Action Usage')
    report_type = fields.Selection([('qweb-pdf', 'PDF'),
                                    ('qweb-html', 'HTML'),
                                    ('controller', 'Controller'),
                                    ('pdf', 'RML pdf (deprecated)'),
                                    ('sxw', 'RML sxw (deprecated)'),
                                    ('webkit', 'Webkit (deprecated)')],
                                   required=True, default="pdf",
                                   help="HTML will open the report directly in your browser, PDF will use wkhtmltopdf to render the HTML into a PDF file and let you download it, Controller allows you to define the url of a custom controller outputting any kind of report.")
    
    # Deprecated rml stuff
    header = fields.Boolean(string='Add RML Header', default=True, help="Add or not the corporate RML header")
    parser = fields.Char(string='Parser Class')
    auto = fields.Boolean(string='Custom Python Parser', default=True)

    report_xsl = fields.Char(string='XSL Path')
    report_xml = fields.Char(string='XML Path')

    report_rml = fields.Char(string='Main Report File Path/controller', help="The path to the main report file/controller (depending on Report Type) or empty if the content is in another data field")
    report_file = fields.Char(related='report_rml', string='Report File', required=False, readonly=False, store=True,
                              help="The path to the main report file (depending on Report Type) or empty if the content is in another field")

    report_sxw = fields.Char(compute='_compute_report_sxw', string='SXW Path')
    report_sxw_content_data = fields.Binary(string='SXW Content Data')
    report_rml_content_data = fields.Binary(string='RML Content Data')
    report_sxw_content = fields.Binary(compute='_compute_report_sxw_content', inverse='_inverse_report_sxw_content', string='SXW Content')
    report_rml_content = fields.Binary(compute='_compute_report_rml_content', inverse='_inverse_report_rml_content', string='RML Content')

    @api.depends('report_rml')
    def _compute_report_sxw(self):
        for report in self:
            if report.report_rml:
                self.report_sxw = report.report_rml.replace('.rml', '.sxw')

    def _report_content(self, name):
        data = self[name + '_content_data']
        if not data and self[name]:
            try:
                with tools.file_open(self[name], mode='rb') as fp:
                    data = fp.read()
            except Exception:
                data = False
        return data
        
    @api.depends('report_sxw', 'report_sxw_content_data')
    def _compute_report_sxw_content(self):
        for report in self:
            report.report_sxw_content = report._report_content('report_sxw')

    @api.depends('report_rml', 'report_rml_content_data')
    def _compute_report_rml_content(self):
        for report in self:
            report.report_rml_content = report._report_content('report_rml')

    def _inverse_report_sxw_content(self):
        for report in self:
            report.report_sxw_content_data = report.report_sxw_content

    def _inverse_report_rml_content(self):
        for report in self:
            report.report_rml_content_data = report.report_rml_content

    @api.model_cr
    def _lookup_report(self, name):
        """
        Look up a report definition.
        """
        join = os.path.join

        # First lookup in the deprecated place, because if the report definition
        # has not been updated, it is more likely the correct definition is there.
        # Only reports with custom parser sepcified in Python are still there.
        if 'report.' + name in odoo.report.interface.report_int._reports:
            return odoo.report.interface.report_int._reports['report.' + name]

        self._cr.execute("SELECT * FROM ir_act_report_xml WHERE report_name=%s", (name,))
        row = self._cr.dictfetchone()
        if not row:
            raise Exception("Required report does not exist: %s" % name)

        if row['report_type'] in ('qweb-pdf', 'qweb-html'):
            return row['report_name']
        elif row['report_rml'] or row['report_rml_content_data']:
            kwargs = {}
            if row['parser']:
                kwargs['parser'] = getattr(odoo.addons, row['parser'])
            return report_sxw('report.'+row['report_name'], row['model'],
                              join('addons', row['report_rml'] or '/'),
                              header=row['header'], register=False, **kwargs)
        elif row['report_xsl'] and row['report_xml']:
            return report_rml('report.'+row['report_name'], row['model'],
                              join('addons', row['report_xml']),
                              row['report_xsl'] and join('addons', row['report_xsl']),
                              register=False)
        else:
            raise Exception("Unhandled report type: %s" % row)

    @api.multi
    def create_action(self):
        """ Create a contextual action for each report. """
        for report in self:
            model = self.env['ir.model']._get(report.model)
            report.write({'binding_model_id': model.id, 'binding_type': 'report'})
        return True

    @api.multi
    def unlink_action(self):
        """ Remove the contextual actions created for the reports. """
        self.check_access_rights('write', raise_exception=True)
        self.filtered('binding_model_id').write({'binding_model_id': False})
        return True
        
    @api.model
    def render_report(self, res_ids, name, data):
        """
        Look up a report definition and render the report for the provided IDs.
        """
        report = self._lookup_report(name)
        if isinstance(report, basestring):  # Qweb report
            # The only case where a QWeb report is rendered with this method occurs when running
            # yml tests originally written for RML reports.
            if tools.config['test_enable'] and not tools.config['test_report_directory']:
                # Only generate the pdf when a destination folder has been provided.
                return self.env['report'].get_html(res_ids, report, data=data), 'html'
            else:
                return self.env['report'].get_pdf(res_ids, report, data=data), 'pdf'
        else:
            return report.create(self._cr, self._uid, res_ids, data, context=self._context)
