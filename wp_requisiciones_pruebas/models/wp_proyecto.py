# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError

class WPProyectos(models.Model):
    _name = "purchase.requester.proyecto"
    _order = 'proyecto_codigo'
    _description = 'Proyectos'
    _rec_name = 'proyecto_nombre'

    proyecto_nombre = fields.Char(string='Nombre',  required=True)
    proyecto_codigo = fields.Char(string='Código', required=True,  index=True)
    proyecto_lider = fields.Many2one('res.users', string='Encargado/Líder')
    proyecto_compradores = fields.Many2many('res.users', string='Compradores')
    proyecto_fecha_inicio = fields.Date('Fecha de inicio')
    proyecto_cliente = fields.Many2one('res.partner', string='Cliente', domain="[('category_id.name','ilike', 'Cliente')]")
    proyecto_obra = fields.Char(string='Obra')
    proyecto_no_contrato = fields.Integer(string='No. Contrato')
    proyecto_localizacion = fields.Char(string='Localización')

class WPAreas(models.Model):
    _name = "purchase.requester.area"
    _description = 'Áreas'
    _rec_name = 'area_nombre'

    area_nombre = fields.Char(string='Nombre')
    area_codigo = fields.Char(string='Código')
    area_lider = fields.Many2one('res.users', string='Encargado/Líder')
    area_proyecto = fields.Many2one('purchase.requester.proyecto', string='Proyecto')

class WPDisciplinas(models.Model):
    _name = "purchase.requester.disciplina"
    _description = 'Disciplinas'
    _rec_name = 'disciplina_nombre'

    disciplina_nombre = fields.Char(string='Nombre')
    disciplina_codigo = fields.Char(string='Código')
    disciplina_lider = fields.Many2one('res.users', string='Encargado/Líder')
    disciplina_proyecto = fields.Many2one('purchase.requester.proyecto', string='Proyecto')

class WPTipoReqisicion(models.Model):
    _name = "purchase.requester.tiporeq"
    _description = 'Tipo de Requisición'
    _rec_name = 'tiporeq_nombre'

    tiporeq_nombre = fields.Char(string='Nombre')
    tiporeq_codigo = fields.Char(string='Código')
