# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'WP Requisiciones',
    'version': '14.0.1.0.0',
    'category': 'Inventory/Purchase',
    'summary': 'Módulo para solicitud de requisiciones',
    'description': "",
    'author': "Ignacio Valencia",
    'website': 'https://equiposwp.com',
    'depends': ['account','purchase','stock','purchase_stock','hr'],
    "license": "AGPL-3",
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/wp_purchase.xml',
        'views/wp_requester.xml',
        'views/wp_area.xml',
        'views/wp_disciplina.xml',
        'views/wp_product.xml',
        'views/wp_proyecto.xml',
        'views/wp_requester_order_line.xml',
        'views/wp_stock.xml',
        'views/wp_tiporeq.xml',
        'report/wp_report_purchase_addfields.xml',
        'report/wp_report_request.xml',
        'report/wp_reports.xml',
    ],
    'images': ['static/description/icon.png'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'assets': {
        'web.assets_backend': [
            '/wp_requisiciones/static/src/js/hello_world.js',
        ],
        'web.assets_qweb': [
            '/wp_requisiciones/static/src/css/requester.css',
        ],
    },
}
