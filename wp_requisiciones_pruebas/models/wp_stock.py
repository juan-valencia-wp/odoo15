# -*- coding: utf-8 -*-

import re

from odoo import api, fields, models, tools, _
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError

class StockWarehouseInherit(models.Model):
    _inherit = "stock.warehouse"

    almacen_proyecto = fields.Many2one('purchase.requester.proyecto', string="Proyecto")
    almacen_area = fields.Many2one('purchase.requester.area', string="Área")

class StockPickingInherit(models.Model):
    _inherit = "stock.picking"

    ban_recepciones = fields.Boolean(default=True)
    ban_salidas = fields.Boolean(default=True)
    doc_origen = fields.Many2one('purchase.order', string='Orden de Compra')
    image_1920 = fields.Image(string='Foto empleado', related='partner_id.image_1920')
    supervisor = fields.Many2one('res.partner', 'Supervisor', check_company=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})



    @api.onchange('picking_type_id', 'origin')
    def _onchange_picking_type_id_inherit(self):
        if not self.origin and self.picking_type_id.code == 'incoming':
            self.ban_recepciones = False
        else:
            self.ban_recepciones = True
            order_lines = []
            self.move_ids_without_package = order_lines.clear()
            self.doc_origen = order_lines.clear()

        if self.picking_type_id.code == 'outgoing':
            self.ban_salidas = False
        else:
            self.ban_salidas = True
            order_lines = []
            self.supervisor = order_lines.clear()


    """@api.onchange('doc_origen')
    def _onchange_doc_origen(self):
        if not self.doc_origen:
            return
        self.purchase_id = self.doc_origen"""

    @api.onchange('doc_origen')
    def _onchange_doc_origen(self):
        if not self.doc_origen:
            order_lines = []
            self.move_ids_without_package = order_lines.clear()
            return

        self.purchase_id = self.doc_origen
        immediate_transfer = False
        self = self.with_company(self.company_id)
        purchase = self.purchase_id

        # Create PO lines if necessary
        order_lines = []
        self.move_ids_without_package = order_lines.clear()

        for line in purchase.order_line:
            # Compute name
            name = line.product_id.display_name
            description = line.product_id.description_pickingin

            # Compute quantity and price_unit
            if line.product_uom != line.product_id.uom_po_id:
                product_qty = line.product_uom._compute_quantity(line.product_qty, line.product_id.uom_po_id)
            else:
                product_qty = line.product_qty

            # Create PO line
            order_line_values = line._prepare_requester_stock_line(
                name=name, product_qty=product_qty, description=description)
            #order_lines.append((0, 0, order_line_values))
            order_lines.append((0, 0, order_line_values))
        self.move_ids_without_package = order_lines
        order_lines.clear()

class StockMoveInherit(models.Model):
    _inherit = 'purchase.order.line'

    def _prepare_requester_stock_line(self, name, product_qty=0.0, description='w'):
        self.ensure_one()

        return {
            'name': name,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_po_id.id,
            'product_uom_qty': product_qty,
            'description_picking': description,
        }
