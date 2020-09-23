# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    one_step_approval_button_visible = fields.Boolean(string='One-Step Approval Button Visibility',
                                                      compute='_compute_approval_buttons_visibility', help='Utility field to handle one-step approval button visibility.')
    multi_step_approval_button_visible = fields.Boolean(string='Multi-Step Approval Button Visibility',
                                                        compute='_compute_approval_buttons_visibility', help='Utility field to handle multi-step button visibility.')
    purchase_approval_ids = fields.One2many('purchase.approval', 'purchase_order_id', string='Approvals Required')
    state = fields.Selection(selection_add=[('step_approval', 'Waiting for approval'), ('purchase',)])

    @api.depends('purchase_approval_ids')
    def _compute_approval_buttons_visibility(self):
        """ Compute approval buttons visibility """
        for order in self:
            approval = order._get_first_unapproved_rule()
            if approval:
                approval_type = self.env['ir.config_parameter'].sudo().get_param('purchase_approval.approval_type')
                visibility = any(self.env.user.id == user.id for user in approval.responsible_ids.mapped('user_id'))
                order.one_step_approval_button_visible = visibility if approval_type == 'one_step' else False
                order.multi_step_approval_button_visible = visibility if approval_type == 'multi_step' else False
            else:
                order.multi_step_approval_button_visible = False
                order.one_step_approval_button_visible = False

    def button_confirm(self):
        """ Overridden method without modifying super behavior

        Bypass super behavior if there are approval rules which apply. In that case order state is set to 'waiting for approval'
        and responsible are notified """
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            approval_type = self.env['ir.config_parameter'].sudo().get_param('purchase_approval.approval_type')
            tax_included = self.env['ir.config_parameter'].sudo().get_param('purchase_approval.tax_included')
            if approval_type:
                rules = self.env['purchase.approval.rule'].search([('approval_amount', '<=',
                                                                    order.amount_total if tax_included
                                                                    else order.amount_untaxed)])
                if rules:
                    if approval_type == 'one_step':
                        # get the rule with the highest amount
                        rules = rules.sorted(key=lambda rule: rule.approval_amount, reverse=True)
                        order.purchase_approval_ids = order.create_approval(rules[0])
                    else:
                        # get all rules in ascending order
                        rules = rules.sorted(key=lambda rule: rule.approval_amount, reverse=False)
                        order.purchase_approval_ids = order.create_approval(rules)
                    order.write({'state': 'step_approval'})
                    order._notify_approval_responsible()
                    return True
            return super(PurchaseOrder, order).button_confirm()

    def _notify_approval_responsible(self):
        """ Write a request for approval notification according to current rule and delegate mailing to purchase approval """
        for order in self:
            approval = order._get_first_unapproved_rule()
            if approval:
                responsible = approval.responsible_ids.name if len(approval.responsible_ids) == 1 \
                    else approval.approval_rule_id.job_id.name if approval.approval_rule_id.job_id \
                    else approval.approval_rule_id.approval_responsible
                body = _('Waiting for {} approval').format(responsible)
                subject = _('Approval Required')
                self.message_post(body=body,
                                   subject=subject,
                                   message_type='notification',
                                   subtype_id=self.env.ref('mail.mt_note').id)
                approval.send_mail_responsible()

    def _get_first_unapproved_rule(self):
        """ Retrieve first unapproved rule which approval status is not true from approval rules list """
        for approval in self.purchase_approval_ids:
            if not approval.approval_status:
                return approval

    def one_step_approve(self):
        """ Approve an order in one step """
        current_approval = self._get_first_unapproved_rule()
        current_approval.write({'approval_status': True})
        self.button_approve()
        return {}

    def approve_cancel(self):
        super(PurchaseOrder, self).button_cancel()

    def multi_step_approve(self):
        """ Approve a step from multi-step approval order """
        current_approval = self._get_first_unapproved_rule()
        current_approval.write({'approval_status': True})
        next_approval = self._get_first_unapproved_rule()
        if not next_approval:
            self.button_approve()
        else:
            # if there are remaining steps to approve, notify next responsible from approval rules list
            self._notify_approval_responsible()
            self.write({'date_approve': fields.Date.context_today(self)})
        return {}

    def create_approval(self, rules):
        """ Create approval rules to apply to current order """
        approvals = self.env['purchase.approval']
        for rule in rules:
            approvals += self.env['purchase.approval'].create({
                'purchase_order_id': self.id,
                'approval_rule_id': rule.id,
            })
        return approvals
