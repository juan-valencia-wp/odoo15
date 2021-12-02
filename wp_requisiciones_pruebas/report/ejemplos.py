    """
    para imprimir todo se usa un boton:
      <button name="print_report" string="Print RFQ" type="object" states="draft" class="oe_highlight" groups="purchase.group_purchase_manager"/>
      también se puede usar así:
      <button name="%(action_report_request)d" string="Print RFQ" type="action" states="draft" class="oe_highlight" groups="purchase.group_purchase_manager"/>
    """


    """def print_report(self):
        data = {}
        docids = self.env['purchase.requester'].search([]).ids
        return self.env.ref('wp_requisiciones_pruebas.action_report_request').report_action(docids, data=data)"""


    """@api.model
    def onchange_seq(self):
        count = 0
        for rec in self:
            for line in rec.purchase_order_id:
                count += 1
                rec.update({'product_seq': count})"""

    """@api.depends('product_seq', 'product_id')
    def seq_and_name(self):
        for rec in self:
            rec.product_seq_name = rec.product_seq +' - '+ rec.product_id.name"""

    """
    @api.onchange('proveedor_uno','proveedor_dos','proveedor_tres')
    def _onchange_proveedorres(self):
        for line in self.purchase_order_line:
            for prov in line.product_id.seller_ids:
                if self.proveedor_uno == prov.name:
                    line.precio_prov_uno = prov.price
                if self.proveedor_dos == prov.name:
                    line.precio_prov_dos = prov.price
                if self.proveedor_tres == prov.name:
                    line.precio_prov_tres = prov.price


    @api.onchange('proveedor_uno')
    def _onchange_proveedor_uno(self):
        for line in self.purchase_order_line:
            for prov in line.product_id.seller_ids:
                if self.proveedor_uno == prov.name:
                    line.precio_prov_uno = prov.price

    @api.onchange('proveedor_dos')
    def _onchange_proveedor_dos(self):
        for line in self.purchase_order_line:
            for prov in line.product_id.seller_ids:
                if self.proveedor_dos == prov.name:
                    line.precio_prov_dos = prov.price

    @api.onchange('proveedor_tres')
    def _onchange_proveedor_tres(self):
        for line in self.purchase_order_line:
            for prov in line.product_id.seller_ids:
                if self.proveedor_tres == prov.name:
                    line.precio_prov_tres = prov.price

    """

    """
        message = {
           'type': 'ir.actions.client',
           'tag': 'display_notification',
           'params': {
               'title': _('Warning!'),
               'message': 'You cannot do this action now',
               'sticky': False,
           }
        }
        return message

    for record in self:
            return {
                "type": "ir.actions.act_window",
                "name": 'Comparando Proveedores',
                "res_model": "purchase.requester.line",
                "views": [(False, "list")],
                'view_type': 'list',
                'view_mode': 'list',
                'domain': [('purchase_order_id', '=', record.purchase_req_id)],
            }
    """
