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
    is_technical = fields.Boolean('Technical Resquest',default=False)
    request_technical_id = fields.Many2one('res.users', string='Technical Responsible', index=True, tracking=True)

    def button_need_technical(self):
        """ Request Technical approval """
        for request in self:
            if not request.request_technical_id:
                raise UserError(_('Please specify a technical approval.'))
            request.is_technical = True
            request.stage_id = self.env.ref('semlex_purchase_resquest.purchase_request_stage_waiting_approval').id