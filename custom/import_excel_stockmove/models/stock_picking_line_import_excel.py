from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules import get_module_path
import os, os.path
from datetime import datetime
import base64
import xlrd
import math


class ImportReceiptLine(models.TransientModel):
    _name = 'stock.picking.import.receipt'
    _description = 'import xls file into stock picking line'

    partner_id = fields.Many2one('res.partner', 'Partner')
    location_id = fields.Many2one(
        'stock.location', "Source Location",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_src_id, required=True)
    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_dest_id, required=True)
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type',required=True)
    upload_file = fields.Binary(string="Lookup Excel File")
    fill_qty_done = fields.Boolean(string="Fill Quantity Done during import")

    @api.onchange('picking_type_id', 'partner_id')
    def onchange_picking_type(self):
        if self.picking_type_id:
            if self.picking_type_id.default_location_src_id:
                location_id = self.picking_type_id.default_location_src_id.id
            elif self.partner_id:
                location_id = self.partner_id.property_stock_supplier.id
            else:
                location_id = self.env['stock.warehouse']._get_partner_locations()

            if self.picking_type_id.default_location_dest_id:
                location_dest_id = self.picking_type_id.default_location_dest_id.id
            elif self.partner_id:
                location_dest_id = self.partner_id.property_stock_customer.id
            else:
                location_dest_id = self.env['stock.warehouse']._get_partner_locations()

            self.location_id = location_id
            self.location_dest_id = location_dest_id

        # TDE CLEANME move into onchange_partner_id
        if self.partner_id and self.partner_id.picking_warn:
            if self.partner_id.picking_warn == 'no-message' and self.partner_id.parent_id:
                partner = self.partner_id.parent_id
            elif self.partner_id.picking_warn not in ('no-message', 'block') and self.partner_id.parent_id.picking_warn == 'block':
                partner = self.partner_id.parent_id
            else:
                partner = self.partner_id
            if partner.picking_warn != 'no-message':
                if partner.picking_warn == 'block':
                    self.partner_id = False
                return {'warning': {
                    'title': ("Warning for %s") % partner.name,
                    'message': partner.picking_warn_msg
                }}

    @api.one
    def import_format_inbound_customer(self):
        
        #<< testing header no.
        #context = dict(self._context or {})
        #stock_picking = self.env['stock.picking'].browse(context.get('active_ids'))
        #stock_picking = stock_picking[0]
        #raise UserError(_('test: stock_picking.id = %s ' % stock_picking.id))
        #>>
        
        if not self.upload_file:
            raise UserError(_('Lookup xls excel file before upload'))
        mpath = get_module_path('import_excel_stockmove')
        out_file_name = 'inbound.xls'
        out_file = mpath + _('/tmp/' + out_file_name)
        #delete file if exist
        if os.path.exists(out_file):
            os.remove(out_file)
        data = base64.b64decode(self.upload_file)
        with open(out_file,'wb') as file:
            file.write(data) 
        xl_workbook = xlrd.open_workbook(file.name)
        sheet_names = xl_workbook.sheet_names()
        sheetname = 'Sheet1'
        if not (sheetname in sheet_names):
            raise UserError(_('Worksheet with name "%s" does not exist' % sheetname))
        xl_sheet = xl_workbook.sheet_by_name(sheetname)
        #Number of Columns
        num_cols = xl_sheet.ncols
        #header
        headers = []
        for col_idx in range(0, num_cols):
            cell_obj = xl_sheet.cell(0, col_idx)
            headers.append(cell_obj.value)
        import_data = []
        for row_idx in range(1, xl_sheet.nrows):
            row_dict = {}
            for col_idx in range(0, num_cols):
                cell_obj = xl_sheet.cell(row_idx,col_idx)
                row_dict[headers[col_idx]] = cell_obj.value
            import_data.append(row_dict)
        
        if import_data:
            for row in import_data:
                #Check master product
                check_product = self.env['product.product'].search([('default_code','=',row['Item number'])])
                if not check_product:
                    raise UserError(_('Product %s does not exist in master data' % row['Item number']))
                else:
                    check_product = check_product[0]
                #Check master UoM
                check_uom = self.env['uom.uom'].search([('name','=',row['Unit'])])
                if not check_uom:
                    raise UserError(_('UoM %s does not exist in master data' % row['Unit']))
                else:
                    check_uom = check_uom[0]
                #                   0                   1                2               3             4             5                    6                    7                    8              9             10                11              12              13              14              15                 16                 17               18               19                20                 21
                #rowdata = [check_product.id,row['Item number'],row['Product  name'],check_uom.id,row['Unit'],row['Batch number'],row['Warehouse'],row['Best before date'],row['QTY Kirim'],row['NO IJ7'],row['Qty Mobil 7'],row['NO IJ8'],row['Qty Mobil 8'],row['NO IJ9'],row['Qty Mobil 9'],row['NO IJ10'],row['Qty Mobil 11'],row['NO IJ11'],row['Qty Mobil 12'],row['NO IJ12'],row['Qty Mobil 10'],row['Jml Palet']]
                ijno = _('%s%s%s%s%s%s' % (row['NO IJ7'],row['NO IJ8'],row['NO IJ9'],row['NO IJ10'],row['NO IJ11'],row['NO IJ12']))
                stock_picking = self.env['stock.picking'].search([('origin','=',ijno)])
                if not stock_picking:
                    stock_picking = stock_picking.create({
                        'partner_id': self.partner_id.id,
                        'picking_type_id': self.picking_type_id.id,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'origin': ijno
                    })
                else:
                    stock_picking = stock_picking[0]
                    if stock_picking.state in ['done','cancel']:
                        raise UserError(_('Stock Picking with Source Document %s already exist in the system with status %s, Source Document must be on other new value' % (ijno,stock_picking.state)))

                #mulai input data
                stock_move = stock_picking.move_lines.create({
                                    'name':row['Product  name'],
                                    'sequence':10,
                                    'company_id':stock_picking.company_id.id,
                                    'product_id': check_product.id,
                                    'product_uom': check_uom.id,
                                    #'product_qty': row['QTY Kirim'],
                                    'product_uom_qty': row['QTY Kirim'],
                                    'location_id': stock_picking.location_id.id,
                                    'location_dest_id': stock_picking.location_dest_id.id,
                                    'picking_type_id':stock_picking.picking_type_id.id,
                                    'picking_id':stock_picking.id
                                    })

                #Check Stock.production.lot
                #raise UserError(_('test: ijno = %s, Best before date = %s ' % (ijno,datetime(*xlrd.xldate_as_tuple(row['Best before date'], 0)))))
                check_lot = self.env['stock.production.lot'].search([('name','=',row['Batch number']),('product_id','=',check_product.id)])
                if not check_lot:
                    check_lot = self.env['stock.production.lot'].create({
                            'name': row['Batch number'],
                            'product_id': check_product.id,
                            'ref': ijno,
                            'use_date': datetime(*xlrd.xldate_as_tuple(row['Best before date'], 0))
                            })
                else:
                    check_lot = check_lot[0]

                qty_done = 0
                if self.fill_qty_done:
                    qty_done = row['QTY Kirim']

                stock_move.move_line_ids.create({
                        'picking_id': stock_picking.id,
                        'move_id': stock_move.id,
                        'product_id': check_product.id,
                        'product_uom_id': check_uom.id,
                        'product_uom_qty': row['QTY Kirim'],
                        'qty_done': qty_done,
                        'lot_id': check_lot.id,
                        'lot_name': row['Batch number'],
                        'location_id': stock_picking.location_id.id,
                        'location_dest_id': stock_picking.location_dest_id.id
                        })

    @api.one
    def import_format_inbound_wh(self):
        if not self.upload_file:
            raise UserError(_('Lookup xls excel file before upload'))
        mpath = get_module_path('import_excel_stockmove')
        out_file_name = 'inbound.xls'
        out_file = mpath + _('/tmp/' + out_file_name)
        #delete file if exist
        if os.path.exists(out_file):
            os.remove(out_file)
        data = base64.b64decode(self.upload_file)
        with open(out_file,'wb') as file:
            file.write(data) 
        xl_workbook = xlrd.open_workbook(file.name)
        sheet_names = xl_workbook.sheet_names()
        sheetname = 'Sheet1'
        if not (sheetname in sheet_names):
            raise UserError(_('Worksheet with name "%s" does not exist' % sheetname))
        xl_sheet = xl_workbook.sheet_by_name(sheetname)
        #Number of Columns
        num_cols = xl_sheet.ncols
        #header
        headers = []
        for col_idx in range(0, num_cols):
            cell_obj = xl_sheet.cell(0, col_idx)
            headers.append(cell_obj.value)
        import_data = []
        for row_idx in range(1, xl_sheet.nrows):
            row_dict = {}
            for col_idx in range(0, num_cols):
                cell_obj = xl_sheet.cell(row_idx,col_idx)
                row_dict[headers[col_idx]] = cell_obj.value
            import_data.append(row_dict)
        
        if import_data:
            for row in import_data:
                #Check master product
                product_no = row['PRODUCT CODE']
                if isinstance(product_no,int) or isinstance(product_no,float):
                    fractional, whole = math.modf(product_no)
                    if fractional == 0:
                        product_no = str(int(product_no))
                    else:
                        product_no = str(product_no)

                check_product = self.env['product.product'].search([('default_code','=',product_no)])
                if not check_product:
                    raise UserError(_('Product %s does not exist in master data' % product_no))
                else:
                    check_product = check_product[0]
                #Check master UoM
                check_uom = self.env['uom.uom'].search([('name','=',row['UOM'])])
                if not check_uom:
                    raise UserError(_('UoM %s does not exist in master data' % row['UOM']))
                else:
                    check_uom = check_uom[0]
                #                   0                   1                2               3             4             5                    6     
                #rowdata = [check_product.id,row['PRODUCT CODE'],row['PO NUMBER'],check_uom.id,row['UOM'],row['BATCH'],row['EXPIRED'],row['QTY']
                ijno = row['PO NUMBER']
                stock_picking = self.env['stock.picking'].search([('origin','=',ijno)])
                if not stock_picking:
                    stock_picking = stock_picking.create({
                        'partner_id': self.partner_id.id,
                        'picking_type_id': self.picking_type_id.id,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'origin': ijno
                    })
                else:
                    stock_picking = stock_picking[0]
                    if stock_picking.state in ['done','cancel']:
                        raise UserError(_('Stock Picking with Source Document %s already exist in the system with status %s, Source Document must be on other new value' % (ijno,stock_picking.state)))

                #mulai input data
                stock_move = stock_picking.move_lines.create({
                                    'name':check_product.name,
                                    'sequence':10,
                                    'company_id':stock_picking.company_id.id,
                                    'product_id': check_product.id,
                                    'product_uom': check_uom.id,
                                    #'product_qty': row['QTY Kirim'],
                                    'product_uom_qty': row['QTY'],
                                    'location_id': stock_picking.location_id.id,
                                    'location_dest_id': stock_picking.location_dest_id.id,
                                    'picking_type_id':stock_picking.picking_type_id.id,
                                    'picking_id':stock_picking.id
                                    })

                #Check Stock.production.lot
                #raise UserError(_('test: ijno = %s, Best before date = %s ' % (ijno,datetime(*xlrd.xldate_as_tuple(row['Best before date'], 0)))))
                batchno = row['BATCH']
                if isinstance(batchno,int) or isinstance(batchno,float):
                    fractional, whole = math.modf(batchno)
                    if fractional == 0:
                        batchno = str(int(batchno))
                    else:
                        batchno = str(batchno)

                check_lot = self.env['stock.production.lot'].search([('name','=',batchno),('product_id','=',check_product.id)])
                if not check_lot:
                    check_lot = self.env['stock.production.lot'].create({
                            'name': batchno,
                            'product_id': check_product.id,
                            'ref': ijno,
                            'use_date': datetime(*xlrd.xldate_as_tuple(row['EXPIRED'], 0))
                            })
                else:
                    check_lot = check_lot[0]

                qty_done = 0
                if self.fill_qty_done:
                    qty_done = row['QTY']
                
                stock_move.move_line_ids.create({
                        'picking_id': stock_picking.id,
                        'move_id': stock_move.id,
                        'product_id': check_product.id,
                        'product_uom_id': check_uom.id,
                        'product_uom_qty': row['QTY'],
                        'qty_done': qty_done,
                        'lot_id': check_lot.id,
                        'lot_name': batchno,
                        'location_id': stock_picking.location_id.id,
                        'location_dest_id': stock_picking.location_dest_id.id
                        })



    @api.one
    def import_format_outbound_customer(self):
        if not self.upload_file:
            raise UserError(_('Lookup xls excel file before upload'))
        mpath = get_module_path('import_excel_stockmove')
        out_file_name = 'inbound.xls'
        out_file = mpath + _('/tmp/' + out_file_name)
        #delete file if exist
        if os.path.exists(out_file):
            os.remove(out_file)
        data = base64.b64decode(self.upload_file)
        with open(out_file,'wb') as file:
            file.write(data) 
        xl_workbook = xlrd.open_workbook(file.name)
        sheet_names = xl_workbook.sheet_names()
        sheetname = 'Sheet1'
        if not (sheetname in sheet_names):
            raise UserError(_('Worksheet with name "%s" does not exist' % sheetname))
        xl_sheet = xl_workbook.sheet_by_name(sheetname)
        #Number of Columns
        num_cols = xl_sheet.ncols
        #header
        headers = []
        for col_idx in range(0, num_cols):
            cell_obj = xl_sheet.cell(0, col_idx)
            headers.append(cell_obj.value)
        import_data = []
        for row_idx in range(1, xl_sheet.nrows):
            row_dict = {}
            for col_idx in range(0, num_cols):
                cell_obj = xl_sheet.cell(row_idx,col_idx)
                row_dict[headers[col_idx]] = cell_obj.value
            import_data.append(row_dict)
        
        if import_data:
            for row in import_data:
                #Check master product
                product_no = row['Item number']
                if isinstance(product_no,int) or isinstance(product_no,float):
                    fractional, whole = math.modf(product_no)
                    if fractional == 0:
                        product_no = str(int(product_no))
                    else:
                        product_no = str(product_no)
                
                check_product = self.env['product.product'].search([('default_code','=',product_no)])
                if not check_product:
                    raise UserError(_('Product %s does not exist in master data' % product_no))
                else:
                    check_product = check_product[0]
                
                #Check master UoM
                check_uom = self.env['uom.uom'].search([('name','=',row['UOM'])])
                if not check_uom:
                    raise UserError(_('UoM %s does not exist in master data' % row['UOM']))
                else:
                    check_uom = check_uom[0]
                
                #Check Customer
                custno = row['Customer Internal Reference']
                check_cust = self.env['res.partner'].search([('ref','=',custno)])
                if not check_cust:
                    raise UserError(_('Customer Internal Reference %s does not exist in master data' % custno))
                else:
                    check_cust = check_cust[0]

                #                   0        1           2                  3               4                  5                 6           7              8                9                       10
                #rowdata = [check_uom.id,row['UOM'],check_product.id,row['Item number'],row['BU'],row['Pick quantity'],row['Batch number'],row['PLS'],row['Customer'],check_cust.id,row['Customer Internal Reference']
                ijno = row['PLS']
                stock_picking = self.env['stock.picking'].search([('origin','=',ijno)])
                if not stock_picking:
                    stock_picking = stock_picking.create({
                        'partner_id': check_cust.id,
                        'picking_type_id': self.picking_type_id.id,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'origin': ijno
                    })
                else:
                    stock_picking = stock_picking[0]
                    if stock_picking.state in ['done','cancel']:
                        raise UserError(_('Stock Picking with Source Document %s already exist in the system with status %s, Source Document must be on other new value' % (ijno,stock_picking.state)))

                #lokasi tidak perlu, karena systemnya akan otomatis cari
                ##Check Source Location Pick
                #check_loc = self.env['stock.location'].search([('complete_name','=ilike',_('%s%s' % ('%',row['BU'])))]) #complete_name
                #if not check_loc:
                #    raise UserError(_('Location %s does not exist in master data' % row['BU']))
                #else:
                #    check_loc = check_loc[0]

                #raise UserError(_('BU = %s, Check Location %s with id %s' % (row['BU'],check_loc.name,check_loc.id)))

                #mulai input data
                stock_move = stock_picking.move_lines.create({
                                    'name':check_product.name,
                                    'sequence':10,
                                    'company_id':stock_picking.company_id.id,
                                    'product_id': check_product.id,
                                    'product_uom': check_uom.id,
                                    #'product_qty': row['QTY Kirim'],
                                    'product_uom_qty': row['Pick quantity'],
                                    #'reserved_avaibility': 0,
                                    'location_id': stock_picking.location_id.id,
                                    'location_dest_id': stock_picking.location_dest_id.id,
                                    'picking_type_id':stock_picking.picking_type_id.id,
                                    'picking_id':stock_picking.id
                                    })

                
                # Check LOT

                #Check Stock.production.lot
                #raise UserError(_('test: ijno = %s, Best before date = %s ' % (ijno,datetime(*xlrd.xldate_as_tuple(row['Best before date'], 0)))))
                batchno = row['Batch number']
                if isinstance(batchno,int) or isinstance(batchno,float):
                    fractional, whole = math.modf(batchno)
                    if fractional == 0:
                        batchno = str(int(batchno))
                    else:
                        batchno = str(batchno)
                
                check_lot = self.env['stock.production.lot'].search([('name','=',batchno),('product_id','=',check_product.id)])
                if not check_lot:
                    raise UserError(_('Batch# %s on Product %s does not exist in master data' % (batchno,product_no)))
                else:
                    check_lot = check_lot[0]

                #qty_done = 0
                #if self.fill_qty_done:
                #    qty_done = row['Pick quantity']
                
                stock_move.move_line_ids.create({
                        'picking_id': stock_picking.id,
                        'move_id': stock_move.id,
                        'product_id': check_product.id,
                        'product_uom_id': check_uom.id,
                #        'product_uom_qty': row['Pick quantity'],
                #        'qty_done': qty_done,
                        'lot_id': check_lot.id,
                        'lot_name': batchno,
                        'location_id': stock_picking.location_id.id,
                        'location_dest_id': stock_picking.location_dest_id.id
                        })


                    
    @api.one
    def import_format_outbound_wh(self):
        if not self.upload_file:
            raise UserError(_('Lookup xls excel file before upload'))
        mpath = get_module_path('import_excel_stockmove')
        out_file_name = 'inbound.xls'
        out_file = mpath + _('/tmp/' + out_file_name)
        #delete file if exist
        if os.path.exists(out_file):
            os.remove(out_file)
        data = base64.b64decode(self.upload_file)
        with open(out_file,'wb') as file:
            file.write(data) 
        xl_workbook = xlrd.open_workbook(file.name)
        sheet_names = xl_workbook.sheet_names()
        sheetname = 'Sheet1'
        if not (sheetname in sheet_names):
            raise UserError(_('Worksheet with name "%s" does not exist' % sheetname))
        xl_sheet = xl_workbook.sheet_by_name(sheetname)
        #Number of Columns
        num_cols = xl_sheet.ncols
        #header
        headers = []
        for col_idx in range(0, num_cols):
            cell_obj = xl_sheet.cell(0, col_idx)
            headers.append(cell_obj.value)
        import_data = []
        for row_idx in range(1, xl_sheet.nrows):
            row_dict = {}
            for col_idx in range(0, num_cols):
                cell_obj = xl_sheet.cell(row_idx,col_idx)
                row_dict[headers[col_idx]] = cell_obj.value
            import_data.append(row_dict)
        
        if import_data:
            for row in import_data:
                #Check master product
                product_no = row['PRODUCT CODE']
                if isinstance(product_no,int) or isinstance(product_no,float):
                    fractional, whole = math.modf(product_no)
                    if fractional == 0:
                        product_no = str(int(product_no))
                    else:
                        product_no = str(product_no)

                check_product = self.env['product.product'].search([('default_code','=',product_no)])
                if not check_product:
                    raise UserError(_('Product %s does not exist in master data' % product_no))
                else:
                    check_product = check_product[0]
                
                #Check master UoM
                check_uom = self.env['uom.uom'].search([('name','=',row['UOM'])])
                if not check_uom:
                    raise UserError(_('UoM %s does not exist in master data' % row['UOM']))
                else:
                    check_uom = check_uom[0]
                
                #Check Customer
                custno = '' + row['CUSTOMER']
                check_cust = self.env['res.partner'].search([('ref','=',custno)])
                if not check_cust:
                    raise UserError(_('Customer Internal Reference %s does not exist in master data' % custno))
                else:
                    check_cust = check_cust[0]

                #                   0        1           2                  3               4                  5                 6           7              8                9                       10
                #rowdata = [check_uom.id,row['UOM'],check_product.id,row['Item number'],row['BU'],row['Pick quantity'],row['Batch number'],row['PLS'],row['Customer'],check_cust.id,row['Customer Internal Reference']
                ijno = row['PICKING NUMBER']
                stock_picking = self.env['stock.picking'].search([('origin','=',ijno)])
                if not stock_picking:
                    stock_picking = stock_picking.create({
                        'partner_id': check_cust.id,
                        'picking_type_id': self.picking_type_id.id,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'origin': ijno
                    })
                else:
                    stock_picking = stock_picking[0]
                    if stock_picking.state in ['done','cancel']:
                        raise UserError(_('Stock Picking with Source Document %s already exist in the system with status %s, Source Document must be on other new value' % (ijno,stock_picking.state)))

                #lokasi tidak perlu, karena systemnya akan otomatis cari
                ##Check Source Location Pick
                #check_loc = self.env['stock.location'].search([('complete_name','=ilike',_('%s%s' % ('%',row['LOCATION'])))]) #complete_name
                #if not check_loc:
                #    raise UserError(_('Location %s does not exist in master data' % row['LOCATION']))
                #else:
                #    check_loc = check_loc[0]

                #raise UserError(_('LOCATION = %s, Check Location %s with id %s' % (row['LOCATION'],check_loc.name,check_loc.id)))

                #mulai input data
                stock_move = stock_picking.move_lines.create({
                                    'name':check_product.name,
                                    'sequence':10,
                                    'company_id':stock_picking.company_id.id,
                                    'product_id': check_product.id,
                                    'product_uom': check_uom.id,
                                    #'product_qty': row['QTY Kirim'],
                                    'product_uom_qty': row['QTY'],
                                    #'reserved_avaibility': 0,
                                    'location_id': stock_picking.location_id.id,
                                    'location_dest_id': stock_picking.location_dest_id.id,
                                    'picking_type_id':stock_picking.picking_type_id.id,
                                    'picking_id':stock_picking.id
                                    })

                
                # Check LOT

                #Check Stock.production.lot
                #raise UserError(_('test: ijno = %s, Best before date = %s ' % (ijno,datetime(*xlrd.xldate_as_tuple(row['Best before date'], 0)))))
                batchno = row['Batch Number']
                if isinstance(batchno,int) or isinstance(batchno,float):
                    fractional, whole = math.modf(batchno)
                    if fractional == 0:
                        batchno = str(int(batchno))
                    else:
                        batchno = str(batchno)
                        
                check_lot = self.env['stock.production.lot'].search([('name','=',batchno),('product_id','=',check_product.id)])
                if not check_lot:
                    raise UserError(_('Batch# %s on Product %s does not exist in master data' % (batchno,product_no)))
                else:
                    check_lot = check_lot[0]

                #qty_done = 0
                #if self.fill_qty_done:
                #    qty_done = row['Pick quantity']
                
                stock_move.move_line_ids.create({
                        'picking_id': stock_picking.id,
                        'move_id': stock_move.id,
                        'product_id': check_product.id,
                        'product_uom_id': check_uom.id,
                #        'product_uom_qty': row['Pick quantity'],
                #        'qty_done': qty_done,
                        'lot_id': check_lot.id,
                        'lot_name': batchno,
                        'location_id': stock_picking.location_id.id,
                        'location_dest_id': stock_picking.location_dest_id.id
                        })