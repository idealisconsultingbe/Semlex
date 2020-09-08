# -*- coding: utf-8 -*-
from odoo import fields, models


class PurchaseApprovalRule(models.Model):
    """ Purchase Approval Rule is a generic rule that is applied on any purchase above
        a specific amount. """
    _name = 'purchase.approval.rule'
    _description = 'Approval Rule of Purchase Orders'
    _rec_name = 'rule_name'

    def _default_approval_type(self):
        return self.env['ir.config_parameter'].sudo().get_param('purchase_approval.approval_type')

    def _default_tax_included(self):
        return self.env['ir.config_parameter'].sudo().get_param('purchase_approval.tax_included')

    approval_type = fields.Selection([
        ('one_step', 'One Step'),
        ('multi_step', 'Multi-Step'),
    ], string="Approval Type", compute='_compute_approval_type', default=_default_approval_type, help='Purchase order approval type.')
    tax_included = fields.Boolean(string='Taxes Included', compute='_compute_tax_included', default=_default_tax_included)
    rule_name = fields.Char(string='Rule Name')
    approval_amount = fields.Monetary(string='Minimum Amount', currency_field='company_currency_id', help='This is the minimal amount an order should reached in order to apply this rule.')
    approval_responsible = fields.Selection([
        ('position', 'Job Position'),
        ('manager', 'Manager'),
        ('manager+1', 'Manager +1'),
        ('employee', 'Employee'),
    ], string='Approval Responsible', default='manager', help='Responsible of purchase order approval.')
    job_id = fields.Many2one('hr.job', string='Job Position')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    company_id = fields.Many2one('res.company', string='Company', compute='_compute_company_id', store=True)
    company_currency_id = fields.Many2one('res.currency', string='Company Currency', related='company_id.currency_id',
                                          help='Utility field to express amount currency.')
    purchase_approval_ids = fields.One2many('purchase.approval', 'approval_rule_id', string='Approvals')

    def _compute_company_id(self):
        """ Retrieve company id from env at rule creation """
        for rule in self:
            rule.company_id = self.env.company

    def _compute_approval_type(self):
        """ Retrieve information from config about approval type (one or multi step approval) """
        for rule in self:
            rule.approval_type = self.env['ir.config_parameter'].sudo().get_param('purchase_approval.approval_type')

    def _compute_tax_included(self):
        """ Retrieve information from config about tax calculation (taxes included or not) """
        for rule in self:
            rule.tax_included = self.env['ir.config_parameter'].sudo().get_param('purchase_approval.tax_included')
