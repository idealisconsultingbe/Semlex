# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import date


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    manager_id = fields.Many2one('res.users', string='Default Manager', config_parameter='purchase_request.manager_id')


