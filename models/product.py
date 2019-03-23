# -*- coding: utf-8 -*-

from odoo import models, fields, api

class product(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'
    sumar_validacion = fields.Boolean (string='NO sumar en validación:')
    precio_venta_informe = fields.Float (string = 'Precio de Venta Informe:')
    calcular = fields.Boolean (string='Calcular peso en ordenes de compra:', default=True) 
	