# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_purchase_approval = fields.Boolean(string='Purchase Order Step Approval')
    approval_type = fields.Selection([
        ('one_step', 'One Step'),
        ('multi_step', 'Multi-Step'),
    ], string='Approval Type', help='Purchase order approval type according to rules that apply. One-step: purchase orders should be approved by only one user, the highest rule applies. Multi-step: purchase orders should be approved by several users, rules apply from lowest rule to the highest.',
        default='one_step', config_parameter='purchase_approval.approval_type')
    tax_included = fields.Boolean(string='Taxes Included', config_parameter='purchase_approval.tax_included', help='Rules amount includes taxes.')

    @api.constrains('module_purchase_approval', 'po_order_approval')
    def _check_module_purchase_approval(self):
        for settings in self:
            if settings.module_purchase_approval and settings.po_order_approval:
                raise UserError(_('Configuration conflict: Purchase Order Approval and Purchase Order Step Approval settings'))
