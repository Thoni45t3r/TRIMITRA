{
    'name': "Invoice Report Custom",
    'version': '12.0.0.0.1',
    'summary': """Invoice Custom""",
    'description': """Merubah Layout Invoice Doc Printout""",
    'category': 'Accounting',
    'author': 'Ahmad Heriyanto',
    'company': 'Nikisae',
    'maintainer': 'Ahmad Heriyanto',
    'website': "https://id.linkedin.com/in/ahmadheriyanto ",
    'depends': ['base', 'account', 'sale'],
    'data': [
        "views/account_invoice_contact.xml",
        "report/invoice_template_custom.xml",
    ],
    'images': [],
    'license': "AGPL-3",
    'installable': True,
    'application': False,
}
