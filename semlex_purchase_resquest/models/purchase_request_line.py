# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, _
from odoo.tools.misc import get_lang


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    request_technical_id = fields.Many2one('res.users', string='Technical Responsible', index=True, tracking=True)
    technical_approval = fields.Boolean('Technical Approve', readonly=True, default=False)
    request_technical_stage_name = fields.Char(related='purchase_request_id.technical_stage_name', string='Technical Stage Name', store=True, help='Utility field used in UI.')
    technical_approve_visible = fields.Boolean(compute='get_technical_approve_visible')

    def get_technical_approve_visible(self):
        """
        :param self:
        :return:
        """
        for request_line in self :
            request_line.technical_approve_visible = self.env.user == request_line.request_technical_id

    def button_tech_validation(self):
        """ Technical Approval """
        for request_line in self:
            request_line.technical_approval = True
            # If all line technical validated - change purchase request status
            request_line_to_validate = request_line.purchase_request_id.request_line_ids.filtered(lambda l: len(l.request_technical_id) != 0 and l.technical_approval == False)
            if not request_line_to_validate:
                request_line.purchase_request_id.stage_id = self.env.ref('purchase_request.purchase_request_stage_approved').id

    @api.onchange('product_id')
    def _onchange_product_id_update_tech_manager(self):
        for line in self:
            # assign technical manager if exist in product category
            if line.product_id.categ_id.technical_manager_id:
                line.request_technical_id = line.product_id.categ_id.technical_manager_id.id


