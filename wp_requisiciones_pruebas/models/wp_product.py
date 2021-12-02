# -*- coding: utf-8 -*-

import re

from odoo import api, fields, models, tools, _
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError

class PurchaseProductTemplateInherit(models.Model):
    _inherit = "product.template"

    p_marca = fields.Char(string="Marca")
    p_modelo = fields.Char(string="Modelo")
    p_serie = fields.Char(string="Serie")
