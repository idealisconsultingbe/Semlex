# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    request_line_ids = fields.One2many('purchase.request.line', 'order_id', string='Purchase Request Lines', readonly=True)

    @api.model
    def action_create_purchase_order(self, line_ids):
        """
        Create a purchase order from purchase request lines
        -   lines without product and vendor are skipped
        -   if there is no line with a product and a vendor, purchase order is not created
        Purchase request lines should not :
        - have different vendors,
        - be related to a different order,
        - be in draft or cancelled stage
        """
        lines = self.env['purchase.request.line'].browse(line_ids)
        self.env['purchase.order'].check_lines_compatibility(lines)
        product_lines = lines.filtered(lambda request_line: request_line.product_id and request_line.partner_id
                                       and request_line.product_qty_to_order != 0)
        if product_lines:
            origins = set(product_lines.mapped('purchase_request_id.ref'))
            order = self.env['purchase.order'].search([('state', '=', 'draft'),
                                                       ('partner_id', '=', product_lines.mapped('partner_id').id),
                                                       ('company_id', '=', product_lines.mapped('company_id').id)],
                                                      order="create_date DESC", limit=1)
            if order:
                if order.origin:
                    origins.update(order.origin.split(', '))
                order.write({'origin': ', '.join(list(origins)), 'request_line_ids': order.request_line_ids.ids + product_lines.ids})
            else:
                vals = {
                    'company_id': product_lines.mapped('company_id').id,
                    'currency_id': self.env.company.currency_id.id,
                    'partner_id': product_lines.mapped('partner_id').id,
                    'user_id': self.env.user.id,
                    'request_line_ids': product_lines.ids,
                    'origin': ', '.join(list(origins)),
                }
                order = self.env['purchase.order'].create(vals)
            for line in product_lines:
                vals = {
                    'name': line.name or line.product_id.name,
                    'order_id': order.id,
                    'product_qty': line.product_qty_to_order,
                    'product_id': line.product_id and line.product_id.id or False,
                    'product_uom': line.product_uom and line.product_uom.id or line.product_id.uom_po_id.id,
                    'price_unit': line.price_unit or 0.0,
                    'company_id': line.company_id.id,
                    'date_planned': line.date_expected,
                    'display_type': line.display_type,
                    'account_analytic_id': line.purchase_request_id.analytic_account_id.id or False,
                }
                self.env['purchase.order.line'].create(vals)
            return order

    @api.model
    def check_lines_compatibility(self, lines):
        if not lines:
            raise UserError(_('You cannot create a purchase order: at least one purchase request line is required.'))
        if any(line.technical_stage_name in ('cancelled', 'draft','confirmed') for line in lines):
            raise UserError(_('You cannot create a purchase order: at least one purchase request line is in Draft, Confirm or Cancelled stage.'))
        if any(line.order_id for line in lines):
            raise UserError(_('You cannot create a purchase order: there is already an order for at least one purchase request line.'))
        if len(lines.mapped('partner_id')) > 1:
            raise UserError(_('You cannot create a purchase order: there are purchase request lines with different vendors.'))
        if len(lines.mapped('company_id')) > 1:
            raise UserError(_('You cannot create a purchase order: there are purchase request lines with different companies.'))
        if not lines.mapped('partner_id'):
            raise UserError(_('You cannot create a purchase order: at least one purchase resquest line should have a vendor.'))
        if not lines.mapped('product_id'):
            raise UserError(_('You cannot create a purchase order: at least one purchase resquest line should have a product.'))
