# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    def get_valid_technical_visible(self):
        """
        :param self:
        :return:
        """
        self.valid_technical_visible = self.env.user == self.request_technical_id

    valid_technical_visible = fields.Boolean(compute='get_valid_technical_visible')
    request_technical_id = fields.Many2one('res.users', string='Technical Responsible', index=True, tracking=True)
    is_iso_impact = fields.Boolean('Request with ISO impacts',default=False,copy=False)

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


    def button_need_technical(self):
        """ Request Technical approval """
        for request in self:
            if not request.request_technical_id:
                raise UserError(_('Please specify a technical approval.'))
            request.stage_id = self.env.ref('semlex_purchase_resquest.purchase_request_stage_waiting_approval').id

    def button_tech_approved(self):
        """ Technical approval """
        for request in self:
            request.button_approved()