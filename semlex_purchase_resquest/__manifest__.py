# -*- coding: utf-8 -*-
{
    'name': 'Semlex Purchase Request',
    'version': '13.0.1.0.0',
    'summary': """Additional features for idealis module purchase_request""",
    'description': 'Additional features for idealis module purchase_request',
    'category': 'Purchase',
    'author': 'Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['base','purchase_request'],
    'data': [
        'data/purchase_request_stage_data.xml',
        'data/mail_template_data.xml',
        'view/product_view.xml',
        'view/res_config_settings_views.xml',
        'view/purchase_request_views.xml',
    ],
    'images': [],
    'license': 'LGPL-3',
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
