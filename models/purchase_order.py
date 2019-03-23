# -*- coding: utf-8 -*-

from odoo import models, fields, api
from openerp.exceptions import ValidationError
from odoo.exceptions import UserError
from openerp.exceptions import Warning
from openerp import models, fields, api
import subprocess
import time
import datetime
import base64
from openerp.http import request
from ..dependencies.imManager import IM

class purchase_order(models.Model):
    _name = 'purchase.order'
    _inherit = 'purchase.order'
    state = fields.Selection(selection_add=[('quotation_paid', "Pagado")])
    imagen_pago = fields.Binary(string="Información de pago")
    fecha_pago = fields.Datetime(string="Fecha Pago", readonly=True, copy=False)
    cajero_id = fields.Char(string="Cajero", readonly=True, copy=False)
    cliente = fields.Char(string="Cliente")
    cantidad = fields.Integer(string="Cantidad (KG)", default=1)
    material_procesado = fields.Char(string="Material Procesado", default="Desechos Reciclables")
    co2 = fields.Char(store=True, string="CO2")
    periodo = fields.Char(string="Periodo")
    peso_lleno = fields.Float(string="Peso Lleno")
    peso_vacio = fields.Float(string="Peso Vacio")
    peso_neto = fields.Float( string="Peso Neto")
    ficha = fields.Char (string="Ficha")
    placa_vehiculo= fields.Char (string="Placa")
    pago = fields.Selection ([('regular','Regular'), ('muy','***MUY PAGA***'), ('caja_chica','Caja Chica')], string='Metodo de Pago', required=True)
    pago_caja = fields.Selection ([('pendiente','Pendiente'),('pagado','Pagado')], string='Pago', default="pendiente", readonly=True, copy=False)
    #informacion = fields.Char(compute='_update_info', store=True, string="Avisos")
    informacion = fields.Char (string="Avisos")
    #prestamo_info = fields.Char(compute='_action_allowance', store=True, default=0, string="Prestamo" )
    #mantenimiento_info = fields.Char(compute='_action_allowance', store=True, string="Avisos")
	#purchase_info_validation = fields.Char(compute='_action_purchase_creation', store=True, string="validacion")

    @api.multi
    def button_confirm(self):
        super(purchase_order, self).button_confirm()

        # Ingreso Automatico de Albaranes
        albaran = self.env['stock.picking'].search([('state', '=', 'assigned'), ('origin', '=', self.name)])
        print ("------>" + str(albaran))

        for move in albaran.move_ids_without_package:
            move.quantity_done = move.product_uom_qty

        albaran.button_validate()

    
    # Marcar la factura como pagada y la asocia con los cierres de caja
    @api.one
    def action_quotation_paid(self):

        # Valida si la factura fue cancelada antes de pagarla
        if str(self.state) == "cancel" :
            raise Warning ("Error: La factura fue cancelada")
        
        '''
        #Cajeros    
        cajero_cierre_regular = self.env['cierre'].search([('cajero', '=', str(self.env.user.name)), ('state', '=', 'new'), ('tipo', '=', 'regular')])
        cajero_cierre_caja_chica = self.env['cierre'].search([('cajero', '=', str(self.env.user.name)), ('state', '=', 'new'), ('tipo', '=', 'caja_chica')])
        # Cierres
        cierre_regular = self.env['cierre'].search([('state', '=', 'new'), ('tipo', '=', 'regular')])
        cierre_caja_chica = self.env['cierre'].search([('state', '=', 'new'), ('tipo', '=', 'caja_chica')])

        # El usuario administrador puede pagar todas las facturas
        if str(self.env.user.name) == "Administrator" :
            self.cajero_id = str(self.env.user.name)
            self.fecha_pago = fields.Datetime.now()
            self.pago_caja = 'pagado'
            self.cierre_id = cierre_regular.id
            self.cierre_id_caja_chica = cajero_cierre_caja_chica.id
        else:
            # Valida si el usuario que creo la orden de compra es igual al cajero
            if str(self.env.user.name) == str(self.validator.name) :
                raise Warning ("Error: El usuario que valida el pedido de compra es igual al cajero")

            # Valida si hay cierres de caja disponibles para asociarlos
            if cierre_regular.id == False :
                raise Warning ("Error: Proceda a crear un cierre de caja tipo Regular.")
            if str(self.pago) == "caja_chica":
                if cierre_caja_chica.id == False:
                    raise Warning ("Error: Proceda a crear un cierre de caja tipo Caja Chica.")     
            #===============================================
            # Valida facturas tipo Caja Chica
            if str(self.pago) == "caja_chica" :

                if str(cajero_cierre_caja_chica.cajero) == str(self.env.user.name) :
                    self.cajero_id = str(self.env.user.name)
                    self.fecha_pago = fields.Datetime.now()
                    self.pago_caja = 'pagado'
                    self.cierre_id = cierre_regular.id
                    self.cierre_id_caja_chica = cajero_cierre_caja_chica.id
                else:
                    raise Warning ("Usuario no autorizado para pagar facturas") 
            #===============================================
            # Valida facturas tipo Regular
            elif str(self.pago) == "regular" :

                # Valida si el usuario que creo la orden de compra es igual al cajero
                if str(self.env.user.name) == str(self.validator.name) :
                    raise Warning ("Error: El usuario que valida el pedido de compra es igual al cajero")
                
                # verifica que se adjunte la imagen
                if str(self.imagen_pago) == "None":
                    raise Warning ("Por Favor adjunte la imagen de pago.")

                if str(cajero_cierre_regular.cajero) == str(self.env.user.name) :
                    self.cajero_id = str(self.env.user.name)
                    self.fecha_pago = fields.Datetime.now()
                    self.pago_caja = 'pagado'
                    self.cierre_id = cierre_regular.id
                    self.cierre_id_caja_regular = cajero_cierre_regular.id
                else:
                    raise Warning ("Usuario no autorizado para pagar facturas")
            #===============================================
            # Valida las facturas tipo Muy Paga
            elif str(self.pago) == "muy" :
                self.cajero_id = str(self.env.user.name)
                self.fecha_pago = fields.Datetime.now()
                self.pago_caja = 'pagado'
                # Asocia el Nombre del cajera
                self.cierre_id = cajero_cierre_regular.id
                # Asocia el cierre de caja
                self.cierre_id_caja_regular = cajero_cierre_regular.id
            
            else:
                raise Warning ("Usuario no autorizado para pagar facturas") 
                    
            if str(self.informacion) == "Listo Para Revisar | ***MUY PAGA***":
                self.informacion = "***MUY PAGA***"

            # Crear directament un Abono al prestamo
            res= self.env['cliente.allowance'].search([('name', '=', str(self.partner_id.name)), ('state', '=', 'new')])
            print str(res)
            for line in self.order_line:
                if line.product_id.name == "Prestamo" and len(res) > 0:
res[0].abono_ids.create({'name':str(res[0].name),'libro_id':res[0].id, 'monto':-(line.price_subtotal), 'notas': str(self.name)})
`
'''

