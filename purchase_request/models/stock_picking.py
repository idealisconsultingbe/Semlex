# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'stock.picking'

    request_ids = fields.One2many('purchase.request', 'picking_id', string='Purchase Request', readonly=True)

    @api.model
    def action_create_stock_picking(self, request):
        """
        Create a stock picking from purchase request for deliver to user
        """
        self.env['stock.picking'].check_lines_compatibility(request.request_line_ids)
        product_lines = request.request_line_ids.filtered(lambda request_line: request_line.product_id)
        if product_lines:
            vals = {
                    'picking_type_id': request.request_type_id.stock_picking_type_id.id,
                    # 'request_ids': request.id,
                    'origin': request.ref,
                    'partner_id':request.user_id.partner_id.id,
                    'location_id': request.request_type_id.stock_picking_type_id.default_location_src_id.id,
                    'location_dest_id': request.request_type_id.stock_picking_type_id.default_location_dest_id.id,
                }
            picking_id = self.env['stock.picking'].create(vals)

            for line in product_lines:
                self.env['stock.move'].create({
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_qty,
                    'product_uom': line.product_id.uom_id.id,
                    'picking_id': picking_id.id,
                    # 'delivery_date': line.date_expected,
                    'location_id': picking_id.location_id.id,
                    'location_dest_id': picking_id.location_dest_id.id})
            picking_id.action_assign()
            return picking_id

    @api.model
    def check_lines_compatibility(self, lines):
        if not lines:
            raise UserError(_('You cannot create a stock picking: at least one purchase request line is required.'))
        if any(line.technical_stage_name in ('cancelled', 'draft','confirmed') for line in lines):
            raise UserError(_('You cannot create a stock picking: at least one purchase request line is in Draft, Confirm or Cancelled stage.'))
        if any(line.purchase_request_id.picking_id for line in lines):
            raise UserError(_('You cannot create a stock picking: there is already an picking for at least one purchase request line.'))
        if len(lines.mapped('company_id')) > 1:
            raise UserError(_('You cannot create a stock picking: there are purchase request lines with different companies.'))
        if not lines.mapped('product_id'):
            raise UserError(_('You cannot create a stock picking: at least one purchase resquest line should have a product.'))
