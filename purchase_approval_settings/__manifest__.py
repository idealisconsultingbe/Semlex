# -*- coding: utf-8 -*-
{
    'name': "Purchase Approval Settings",
    'summary': "Manage Settings of Purchase Approval Module",
    'description': """
        This module adds purchase settings for purchase approval module. It allows user to choose between one-step or multi-step type of approval
        and if taxes should be included in logic or not. 
        - one-step approval: only one user must approve a purchase order
        - multi-step approval: several users must approve a purchase order
    """,
    'author': "DWA - Idealis Consulting",
    'website': "http://www.idealisconsulting.com",
    'category': 'Operations/Purchase',
    'version': '13.0.0.1',
    'depends': ['purchase'],
    'data': ['views/res_config_settings_views.xml', ],
    'installable': True,
}