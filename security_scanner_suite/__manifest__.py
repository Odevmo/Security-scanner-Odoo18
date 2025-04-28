# -*- coding: utf-8 -*-
{
    'name': 'Security Scanner Suite',
    'version': '1.0',
    'summary': 'Automated security diagnostics for Odoo instances.',
    'description': 'Provides automated diagnostics on critical security configurations and summarizes the results in a clear, actionable report.',
    'author': 'Odevmo',
    'website': 'https://github.com/Odevmo',
    'category': 'Tools',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/security_scan_views.xml',
        'data/security_scan_sequence.xml',
    ],
    'images': [
        'static/description/thumbnail.png'
    ],
    "description": """
            Security Scanner Suite for Odoo
            ================================
            Developer: Odevmo - Odoo Security Specialist
            
            Secure your Odoo instance with confidence. This module provides automated security diagnostics including:
            
            - Master Password Validation
            - HTTPS Enforcement
            - Access Rule Verification
            - Logging Configuration Check
            - Database Filtering
            - Database Listing Control
            
            Simple UI. One-click Scans. Clean Results.
            Future AI-driven insights and CVE detection coming soon.
    """,
    'installable': True,
    'application': True,
    'auto_install': False,
}