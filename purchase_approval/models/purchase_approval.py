# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PurchaseApproval(models.Model):
    """ Purchase Approval is an intermediate model used to link Purchase Orders and Approval Rules.
        This model computes approval responsible according to rule settings and mail them when their approval is required. """
    _name = 'purchase.approval'
    _description = 'Approval of Purchase Orders'
    _rec_name = 'purchase_order_id'

    responsible_ids = fields.Many2many('hr.employee', 'approval_employee_rel', 'employee_id', string='Approval Responsible', compute='_compute_rule_responsible')
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', required=True)
    approval_rule_id = fields.Many2one('purchase.approval.rule', string='Approval Rule', required=True)
    approval_status = fields.Boolean(string='Approval Status')

    @api.depends('approval_rule_id', 'purchase_order_id')
    def _compute_rule_responsible(self):
        """ Retrieve approval responsible according to applied rule """
        for approval in self:
            employee = approval.purchase_order_id.user_id.employee_id
            responsible = {
                'position': self.env['hr.employee'].search([('job_id', '=', approval.approval_rule_id.job_id.id)]),
                'manager': employee.parent_id if employee.parent_id else employee,
                'manager+1': employee.parent_id.parent_id if employee.parent_id.parent_id else employee.parent_id if employee.parent_id else employee,
                'employee': approval.approval_rule_id.employee_id,
            }
            # if dict value does not exist, default value is the purchase representative
            approval.write({'responsible_ids': responsible.get(approval.approval_rule_id.approval_responsible, employee).mapped('id')})

    def send_mail_responsible(self):
        """ Send mail to each responsible.
        Context is updated with information about responsible and current purchase order
        in order to fill the mail template """
        template = self.env.ref('purchase_approval.purchase_approval_request_mail_template')
        view_context = dict(self._context)
        view_context.update({
            'menu_id': str(self.env.ref('purchase.menu_purchase_root').id),
            'action_id': str(self.env.ref('purchase_approval.purchase_order_action').id),
            'dbname': self.env.cr.dbname,
        })

        mails_to_send = self.env['mail.mail']
        for approval in self:
            if not approval.approval_status:
                for responsible in approval.responsible_ids:
                    if responsible.work_email:
                        view_context.update({
                            'po_id': approval.purchase_order_id.id,
                            'email_to': responsible.work_email,
                            'employee_name': responsible.name,
                        })
                        mail_id = template.with_context(view_context).send_mail(approval.id, notif_layout='mail.mail_notification_light')
                        current_mail = self.env['mail.mail'].browse(mail_id)
                        mails_to_send |= current_mail

        if mails_to_send:
            mails_to_send.send()
