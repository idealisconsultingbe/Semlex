# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    is_iso_impact = fields.Boolean('Request with ISO impacts',default=False,copy=False)
    user_technical_to_approve_ids = fields.Many2many('res.users', string='Technical Responsible to Approve',
                                                     compute='_compute_technical_to_approve',store=True)

    @api.depends('request_line_ids.technical_approval','request_line_ids.technical_stage_name')
    def _compute_technical_to_approve(self):
        """Technical user who must yet approve request"""
        self.user_technical_to_approve_ids = False
        for request in self.filtered(lambda r: r.technical_stage_name == 'waiting_technical'):
            line_top_approve = request.request_line_ids.filtered(lambda l: l.request_technical_id != False and l.technical_approval == False)
            manager_to_approve = line_top_approve.mapped("request_technical_id")
            request.user_technical_to_approve_ids = manager_to_approve

    def button_confirm(self):
        """ Send mail for ISO impacts """
        for request in self:
            super(PurchaseRequest, self).button_confirm()
            if request.is_iso_impact:
                config_mail_template = int(self.env['ir.config_parameter'].sudo().get_param('semlex_purchase_request.iso_mail_template_id'))
                if config_mail_template :
                    template = self.env['mail.template'].browse(config_mail_template)
                    email_values = {
                        }
                    template.sudo().send_mail(request.id, force_send=True, email_values=email_values)
                else:
                    raise UserError(_('Please define a ISO mail template in the configuration.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Purchase Requests'),
            'res_model': 'purchase.request',
            'view_mode': 'kanban,tree,form',
            'target': 'main',
              }

    def button_approved(self):
        """ Request Manager approval - add waiting technical step"""
        for request in self:
            request_line_to_technical = request.request_line_ids.filtered(lambda l: l.request_technical_id.id != False and l.technical_approval == False)
            if not request_line_to_technical:
                request.stage_id = self.env.ref('purchase_request.purchase_request_stage_approved').id
            else :
                request.stage_id = self.env.ref('semlex_purchase_resquest.purchase_request_stage_waiting_approval').id

        return {
            'type': 'ir.actions.act_window',
            'name': _('Purchase Requests'),
            'res_model': 'purchase.request',
            'view_mode': 'kanban,tree,form',
            'target': 'main',
              }