# Calcular la cantidad del producto a facturar
    @api.one
   # @api.onchange('peso_lleno', 'peso_vacio')
    def action_calcular_peso(self):
        
        # Validaciones peso lleno y vacio
        if self.peso_lleno < 1 or self.peso_vacio < 1 :
            raise Warning ("Error: Ingrese los pesos lleno y vacio.")
        if self.peso_vacio > self.peso_lleno:
            raise Warning ("Error: El peso vacio no puede ser mayor al lleno")

        # Validar que solamente 1 producto tenga el check de calcular / Validar los productos sobre los cuales no se puede realizar calculo
        productos_marcados = 0
        for i in self.order_line :
            if i.product_id.calcular == False and i.calcular == True :
                raise Warning ("Error: Este producto no es valido para realizar el cálculo")
            if i.calcular == True:
                productos_marcados += 1
        if productos_marcados > 1 :
            raise Warning ("Error: Solamente 1 producto puede ser calculado")
        if productos_marcados == 0 :
            raise Warning ("Error: Seleccione 1 producto para calcular")

        # Calculo de la cantidad de producto a facturar
        descontar = 0
        cantidad_facturable = self.peso_lleno - self.peso_vacio
        for i in self.order_line:
            # Productos que no se deben descontar: Mantenimiento, rebajo, prestamo
            if i.product_id.name != "Mantenimiento" and i.product_id.name != "Rebajo" and i.product_id.name != "Prestamo" and i.calcular == False:
                descontar += i.product_qty

        # Asigna la cantidad de material a facturar en la linea de compra
        for i in self.order_line:
            if i.calcular == True :
                i.product_qty = cantidad_facturable - descontar

