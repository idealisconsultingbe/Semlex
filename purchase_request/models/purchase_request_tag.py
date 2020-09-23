# -*- coding: utf-8 -*-
from odoo import fields, models, _


class PurchaseRequestTag(models.Model):
    _name = 'purchase.request.tag'
    _description = 'Purchase Request Tag'
    _sql_constraints = [
        ('tag_name_unique', 'unique (name)', _('Tag name already exists.')),
    ]

    name = fields.Char(string='Tag Name', required=True, translate=True)
    color = fields.Integer(string='Color Index', help='0=Grey / 1=Red / 2=Orange / 3=Yellow / 4=Blue / 5=Purple / 6=Pink / 7=Cyan / 8=Dark Blue / 9=Magenta / 10=Green / 11=Grape / 12=White')
