# -*- coding: utf-8 -*-
{
    'name': "Purchase Order Approval",
    'summary': "Manage Purchase Orders Approvals",
    'description': """
        This module allows users to add several rules in order to approve a purchase order. Those rules are triggered if a specific amount is reached 
        and approval from a specific user is expected.
    """,
    'author': "DWA - Idealis Consulting",
    'website': "http://www.idealisconsulting.com",
    'category': 'Operations/Purchase',
    'version': '13.0.0.1',
    'depends': ['hr', 'purchase', 'purchase_approval_settings'],
    'data': [
        'data/mail_template_data.xml',
        'views/purchase_order_views.xml',
        'views/purchase_approval_rule_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
