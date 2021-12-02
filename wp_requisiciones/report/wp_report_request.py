# -*- coding: utf-8 -*-

import re

from odoo import api, fields, models, tools, _
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError

class report_request(models.AbstractModel):
    _name = 'report.wp_requisiciones.report_request'
    _description = ' Reportes de Requisiciones'

    def _get_report_values(self, docids, data=None):
        # get the report action back as we will need its data
        report = self.env['ir.actions.report']._get_report_from_name('wp_requisiciones.report_request')
        # get the records selected for this rendering of the report
        docs = self.env[report.model].browse(docids)
        # return a custom rendering context
        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': docs,
            'data': data,
        }
