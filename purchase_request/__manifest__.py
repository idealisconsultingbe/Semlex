# -*- coding: utf-8 -*-
{
    'name': "Purchase Request",
    'summary': "Manage Purchase Order Requests",
    'description': """
        This module allows users to make requests for products. Those requests may generate a purchase order. 
    """,
    'sequence': 70,
    'author': "DWA - Idealis Consulting",
    'website': "http://www.idealisconsulting.com",
    'category': 'Operations/Purchase',
    'version': '13.0.0.1',
    'depends': ['hr', 'purchase', 'stock'],
    'data': [
        'security/purchase_request_security.xml',
        'security/ir.model.access.csv',
        'data/purchase_request_stage_data.xml',
        'data/purchase_request_data.xml',
        'views/res_config_settings_views.xml',
        'views/purchase_order_views.xml',
        'views/purchase_request_line_views.xml',
        'views/purchase_request_tag_views.xml',
        'views/purchase_request_type_views.xml',
        'views/purchase_request_views.xml',
    ],
    'installable': True,
    'application': True,
}