# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import date


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    iso_mail_template_id = fields.Many2one('mail.template', string='ISO Email templates',
                                           config_parameter='semlex_purchase_request.iso_mail_template_id')

