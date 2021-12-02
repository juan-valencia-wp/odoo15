# -*- coding: utf-8 -*-
from odoo import api, fields, models, api, _
from datetime import datetime, time
from odoo.exceptions import AccessError, UserError, ValidationError

class Requesterorderline(models.Model):
    _name = 'purchase.requester.line'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Requester Order Line'

    product_seq = fields.Integer(string='No.', default=lambda self: 000)
    purchase_order_id = fields.Many2one('purchase.requester',string='Partida id')

    product_id = fields.Many2one('product.product', string="Producto/Servicio")
    product_udm_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_udm = fields.Many2one('uom.uom', string='Unidad de Medida', domain="[('category_id', '=', product_udm_category_id)]")
    product_qty = fields.Float(string='Cantidad')
    product_marca = fields.Char(related='product_id.p_marca', string='Marca')
    product_modelo = fields.Char(related='product_id.p_modelo', string='Modelo')
    product_serie = fields.Char(related='product_id.p_serie', string='Serie')
    price_unit = fields.Float(string="Precio")
    precio_prov_uno = fields.Float('Proveedor 1')
    precio_prov_dos = fields.Float('Proveedor 2')
    precio_prov_tres = fields.Float('Proveedor 3')
    precio_menor_uno = fields.Boolean(default=False)
    precio_menor_dos = fields.Boolean(default=False)
    precio_menor_tres = fields.Boolean(default=False)
    prov_sel = fields.Many2one('res.partner', string='Elegir proveedor')

    @api.onchange('product_id')
    def _product_id_change(self):
        if not self.product_id:
            return

        self.product_udm = self.product_id.uom_po_id or self.product_id.uom_id

    @api.onchange('prov_sel')
    def _onchange_field(self):
        if not self.prov_sel:
            return
        if self.prov_sel == self.purchase_order_id.proveedor_uno:
            self.price_unit = self.precio_prov_uno
        if self.prov_sel == self.purchase_order_id.proveedor_dos:
            self.price_unit = self.precio_prov_dos
        if self.prov_sel == self.purchase_order_id.proveedor_tres:
            self.price_unit = self.precio_prov_tres

    @api.model
    def create(self, vals):
        aa = str(vals['purchase_order_id'])
        self.env.cr.execute("SELECT MAX(product_seq) FROM purchase_requester_line WHERE purchase_order_id = "+aa+"; ")
        bb = self.env.cr.fetchall()
        for valor in bb:
            for vv in valor:
                if vv:
                    cc = int(vv) + 1
                else:
                    cc = 1
        vals['product_seq'] = int(cc)
        return super(Requesterorderline, self).create(vals)

    def _prepare_requester_order_line(self, name, product_qty=0.0, price_unit=0.0, product_seq=0, p_marca='w', p_modelo='w', p_serie='w', taxes_id = 'w'):
        self.ensure_one()
        requisition = self.purchase_order_id
        if requisition.limit_date_order:
            date_planned = requisition.limit_date_order
        else:
            date_planned = datetime.now()

        return {
            'name': name,
            'product_id': self.product_id.id,
            'date_planned': date_planned,
            'price_unit': price_unit,
            'product_uom': self.product_udm,
            'product_qty': product_qty,
            'product_seq': product_seq,
            'p_marca': p_marca,
            'p_modelo': p_modelo,
            'p_serie': p_serie,
            'taxes_id': taxes_id,
        }
