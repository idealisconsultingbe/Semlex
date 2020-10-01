# -*- coding: utf-8 -*-

{
    'name': 'Web - chatter position',
    'version': '1.0',
    'category': 'Other',
    'summary': 'Add a button to systray to switch chatter position',
    'author': 'Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': [
        'mail',
    ],
    'price': 0,
    'currency': 'EUR',
    'data': [
        'views/assets.xml',
    ],
    'qweb': [
        "static/src/xml/chatter_position.xml",
    ],
    'installable': True,
}