# Calcular el peso neto
    @api.onchange('peso_lleno', 'peso_vacio')
    def _action_peso_neto(self):

      if self.peso_lleno > 0 and self.peso_vacio > 0:
        self.peso_neto = self.peso_lleno - self.peso_vacio
    
      # Nombre de la impresora 
      impresora = self.env['impresora'].search([('state', '=', 'on')])
      
      if len(impresora) > 0 and self.peso_lleno > 0:
          if impresora[0].state == "on" :
            subprocess.call('echo' + ' \"' + '------------------------ \n '+ '$(TZ=GMT+6 date +%T%p_%D)' + '\n \n' + 
            str(self.partner_id.name) + '\n' + str(self.placa_vehiculo) + '\n \n' +
            'Ingreso: ' + str(self.peso_lleno) + ' kg \n' + 'Salida: ' + str(self.peso_vacio) + ' kg \n' + 'NETO: ' + str(self.peso_neto) + ' kg \n' 
+ '------------------------ \n'+ '\"' + '| lp -d ' + str(impresora[0].name), shell=True)

# Tomar Fotos   
    @api.one
    def action_take_picture(self):
        # Solo incluye las lineas de pedido si la factura esta vacia
        if len(self.order_line) == 0:
            # Incluye linea de Chatarra
            res= self.env['product.template'].search([['name', '=', 'Chatarra'], ['default_code', '=', 'CH']])
            self.order_line.create({'product_id': str(res.id), 'price_unit':str(res.list_price), 'order_id' : self.id, 'name': '[CH] Chatarra','calcular': True, 'date_planned': str(fields.Date.today()), 'product_qty': 1, 'product_uom': str(res.uom_po_id.id)})

            # Incluye Linea de basura
            #res_basura= self.env['product.template'].search([('name', '=', 'Basura Chatarra')])
            #self.order_line.create({'product_id': str(res_basura.id), 'price_unit':str(res_basura.list_price), 'order_id' : self.id, 'name': '[BC] Basura Chatarra', 'date_planned': str(fields.Date.today())})


        for line in self.order_line:
            # No se adjuntan fotos a los productos especiales
            if line.product_id.name != 'Basura Chatarra' and line.product_id.name != 'Prestamo' and line.product_id.name != 'Rebajo' :

                if not line.imagen_lleno :
                    test = IM({"ip": "192.168.2.32", "user": "admin", "passw": "lacapri001"}, {"ip": "192.168.2.153", "user": "admin", "passw": "lacapri001"})
                    res = test.get_image()
                    print(res)
                    line.imagen_lleno = base64.b64encode(res)
                    break
                else:
                    test = IM({"ip": "192.168.2.32", "user": "admin", "passw": "lacapri001"}, {"ip": "192.168.2.153", "user": "admin", "passw": "lacapri001"})
                    res = test.get_image()
                    print(res)
                    line.imagen_vacio = base64.b64encode(res)
                    break

