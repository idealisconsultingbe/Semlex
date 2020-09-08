# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PurchaseRequestStage(models.Model):
    _name = 'purchase.request.stage'
    _description = 'Purchase Request Stage'
    _order = 'sequence, name, id'
    _sql_constraints = [
        ('unique_stage_name', 'unique(name)',
         _('This stage name is already in use. Please make sure you assign a unique name to this stage.')),
    ]

    name = fields.Char(string='Stage Name', required=True, translate=True)
    technical_name = fields.Char(string='Technical Name', readonly=True, help='Utility field used in business logic.')
    is_statusbar_disabled = fields.Boolean(string='Disabled Statusbar', help='Used to prevent stage change by clicking on statusbar.')
    is_readonly = fields.Boolean(string='Readonly Mode', help='Used to prevent field edition.')
    sequence = fields.Integer(string='Sequence', default=5, help='Used to order stages. Lower is better.')
    fold = fields.Boolean(string='Folded in Pipeline', help='This stage is folded in kanban view.')
