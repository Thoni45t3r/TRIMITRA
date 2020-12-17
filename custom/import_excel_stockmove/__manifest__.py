{
    'name': 'Import Excel for Receipt',
    'version': '12',
    'summary': 'Import data from excel and create receipt line',
    'description': """
Imort Excel Data into Receipt Line.
===================================
User mendapat file excel dari partner, file tersebut berisi data sku yang perlu di import di receipt line.
    """,
    'author': 'Ahmad Heriyanto',
    'website': 'https://id.linkedin.com/in/ahmadheriyanto',
    'category': 'Custom',
    'sequence': 0,
    'depends': ['base',
                'stock',
                'product_expiry',
                'fleet',
                ],
    'demo': [],
    'data': [
        #'views/import_format_inbound_customer.xml',
        'views/import_Format_Inbound_WH.xml',
        #'views/import_format_outbound_customer.xml',
        'views/import_format_outbound_wh.xml',
        'views/inventory.xml',
    ],
    'installable': True,
    'application': True,
}