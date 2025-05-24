# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Approvals - Expenses',
    'version': '1.0',
    'category': 'Human Resources/Approvals',
    'description': """
This module adds to the approvals workflow the possibility to generate
expense sheets from an approval request for expenses.
    """,
    'depends': ['approvals', 'hr_expense'],  # Updated dependency
    'data': [
        'data/approval_category_data.xml',
        'data/mail_templates.xml',
        'views/approval_category_views.xml',
        'views/approval_product_line_views.xml',
        'views/approval_request_views.xml',
    ],
    'demo': [
        'security/ir.model.access.csv',
        'data/approval_demo.xml',  # Ensure this file is updated for expenses
    ],
    'installable': True,
    'auto_install': True,
    'license': 'OEEL-1',
}
