# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, _
from odoo.tools.misc import get_lang


class PurchaseRequestLine(models.Model):
    _name = 'purchase.request.line'
    _description = 'Purchase Request Line'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'purchase_request_id, sequence, id'

    def _default_expected_date(self):
        return fields.Date.today() + timedelta(days=7)

    def _default_product_uom(self):
        uom = self.env.ref('uom.product_uom_unit', False)
        if uom:
            return uom.id
        return None

    name = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    date_expected = fields.Date(string='Expected Date', index=True, required=True, tracking=True, default=_default_expected_date, help='When request products should be received.')
    date_reminder = fields.Date(string='Reminder Date', compute='_compute_date_reminder', help='One week before expected date.')
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default="1.0")
    product_uom_qty = fields.Float(string='Total Quantity', compute='_compute_product_uom_qty', store=True, help='Product quantity according to specified unit of measure.')
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]", default=_default_product_uom)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)])
    product_type = fields.Selection(related='product_id.type', readonly=True)
    price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price')
    purchase_request_id = fields.Many2one('purchase.request', string='Purchase Request', index=True, required=True, ondelete='cascade')
    date_request = fields.Date(related='purchase_request_id.date_request', string='Request Date', readonly=True)
    readonly_request_stage = fields.Boolean(related='purchase_request_id.readonly_stage', string='Is Fields Edition Forbidden')
    company_id = fields.Many2one(related='purchase_request_id.company_id', string='Company')
    request_stage_id = fields.Many2one(related='purchase_request_id.stage_id', string='Request Stage', store=True, tracking=True)
    technical_stage_name = fields.Char(related='request_stage_id.technical_name', string='Technical Stage Name', store=True, help='Utility field used in UI.')
    partner_id = fields.Many2one('res.partner', string='Vendor', tracking=True)
    order_id = fields.Many2one('purchase.order', string='Purchase Order', tracking=True, index=True, readonly=True)
    order_state = fields.Selection(related='order_id.state', string='Purchase Order Status')
    order_reception_date = fields.Date(string='Order Reception Date', compute='_compute_order_reception_date', help='Reception date of move lines linked to this product and purchase order.')
    attachment_number = fields.Integer(string='Number of Attachments', compute='_compute_attachment_number')
    display_type = fields.Selection([
        ('line_section', 'Section'),
        ('line_note', 'Note')], default=False, help='Technical field for UX purpose.')
    product_available = fields.Float(related='product_id.free_qty')
    product_qty_to_order = fields.Float(string="Qty to order", compute='_compute_qty_to_order',inverse='_set_qty_to_order', store=True)

    def _set_qty_to_order(self):
        return True

    @api.depends('product_qty', 'product_available','product_id','order_id')
    def _compute_qty_to_order(self):
        for line in self :
            # type po = order all quantity
            if line.purchase_request_id.request_type_id.operation_type == 'po':
                line.product_qty_to_order = line.product_qty
            # type po_stock = order only not available quantity
            elif line.purchase_request_id.request_type_id.operation_type == 'po_stock':
                line.product_qty_to_order = max(line.product_qty - line.product_available,0)

            # type so or line already purchase = order nothing
            if line.order_id or line.purchase_request_id.request_type_id.operation_type == 'so':
                line.product_qty_to_order = 0

    @api.depends('product_uom', 'product_qty', 'product_id.uom_id')
    def _compute_product_uom_qty(self):
        for line in self:
            if line.product_id and line.product_id.uom_id != line.product_uom:
                line.product_uom_qty = line.product_uom._compute_quantity(line.product_qty, line.product_id.uom_id)
            else:
                line.product_uom_qty = line.product_qty

    def _compute_order_reception_date(self):
        """ Get last purchase order product reception """
        for line in self:
            pickings = self.env['stock.picking'].search([('purchase_id', '=', line.order_id.id)])
            move_line = self.env['stock.move.line'].search(
                [('picking_id', 'in', pickings.ids), ('product_id', '=', line.product_id.id), ('qty_done', '>=', 1.0)],
                limit=1, order='date DESC')
            line.order_reception_date = move_line.date or False

    def _compute_attachment_number(self):
        """ Get number of attached documents """
        # Model.read_group(domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True)
        # fields (list) – list of fields present in the list view specified on the object.
        # groupby (list) – list of groupby descriptions by which the records will be grouped.
        attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'purchase.request.line'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for line in self:
            line.attachment_number = attachment.get(line.id, 0)

    @api.depends('date_expected')
    def _compute_date_reminder(self):
        """ Compute expected date minus one week """
        for line in self:
            line.date_reminder = (line.date_expected - timedelta(days=7)) if line.date_expected else False

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """
        -   Dynamic domain for product_uom field
        -   Product description if product_id is set else False
        """
        for line in self:
            res = {}
            if line.product_id:
                line.product_uom = line.product_id.uom_po_id or line.product_id.uom_id
                product_lang = line.product_id.with_context(
                    lang=get_lang(self.env, self.env.user.lang).code,
                    company_id=self.company_id.id,
                )
                line.name = line._get_product_purchase_description(product_lang)
                res['domain'] = {'product_uom': [('category_id', '=', line.product_uom_category_id.id)], }
            else:
                line.name = False
                res['domain'] = {'product_uom': [], }
            return res

    def _get_product_purchase_description(self, product_lang):
        """ standard method in purchase order line model """
        self.ensure_one()
        name = product_lang.display_name
        if product_lang.description_purchase:
            name += '\n' + product_lang.description_purchase

        return name

    def name_get(self):
        """ overwritten method """
        return [(line.id, '{}, {}'.format(line.purchase_request_id.ref, line.product_id.name if line.product_id else line.description)) for line in self]

    def action_get_attachment_view(self):
        """ Add context and domain to attachment action """
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'purchase.request.line'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'purchase.request.line', 'default_res_id': self.id}
        return res

    def button_convert(self):
        """ Convert a purchase request line into a purchase order """
        for line in self:
            self.env['purchase.order'].action_create_purchase_order([line.id])
