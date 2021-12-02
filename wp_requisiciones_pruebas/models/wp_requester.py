# -*- coding: utf-8 -*-

import re
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)

class Purchaserequester(models.Model):
    _name = 'purchase.requester'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Requisiciones WP'
    _rec_name = 'name_seq'
    _order = 'id desc'

    @api.model
    def create(self, vals):
        if vals.get('name_seq', 'Nuevo') == 'Nuevo':
            aa = vals['proyecto_nombre']
            bb = self.env['purchase.requester.proyecto'].browse(aa).proyecto_codigo
            cc = self.env['ir.sequence'].next_by_code('purchase.requester') or '/'
            vals['name_seq'] = bb + cc
        return super(Purchaserequester, self).create(vals)

    def unlink(self):
        for rec in self:
            if rec.state == 'rej' or rec.state == 'draft':
                return super(Purchaserequester, self).unlink()
            else:
                raise UserError(_('Para borar una requisición de compra, debe cencelarla primero.'))

    @api.depends()
    def action_toapprove(self):
        for rec in self:
            rec.state = 'con'
            rec.target = 'new'

    def action_approve(self):
        for rec in self:
            rec.state = 'acc'

    def action_reject(self):
        for rec in self:
            rec.state = 'rej'
            rec.req_aprobada_proy = False
            rec.req_aprobada_dis = False


    def action_com_prov(self):
        for rec in self:
            if rec.state == 'acc':
                rec.muestra_prov_can = True
                rec.muestra_prov_com = False

    def button_done(self):
        for rec in self:
            rec.state = 'done'

    def action_can_prov(self):
        for rec in self:
            if rec.state == 'acc':
                rec.muestra_prov_com = True
                rec.muestra_prov_can = False
        self.cancela_proveedores()

    def cancela_proveedores(self):
        self.proveedor_uno = self.proveedor_dos = self.proveedor_tres = False
        for line in self.purchase_order_line:
                line.prov_sel = line.precio_menor_uno = line.precio_menor_dos = line.precio_menor_tres = False
                line.price_unit = line.precio_prov_uno = line.precio_prov_dos = line.precio_prov_tres = 0.0


    def action_purchase(self):
        for rec in self:
            rec.state = 'con'
        self.ensure_one()
        if not self.purchase_order_line:
            raise ValidationError(_("No se puede mandar a Aprobación porque no hay partidas."))
        for line in self.purchase_order_line:
            if line.product_qty == 0:
                raise ValidationError(_("No se puede mandar a Aprobación sin especificar la Cantidad de la partida " + str(line.product_seq)+"."))
        """res_model_id = self.env['ir.model'].search([('name', '=', self._description)]).id
        self.env['mail.activity'].create([{'activity_type_id': 4,
                                           'date_deadline': datetime.today(),
                                           'summary': "Jefe Disciplina: Aprobación de Requisición",
                                           'user_id': self.jefe_disciplina.id,
                                           'res_id': self.id,
                                           'res_model_id': res_model_id,
                                           'note': 'Solicitud de aprobación de requisición',
                                           }])
        self.env['mail.activity'].create([{'activity_type_id': 4,
                                           'date_deadline': datetime.today(),
                                           'summary': "Jefe Proyecto: Aprobación de Requisición",
                                           'user_id': self.jefe_proyecto.id,
                                           'res_id': self.id,
                                           'res_model_id': res_model_id,
                                           'note': 'Solicitud de aprobación de requisición',
                                           }])"""

    def button_create(self, context=None):
        for rec in self:
            rec.state = 'acc'

        return {
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "views": [[False, "form"]],
            'view_type': 'form',
            'view_mode': 'form',
            'context': {'default_purchase_inhrt_id': self.jefe_disciplina.id,
                        'default_new_id': self.name_seq,
                        'default_purchase_requester_id': self.id,
                        'default_origin': self.name_seq,
                        },
        }

    def button_creates(self):
        if not self.purchase_order_line.prov_sel:
            raise ValidationError(_("Debe seleccionar al menos un proveedor en una partida para crear una Orden de Compra."))

        for rec in self:
            rec.state = 'acc'
            rec.muestra_prov_can = False

        if self.proveedor_uno and self.proveedor_uno in self.purchase_order_line.prov_sel:
            self._crea_po(self.proveedor_uno)

        if self.proveedor_dos and self.proveedor_dos in self.purchase_order_line.prov_sel:
            self._crea_po(self.proveedor_dos)

        if self.proveedor_tres and self.proveedor_tres in self.purchase_order_line.prov_sel:
            self._crea_po(self.proveedor_tres)

        self.cancela_proveedores()

    def _crea_po(self, prov=None):
        order_id = self.env['purchase.order'].create([{'purchase_inhrt_id': self.jefe_disciplina.id,
                                        'purchase_requester_id': self.id,
                                        'origin': self.name_seq,
                                        'partner_id': prov.id,
                                        'state': 'purchase',
                                       }]).id
        for line in self.purchase_order_line:
           if line.prov_sel == prov:
               name = line.product_id.display_name
               if line.product_id.description_purchase:
                   name += '\n' + line.product_id.description_purchase
               self.env['purchase.order.line'].create([{'product_seq': line.product_seq,
                                                       'order_id': order_id,
                                                       'product_id': line.product_id.id,
                                                       'name': name,
                                                       'p_marca': line.product_id.p_marca,
                                                       'p_modelo': line.product_id.p_modelo,
                                                       'p_serie': line.product_id.p_serie,
                                                       'product_qty': line.product_qty,
                                                       'price_unit': line.price_unit,
                                                       }])

    def button_convert(self):
        for rec in self:
            rec.state = 'draft'

    def button_cancel(self):
        for rec in self:
            if rec.order_count_sdp > 0 or rec.order_count_odc > 0:
                raise ValidationError(_("No se puede cancelar una requisición si tiene una SdP o una OdC vinculada."))
            rec.state = 'rej'
            rec.muestra_prov_com = False
            rec.muestra_prov_can = False
            rec.req_aprobada_proy = False
            rec.req_aprobada_dis = False

        self.cancela_proveedores()

    def button_approve_dis(self):
        for rec in self:
            if rec.req_aprobada_proy == True:
                rec.write({'state': 'acc'})
                rec.muestra_prov_com = False
                rec.req_aprobada_proy = False
                self.req_aprobada()
            else:
                rec.req_aprobada_dis = True

    def button_approve_proy(self):
        for rec in self:
            if rec.req_aprobada_dis == True:
                rec.write({'state': 'acc'})
                rec.muestra_prov_com = True
                rec.req_aprobada_dis = False
                self.req_aprobada()
            else:
                rec.req_aprobada_proy = True

    """def req_aprobada(self):
        for rec in self:
            if rec.state == 'acc':
                _logger.info("==> asi mero")"""

    def req_aprobada(self):
        """for rec in self:
            if rec.state == 'acc':
                for compradores in rec.proyecto_compradores:
                    res_model_id = self.env['ir.model'].search(
                        [('name', '=', self._description)]).id
                    self.env['mail.activity'].create([{'activity_type_id': 4,
                                                       'date_deadline': datetime.today(),
                                                       'summary': "Requisición aprobada",
                                                       'user_id': compradores.id,
                                                       'res_id': self.id,
                                                       'res_model_id': res_model_id,
                                                       'note': 'Requisición aprobada para dar continuidad a la compra',
                                                       }])"""

    proyecto_compradores = fields.Many2many('res.users', string='Compradores', related="proyecto_nombre.proyecto_compradores")

    jefe_disciplina = fields.Many2one('res.users', string='Jefe de Disciplina', related="disciplina_nombre.disciplina_lider", store=True)
    jefe_proyecto = fields.Many2one('res.users', string='Jefe de Proyecto', related="proyecto_nombre.proyecto_lider", store=True)
    description = fields.Text(string="Descripción", states={'acc': [('readonly', True)]}, tracking=True)
    date_order = fields.Datetime('Fecha de Solicitud', required=True, index=True, copy=False, default=datetime.today(), readonly=True)
    limit_date_order = fields.Datetime('Fecha de Límite de Solicitud', required=True, index=True, tracking=True, copy=False,
                             default=datetime.today(),
                             help="Representa la fecha en la que se debe validar la cotización y convertirla en una orden de compra.", states={'acc': [('readonly', True)],'done': [('readonly', True)]})
    user_id = fields.Many2one('res.users', string='Solicitante', index=True,default=lambda self: self.env.user, tracking=True)
    partner_id = fields.Many2one('res.partner', 'Vendor', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)

    purchase_order_id = fields.One2many('purchase.order', 'purchase_requester_id', string='Requisición ID', states={'acc': [('readonly', True)]} )
    res_id = fields.Many2one('res.users', string='User ID')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('con', 'Confirmación'),
        ('acc', 'Aceptado'),
        ('rej', 'Rechazado'),
        ('toapprove', 'Mandar a Aprobación'),
        ('app', 'Aprobar'),
        ('reject', 'Rechazar'),
        ('done', 'Hecho'),
    ], string='Estatus', default='draft', readonly=True, tracking=True)

    name_seq = fields.Char(string="Requisición", required=True, copy=False, readonly=True,  index=True, default=lambda self: _('Nuevo'))

    product_seq = fields.Integer(related='purchase_order_line.product_seq', string='No.', store=True)
    purchase_order_line = fields.One2many('purchase.requester.line', 'purchase_order_id',string='Partida', tracking=True)

    product_id = fields.Many2one('product.product', related='purchase_order_line.product_id', string="Producto/Servicio", tracking=True)
    product_qty = fields.Float(related='purchase_order_line.product_qty', string='Cantidad', tracking=True)
    product_udm = fields.Many2one('purchase.requester.line', related='purchase_order_line.product_udm', string='Unidad de Medida')
    product_marca = fields.Char(related='purchase_order_line.product_marca',string='Marca')
    product_modelo = fields.Char(related='purchase_order_line.product_modelo', string='Modelo')
    product_serie = fields.Char(related='purchase_order_line.product_serie', string='Serie')
    proyecto_nombre = fields.Many2one('purchase.requester.proyecto', string='Proyecto',  required=True, tracking=True)

    area_nombre = fields.Many2one('purchase.requester.area', string='Área', tracking=True)
    disciplina_nombre = fields.Many2one('purchase.requester.disciplina', string='Disciplina', required=True, tracking=True)
    tiporeq_nombre = fields.Many2one('purchase.requester.tiporeq', string='Tipo de Requisición', tracking=True)

    purchase_order_ids = fields.One2many('purchase.order', 'purchase_requester_id', string='Purchase Orders', tracking=True)
    order_count_odc = fields.Integer(compute='_compute_order_count_odc', string='Number of Orders')
    order_count_s_odc = fields.Char(compute='_compute_order_count_odc', string='Number of Orders')
    order_count_sdp = fields.Integer(compute='_compute_order_count_sdp', string='Number of Orders')
    order_count_s_sdp = fields.Char(compute='_compute_order_count_sdp', string='Number of Orders')

    proveedor_uno = fields.Many2one('res.partner', string='Proveedor 1', store=True, readonly=True)
    proveedor_dos = fields.Many2one('res.partner', string='Proveedor 2', store=True, readonly=True)
    proveedor_tres = fields.Many2one('res.partner', string='Proveedor 3', store=True, readonly=True)
    req_aprobada_proy = fields.Boolean(default=False)
    req_aprobada_dis = fields.Boolean(default=False)
    muestra_prov_com = fields.Boolean(default=False)
    muestra_prov_can = fields.Boolean(default=False)
    muestra_confirm = fields.Boolean(default=False)
    aplica_prov_uno = fields.Boolean(default=False)
    aplica_prov_dos = fields.Boolean(default=False)
    aplica_prov_tres = fields.Boolean(default=False)

    @api.onchange('aplica_prov_uno')
    def _onchange_aplica_prov_uno(self):
        if self.aplica_prov_uno == True:
            self.aplica_prov_dos = self.aplica_prov_tres = False
            for rec in self.purchase_order_line:
                rec.prov_sel = self.proveedor_uno
                rec.price_unit = rec.precio_prov_uno
        if not self.aplica_prov_uno and not self.aplica_prov_dos and not self.aplica_prov_tres:
            self.purchase_order_line.prov_sel = False

    @api.onchange('aplica_prov_dos')
    def _onchange_aplica_prov_dos(self):
        if self.aplica_prov_dos == True:
            self.aplica_prov_uno = self.aplica_prov_tres = False
            for rec in self.purchase_order_line:
                rec.prov_sel = self.proveedor_dos
                rec.price_unit = rec.precio_prov_dos
        if not self.aplica_prov_uno and not self.aplica_prov_dos and not self.aplica_prov_tres:
            self.purchase_order_line.prov_sel = False


    @api.onchange('aplica_prov_tres')
    def _onchange_aplica_prov_tres(self):
        if self.aplica_prov_tres == True:
            self.aplica_prov_uno = self.aplica_prov_dos = False
            for rec in self.purchase_order_line:
                rec.prov_sel = self.proveedor_tres
                rec.price_unit = rec.precio_prov_tres
        if not self.aplica_prov_uno and not self.aplica_prov_dos and not self.aplica_prov_tres:
            self.purchase_order_line.prov_sel = False


    @api.onchange('proveedor_uno')
    def _onchange_proveedor_uno(self, order='w'):
        for line_req in self.purchase_order_line:
            line_req.precio_prov_uno = 0.0
            for line_ord in order.order_line:
                if line_req.product_seq == line_ord.product_seq:
                    line_req.precio_prov_uno = line_ord.price_unit

    @api.onchange('proveedor_dos')
    def _onchange_proveedor_dos(self, order='w'):
        for line_req in self.purchase_order_line:
            line_req.precio_prov_dos = 0.0
            for line_ord in order.order_line:
                if line_req.product_seq == line_ord.product_seq:
                    line_req.precio_prov_dos = line_ord.price_unit


    @api.onchange('proveedor_tres')
    def _onchange_proveedor_tres(self, order='w'):
        for line_req in self.purchase_order_line:
            line_req.precio_prov_tres = 0.0
            for line_ord in order.order_line:
                if line_req.product_seq == line_ord.product_seq:
                    line_req.precio_prov_tres = line_ord.price_unit

    @api.onchange('proveedor_uno','proveedor_dos','proveedor_tres')
    def _onchange_proveedores(self):
        if self.proveedor_uno and self.proveedor_dos or self.proveedor_uno and self.proveedor_tres or self.proveedor_dos and self.proveedor_tres:
            if self.proveedor_uno == self.proveedor_dos or self.proveedor_uno == self.proveedor_tres or self.proveedor_dos == self.proveedor_tres:
                raise ValidationError(_("No se puede repetir el mismo proveedor."))
        for line in self.purchase_order_line:
            line.precio_menor_uno = line.precio_menor_dos = line.precio_menor_tres = False
            if line.precio_prov_uno > 0 and line.precio_prov_uno < line.precio_prov_dos and line.precio_prov_uno < line.precio_prov_tres or line.precio_prov_uno > 0 and line.precio_prov_uno < line.precio_prov_dos and not line.precio_prov_tres:
                line.precio_menor_uno = True
            if line.precio_prov_dos > 0 and line.precio_prov_dos < line.precio_prov_uno and line.precio_prov_dos < line.precio_prov_tres or line.precio_prov_dos > 0 and line.precio_prov_dos < line.precio_prov_uno and not line.precio_prov_tres:
                line.precio_menor_dos = True
            if line.precio_prov_tres > 0 and line.precio_prov_tres < line.precio_prov_uno and line.precio_prov_tres < line.precio_prov_dos:
                line.precio_menor_tres = True
            if line.prov_sel != self.proveedor_uno and line.prov_sel != self.proveedor_dos and line.prov_sel != self.proveedor_tres:
                line.prov_sel = False

    @api.depends('purchase_order_ids')
    def _compute_order_count_odc(self):
        for requisition in self:
            requisition.order_count_odc = 0
            requisition.order_count_s_odc = ''
            for rec in requisition.purchase_order_ids:
                if rec.state == 'purchase':
                    requisition.order_count_odc += 1
                    requisition.order_count_s_odc = str(requisition.order_count_odc)

    @api.depends('purchase_order_ids')
    def _compute_order_count_sdp(self):
        for requisition in self:
            requisition.order_count_sdp = 0
            requisition.order_count_s_sdp = ''
            for rec in requisition.purchase_order_ids:
                if rec.state != 'purchase':
                    requisition.order_count_sdp += 1
                    requisition.order_count_s_sdp = str(requisition.order_count_sdp)


    def action_purchase_requisition_list_pass(self):
        pass

    @api.onchange('purchase_order_line')
    def _onchange_purchase_order_line(self):
        cont = len(self.purchase_order_line)
        for x in range(cont-1):
            if self.purchase_order_line[cont-1].product_id == self.purchase_order_line[x].product_id:
                raise ValidationError(_("No se pueden repetir los productos en las partidas"))
