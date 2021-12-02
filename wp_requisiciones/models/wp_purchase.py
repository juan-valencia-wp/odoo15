# -*- coding: utf-8 -*-

import re

from odoo import api, fields, models, tools, _
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError

class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    @api.model
    def _getUserGroupId(self):
        return [('groups_id', '=', self.env.ref('purchase.group_purchase_manager').id)]

    jefe_disciplina = fields.Many2one(
        'res.users', string='Aprobador', domain=_getUserGroupId, readonly=True)
    purchase_inhrt_id = fields.Many2one(
        'res.users', string='Aprobador',  store=True, readonly=False)
    purchase_requester_id = fields.Many2one('purchase.requester', string='Requisición')
    purchase_req_id = fields.Integer(related='purchase_requester_id.id', string='purchase_req_id')

    proyecto_nombre = fields.Many2one('purchase.requester.proyecto', related='purchase_requester_id.proyecto_nombre', string='Proyecto')
    area_nombre = fields.Many2one('purchase.requester.area', related='purchase_requester_id.area_nombre', string='Área', readonly=True)
    disciplina_nombre = fields.Many2one('purchase.requester.disciplina', related='purchase_requester_id.disciplina_nombre', string='Disciplina', readonly=True)
    tiporeq_nombre = fields.Many2one('purchase.requester.tiporeq', related='purchase_requester_id.tiporeq_nombre', string='Tipo de Requisición', readonly=True)

    @api.onchange('purchase_requester_id')
    def _onchange_purchase_requester_id(self):
        if not self.purchase_requester_id:
            self.origin = ''
            self.order_line = False
            return

        self = self.with_company(self.company_id)
        requisition = self.purchase_requester_id

        if not self.origin or requisition.name_seq not in self.origin.split(', '):
            if self.origin:
                if requisition.name_seq:
                    self.origin = requisition.name_seq
            else:
                self.origin = requisition.name_seq
        self.notes = requisition.description

        # Create PO lines if necessary
        order_lines = []
        self.order_line = order_lines.clear()

        for line in requisition.purchase_order_line:
            # Compute name
            name = line.product_id.display_name
            if line.product_id.description_purchase:
                name += '\n' + line.product_id.description_purchase

            # Compute quantity and price_unit
            """if line.product_udm != line.product_id.uom_po_id:
                product_qty = line.product_udm._compute_quantity(line.product_qty, line.product_id.uom_po_id)
                price_unit = line.product_udm._compute_price(line.price_unit, line.product_id.uom_po_id)
            else:
                product_qty = line.product_qty
                price_unit = line.product_id.standard_price"""
            product_qty = line.product_qty
            price_unit = line.product_id.standard_price

            taxes_id = line.product_id.taxes_id

            # Create PO line
            order_line_values = line._prepare_requester_order_line(
                name=name, product_qty=product_qty, price_unit=price_unit, product_seq = line.product_seq, p_marca = line.product_id.p_marca, p_modelo = line.product_id.p_modelo, p_serie = line.product_id.p_serie, taxes_id = taxes_id)
            order_lines.append((0, 0, order_line_values))
        self.order_line = order_lines
        order_lines.clear()

    @api.onchange('partner_id')
    def _onchange_partner_id_sdp(self):
        order_line = self.order_line
        for line in order_line:
            nom_prov = line.partner_id
            for line_prov in line.product_id.seller_ids:
                if nom_prov == line_prov.name:
                    line.price_unit = line_prov.price
                else:
                    line.price_unit = line.product_id.standard_price

    def action_comparar_provedores(self):
        for rec in self:
            if rec.state == 'cancel':
                raise ValidationError(_("No se pueden elegir SdP's canceladas."))
        self.purchase_requester_id.proveedor_uno = self.purchase_requester_id.proveedor_dos = self.purchase_requester_id.proveedor_tres = self.purchase_requester_id.aplica_prov_uno = self.purchase_requester_id.aplica_prov_dos = self.purchase_requester_id.aplica_prov_tres = False
        if len(self) <= 3:
            cont = 1
            for order in self:
                order.purchase_requester_id.action_com_prov()
                if cont == 1:
                    self.purchase_requester_id.proveedor_uno = order.partner_id
                    order.purchase_requester_id.purchase_order_line.precio_prov_dos = order.purchase_requester_id.purchase_order_line.precio_prov_tres = 0.0
                    order.purchase_requester_id._onchange_proveedor_uno(order)
                if cont == 2:
                    self.purchase_requester_id.proveedor_dos = order.partner_id
                    order.purchase_requester_id._onchange_proveedor_dos(order)
                if cont == 3:
                    self.purchase_requester_id.proveedor_tres = order.partner_id
                    order.purchase_requester_id._onchange_proveedor_tres(order)
                order.purchase_requester_id._onchange_proveedores()
                cont += 1
            action = self.env.ref('wp_requisiciones.purchase_form_action_inherit')
            message = {
               'type': 'ir.actions.client',
               'tag': 'display_notification',
               'params': {
                   'title': _('¡Tabla Creada!'),
                   'message': 'Regresa a la requisición %s para comparar proveedores',
                   'sticky': False,
                   'target': 'current',
                   'links': [{
                       'label': self.purchase_requester_id.name_seq,
                       'url': f'#id={self.purchase_requester_id.id}&action={action.id}&model=purchase.requester&view_type=form',
                   }],
               },
            }
            return message
        else:
            raise ValidationError(_("Solo se pueden elegir MÁXIMO TRES Solicitudes de presupuesto a comparar."))

class PurchaseOrderLineInherit(models.Model):
    _inherit = "purchase.order.line"


    @api.onchange("price_unit")
    def _onchange_field_price_unit(self):
        for prov in self.product_id.seller_ids:
            if self.partner_id == prov.name and self.price_unit > prov.price:
                print("=====> si estra")
                message =  {
                    'type': 'ir.actions.client',
                    'tag': 'display_price_notification',
                    'params': {
                       'title': _('¡Precio alto!'),
                       'message': 'Regresa a la requisición para comparar proveedores',
                    },
                }
                return message

    purchase_order_id = fields.Integer( related='order_id.purchase_req_id', string='Partida id', store=True)
    #no_partida = fields.Many2one('purchase.requester.line', string='Partida', domain="[('purchase_order_id','=', purchase_order_id)]", store=True)
    product_seq = fields.Integer(string='No.', default=lambda self: 000)
    p_marca = fields.Char(string="Marca")
    p_modelo = fields.Char(string="Modelo")
    p_serie = fields.Char(string="Serie")
