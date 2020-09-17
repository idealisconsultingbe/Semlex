# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    @api.depends('user_id')
    def _get_request_responsible(self):
        """ get request responsible id """
        for request in self:
            employee_id = request.env['hr.employee'].search([('user_id', '=', request.user_id.id)], limit=1)
            if employee_id.parent_id:
                request.request_responsible_id = employee_id.parent_id.user_id
            else:
                request.request_responsible_id = False

    confirm_visible = fields.Boolean(compute='get_confirm_visible')
    request_responsible_id = fields.Many2one('res.users', string='Request Responsible', index=True, tracking=True,
                                             required=True, compute="_get_request_responsible")
