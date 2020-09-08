# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError

AVAILABLE_PRIORITIES = [
    ('0', 'Low'),
    ('1', 'Medium'),
    ('2', 'High'),
    ('3', 'Very High'),
]


class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Purchase Request'
    _order = 'deadline_date, priority desc, id'
    _rec_name = 'ref'

    def _default_stage_id(self):
        """ get default stage id """
        return self.env['purchase.request.stage'].search([('name', '=', 'Draft')], order='sequence', limit=1).id

    @api.depends('user_id')
    def _get_request_responsible(self):
        """ get request responsible id """
        responsible_id = False
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.user_id.id)], order='sequence', limit=1)
        if employee_id:
            responsible_id = employee_id.parent_id
        return responsible_id

    ref = fields.Char(string='Reference', index=True, default='New')
    user_id = fields.Many2one('res.users', string='Request Representative', index=True, tracking=True,
                              default=lambda self: self.env.user, required=True, check_company=True)
    request_responsible_id = fields.Many2one('res.users', string='Request Responsible', index=True, tracking=True,
                                             required=True, compute="_get_request_responsible")
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', ondelete='set null',
                                          domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                          check_company=True,
                                          help='Analytic account to which this request is linked for financial management.')
    owner_id = fields.Many2one('res.users', string='Request Owner', index=True, tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    priority = fields.Selection(AVAILABLE_PRIORITIES, string='Priority', default=AVAILABLE_PRIORITIES[0][0], tracking=True)
    tag_ids = fields.Many2many('purchase.request.tag', 'purchase_request_tag_rel', 'purchase_request_id', 'tag_id', string='Tags')
    stage_id = fields.Many2one('purchase.request.stage', string='Stage', ondelete='restrict', tracking=True,
                               group_expand='_read_group_stage_ids', default=lambda self: self._default_stage_id())
    technical_stage_name = fields.Char(related='stage_id.technical_name', string='Technical Stage Name', store=True, help='Utility field used in UI.')
    readonly_stage = fields.Boolean(string='Is Fields Edition Forbidden', related='stage_id.is_readonly', help='Utility field used to prevent field edition if request stage is readonly.')
    disabled_statusbar = fields.Boolean(string='Is StatusBar Disabled', related='stage_id.is_statusbar_disabled', help='Utility field used to prevent statusbar usage.')
    request_line_ids = fields.One2many('purchase.request.line', 'purchase_request_id', string='Purchase Request Lines')
    date_request = fields.Date(string='Request Date', required=True, index=True, default=fields.Date.today, readonly=1)
    date_confirm = fields.Date(string='Confirmation Date', readonly=True, index=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id.id)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company.id)
    line_count = fields.Integer(string='Request Lines Count', compute='_compute_line_count')
    deadline_date = fields.Date(string='Nearest Expected Date', compute='_compute_deadline_date', store=True, help='Nearest expected date from all lines linked to this request.')
    remaining_days = fields.Integer(compute='_compute_remaining_days', string="Remaining Days", store=True, help='Remaining days before deadline.')
    color = fields.Integer(string='Color Index', default=0)
    button_convert_visibility = fields.Boolean(string='Convert To Purchase Order Button Visibility', compute='_compute_button_convert_visibility', help='Utility field used to handle convert to purchase button visibility.')

    @api.depends('request_line_ids')
    def _compute_line_count(self):
        """ Compute number of lines in a purchase request """
        line_data = self.env['purchase.request.line'].read_group([('purchase_request_id', 'in', self.ids)], ['purchase_request_id'], ['purchase_request_id'])
        result = dict((data['purchase_request_id'][0], data['purchase_request_id_count']) for data in line_data)
        for request in self:
            request.line_count = result.get(request.id, 0)

    def _compute_remaining_days(self):
        """
        Compute remaining days before deadline.
        Remaining days are not stored and should be re-calculated every time
        a view use them (depends no required). Due to this, it is not possible to merge this method with
        deadline compute method
        """
        for request in self:
            days = 0
            if request.deadline_date:
                days = (request.deadline_date - fields.Date.today()).days + 1
            request.remaining_days = days

    @api.depends('request_line_ids')
    def _compute_button_convert_visibility(self):
        """
        Flag shoud be set to True if:
        - there are no request lines bound to a purchase order
        - there is at least one request line with a product and a vendor
        """
        for request in self:
            if request.request_line_ids.filtered(lambda line: line.order_id):
                request.button_convert_visibility = False
            elif request.request_line_ids.filtered(lambda line: line.partner_id and line.product_id):
                request.button_convert_visibility = True
            else:
                request.button_convert_visibility = False

    @api.depends('request_line_ids')
    def _compute_deadline_date(self):
        """ Compute nearest deadline : deadline which occurs first from all line deadlines"""
        for request in self:
            nearest_deadline = False
            if request.request_line_ids:
                nearest_deadline = min(request.request_line_ids.mapped('date_expected'))
            request.deadline_date = nearest_deadline

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Method used in group_expand attribute of stage field.
        Display all stages in kanban view, regardless they are being used """
        # perform search with private implementation of search() method, allowing specifying the uid to use for the access right check.
        # This is useful for example when filling in the selection list for a drop-down and avoiding access rights errors,
        stage_ids = stages._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    @api.model
    def create(self, vals):
        """ Overridden method
        Add purchase request reference from existing sequence.
        If sequence does not exist, a new sequence should be created.
        """
        if vals.get('ref', 'New') == 'New':
            sequence = self.env['ir.sequence'].next_by_code("purchase.request") or self._create_seq().next_by_code('purchase.request')
            vals.update({'ref': sequence})
        res = super(PurchaseRequest, self).create(vals)
        return res

    def write(self, vals):
        """
        Creators should not be able to change stage to another stage than 'Confirmed'. ir.rules prevent write if current stage
        is different than 'Draft' but it is still possible to change the current stage for any other stage. This is not what is expected.
        Creators can move from 'Draft' to 'Confirmed' and that's all.
        """
        if vals.get('stage_id'):
            stage = self.env['purchase.request.stage'].browse(vals.get('stage_id'))
            if stage.technical_name != 'confirmed':
                allowed_groups = self.env['res.groups'].search([('category_id', '=', self.env.ref('base.module_category_operations_purchase').id)])
                allowed_groups = allowed_groups - self.env.ref('purchase_request.purchase_request_group_creator')
                check_groups = any(group_id in allowed_groups for group_id in self.env.user.groups_id)
                if not check_groups:
                    raise UserError(_('You cannot move this request to {} stage (creators are only allowed to confirm draft requests.').format(stage.name))
        return super(PurchaseRequest, self).write(vals)

    def _create_seq(self):
        """ Create a new sequence """
        vals = {
            'name': 'Purchase Request Sequence',
            'code': 'purchase.request',
            'implementation': 'standard',
            'prefix': 'RFQ',
            'padding': 5,
            'company_id': self.env.company.id
        }
        return self.env['ir.sequence'].create(vals)

    def _message_order_created(self, order):
        """
        Post message notification in case of conversion to purchase order.
        :param order: a purchase order
        """
        action_id = str(self.env.ref('purchase.purchase_order_action_generic').id)
        menu_id = str(self.env.ref('purchase.menu_purchase_root').id)
        url = '<a href="/web?#id={}&action={}&model=purchase.order&view_type=form&menu_id={}">{}</a>'.format(order.id, action_id, menu_id, order.name)
        msg = _('A purchase order {} has been created ').format(url)
        subject = _('Purchase Order Created')
        self.message_post(body=msg,
                          subject=subject,
                          message_type='notification',
                          subtype_id=self.env.ref('mail.mt_note').id)

    def button_assign(self):
        """ Assign request to current user """
        for request in self:
            request.owner_id = self.env.user.id

    def button_convert(self):
        """ Convert a purchase request into a purchase order """
        for request in self:
            res = self.env['purchase.order'].action_create_purchase_order(request.request_line_ids.mapped('id'))
            request._message_order_created(res)

    def button_draft(self):
        """ Change stage to draft """
        for request in self:
            request.stage_id = self.env.ref('purchase_request.purchase_request_stage_draft').id

    def button_confirm(self):
        """ Change stage to confirmed """
        for request in self:
            request.date_confirm = fields.Datetime.now()
            request.stage_id = self.env.ref('purchase_request.purchase_request_stage_confirmed').id

    def button_cancel(self):
        """ Change stage to cancelled """
        for request in self:
            request.stage_id = self.env.ref('purchase_request.purchase_request_stage_cancelled').id
