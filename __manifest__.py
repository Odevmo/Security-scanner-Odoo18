{
    'name': 'Security Scanner Suite',
    'version': '1.0',
    'summary': 'Performs security scans on the Odoo instance.',
    'description': """
        This module allows administrators to perform basic security scans
        on their Odoo instance to check for essential security configurations.
    """,
    'website': 'https://github.com/Odevmo',
    'license': 'LGPL-3',
    'category': 'Security',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/security_scan_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}