import json
from datetime import datetime
import requests
import re

data = {
    "tipo_de_comprobante":{
        "01":"1",
        "03":"2",
        "07":"3",
        "08":"4",
        "09":"7"
    },
    "sunat_transaction":{
        "0101":"1",
        "0200":"2",
        "0101":"4",
        "0401":"29",
        "1001":"30",
        "1004":"33",
        "2001":"34",
        "1003":"32",
        "1002":"31"
    },
    "moneda":{
        "PEN":"1",
        "USD":"2",
        "EUR":"3"
    },
    "percepcion_tipo":{
        "01":"1",
        "02":"2",
        "03":"3"
    },
    "tipo_de_nota_de_credito":{
        "01":"1",
        "02":"2",
        "03":"3",
        "04":"4",
        "05":"5",
        "06":"6",
        "07":"7",
        "08":"8",
        "09":"9",
        "10":"10",
        "11":"11",
        "12":"12",
        "13":"13"
    },
    "tipo_de_nota_de_debito":{
        "01":"1",
        "02":"2",
        "03":"3",
        "11":"5",
        "12":"4"
    },
    "tipo_de_igv":{
        "10":"1",
        "11":"2",
        "12":"3",
        "13":"4",
        "14":"5",
        "15":"6",
        "16":"7",
        "20":"8",
        "21":"17",
        "30":"9",
        "31":"10",
        "32":"11",
        "33":"12",
        "34":"13",
        "35":"14",
        "36":"15",
        "40":"16"
    },
    "guia_tipo":{
        "09":"1"
    }
}


class NubeFactPSE:
    
    def __init__(self, documento = None):
        self.documento = documento
        
    def _getCliente(self):
        vals = {}
        cliente = self.documento.tipoDocumento=='09' and self.documento.remitente or self.documento.adquirente
        vals['cliente_tipo_de_documento'] = cliente.tipoDocumento
        vals['cliente_numero_de_documento'] = cliente.numDocumento
        vals['cliente_denominacion'] = cliente.nombre
        vals['cliente_direccion'] = cliente.direccion
        vals['cliente_email'] = cliente.email
        vals['cliente_email_1'] = ""
        vals['cliente_email_2'] = ""
        vals['enviar_automaticamente_al_cliente'] = cliente.email and True or False
        return vals
    
    def _getDocumentoModificado(self):
        vals = {}
        for documentoModificado in self.documento.documentosModificados:
            vals['documento_que_se_modifica_tipo'] = documentoModificado.tipoDocumento
            vals['documento_que_se_modifica_serie'] = documentoModificado.numero.split("-")[0]
            vals['documento_que_se_modifica_numero'] = documentoModificado.numero.split("-")[-1]
            if self.documento.tipoDocumento in ['07']:
                vals['tipo_de_nota_de_credito'] = self.documento.codigoNota
                vals['tipo_de_nota_de_debito'] = ""
            else:
                vals['tipo_de_nota_de_credito'] = ""
                vals['tipo_de_nota_de_debito'] = self.documento.codigoNota
            break
        return vals
    
    def _getTotales(self):
        vals={}
        vals['descuento_global'] = self.documento.totalDescuentos
        descuento = 0.0
        for detalle in self.documento.detalles:
            for desc in detalle.cargoDescuentos:
                if desc.indicador == 'false':
                    descuento+=desc.monto
        vals['total_descuento'] = self.documento.totalDescuentos + descuento
        vals['total_anticipo'] = self.documento.totalAnticipos
        vals['total_gravada'] = self.documento.totalValVenta
        vals['total_inafecta'] = 0.0
        vals['total_exonerada'] = 0.0
        vals['total_igv'] = self.documento.totalTributos
        vals['total_otros_cargos'] = self.documento.totalCargos
        vals['total'] = self.documento.totalVenta
        return vals
    
    def _getItems(self):
        placa = ""
        items=[]
        cont=0
        for detalle in self.documento.detalles:
            vals = {}
            vals['unidad_de_medida'] = detalle.codUnidadMedida
            vals['codigo'] = detalle.codProducto
            vals['codigo_producto_sunat'] = detalle.codProductoSUNAT
            vals['descripcion'] = detalle.descripcion
            vals['cantidad'] = detalle.cantidad
            vals['valor_unitario'] = detalle.mtoValorUnitario
            vals['precio_unitario'] = detalle.mtoPrecioVentaUnitario
            descuento = 0.0
            for desc in detalle.cargoDescuentos:
                if desc.indicador == 'false':
                    descuento+=desc.monto
            for tributo in detalle.tributos:
                if descuento>0.0 and tributo.procentaje>0.0 and tributo.ideTributo != '7152':
                    vals['precio_unitario'] = round(vals['valor_unitario']*(1+tributo.procentaje/100), 10)
                elif tributo.ideTributo != '7152':
                    vals['precio_unitario'] = round(vals['valor_unitario']+tributo.montoTributo, 10)
            vals['descuento'] = descuento
            vals['subtotal'] = detalle.mtoValorUnitario*detalle.cantidad - descuento      
            vals['tipo_de_igv'] = data['tipo_de_igv'].get(detalle.tipAfectacion,detalle.tipAfectacion)
            vals['igv'] = detalle.sumTotTributosItem
            vals['total'] = detalle.mtoPrecioVentaUnitario*detalle.cantidad
            vals['anticipo_regularizacion'] = ''
            vals['anticipo_documento_serie'] = ''
            vals['anticipo_documento_numero'] = ''
            if detalle.placa:
                placa = detalle.placa
            items.append(vals)
        vals = {}
        vals['items'] = items
        vals['placa'] = placa
        return vals
    
    def _getGuias(self):
        res = []
        for guia in self.documento.guias:
            res.append({'guia_tipo': data['guia_tipo'].get(guia.tipoDocumento, '1'),
                        'guia_serie_numero':guia.numero})
        return {'guias':res}
    
    def _getVentaCredito(self):
        res = []
        num = 1
        for cuota in self.documento.medioPago.cuotas:
            res.append({
                'cuota':num,
                'fecha_de_pago': datetime.strptime(cuota.fecha, "%Y-%m-%d").strftime("%d-%m-%Y"),
                'importe': cuota.monto
                })
            num+=1
        return {'venta_al_credito':res}
    
    def getDocumento(self):
        vals = {}
        vals['operacion'] = "generar_comprobante"
        vals['tipo_de_comprobante']= data['tipo_de_comprobante'].get(self.documento.tipoDocumento, self.documento.tipoDocumento)
        vals['serie']=self.documento.numero.split("-")[0]
        vals['numero']=self.documento.numero.split("-")[1]
        vals['sunat_transaction']= data['sunat_transaction'].get(self.documento.tipOperacion, self.documento.tipOperacion)
        vals['fecha_de_emision']= self.documento.fecEmision.strftime("%d-%m-%Y")
        vals['fecha_de_vencimiento']= self.documento.fecVencimiento and datetime.strptime(self.documento.fecVencimiento, "%Y-%m-%d").strftime("%d-%m-%Y") or ""
        vals['moneda']= data['moneda'].get(self.documento.tipMoneda,self.documento.tipMoneda) 
        #"tipo_de_cambio": "",
        vals['observaciones']= self.documento.motivo
        vals['enviar_automaticamente_a_la_sunat']=True
        vals['codigo_unico']=''
        vals['condiciones_de_pago'] = ''
        vals['medio_de_pago'] = ''
        ref = self.documento.referencia.replace(" ","").replace("-","").replace("/","")
        if ref and re.match(r'^[a-zA-Z0-9]*$', ref):
            vals['orden_compra_servicio'] = self.documento.referencia
        vals['tabla_personalizada_codigo'] = ''
        vals['formato_de_pdf'] = ''
        vals['percepcion_tipo'] = ''
        vals['percepcion_base_imponible'] = ''
        vals['total_percepcion'] = ''
        vals['total_incluido_percepcion'] = ''
        vals['detraccion'] = False
        vals.update(self._getCliente())
        if self.documento.tipoDocumento in ['07', '08']:
            vals.update(self._getDocumentoModificado())
        vals.update(self._getTotales())
        vals.update(self._getItems())
        vals.update(self._getGuias())
        vals.update(self._getVentaCredito())
        print(vals)
        return vals
        #data = json.dumps(vals)
    
    def getGuia(self):
        vals = {}
        vals['operacion'] = "generar_guia"
        vals['tipo_de_comprobante']= data['tipo_de_comprobante'].get(self.documento.tipoDocumento, self.documento.tipoDocumento)
        vals['serie']=self.documento.numero.split("-")[0]
        vals['numero']=self.documento.numero.split("-")[1]
        
        vals.update(self._getCliente())
        vals['fecha_de_emision']= self.documento.fecEmision.strftime("%d-%m-%Y")
        vals['observaciones']= self.documento.descripcion 
        
        vals['motivo_de_traslado']= self.documento.motivo
        vals['peso_bruto_total']= self.documento.pesoBruto
        vals['numero_de_bultos']= self.documento.bultos
        
        vals['tipo_de_transporte']= self.documento.modoTraslado
        vals['fecha_de_inicio_de_traslado']= self.documento.fechaTraslado
        
        for transportista in self.documento.transportistas:
            vals['transportista_documento_tipo']= transportista.tipoDocumento
            vals['transportista_documento_numero']= transportista.numDocumento
            vals['transportista_denominacion']= transportista.nombre
            if transportista.tipoDocumento in ['6']:
                break
        vals['transportista_placa_numero']= self.documento.placa
        
        for transportista in self.documento.transportistas:
            vals['conductor_documento_tipo']= transportista.tipoDocumento
            vals['conductor_documento_numero']= transportista.numDocumento
            vals['conductor_denominacion']= transportista.nombre
            if transportista.tipoDocumento not in ['6']:
                break
            
        vals['punto_de_partida_ubigeo']= self.documento.ubigeoPartida
        vals['punto_de_partida_direccion']= self.documento.direccionPartida
        
        vals['punto_de_llegada_ubigeo']= self.documento.ubigeoLlegada
        vals['punto_de_llegada_direccion']= self.documento.direccionLlegada
        vals['enviar_automaticamente_a_la_sunat']=True
        vals['codigo_unico']= ''
        vals['formato_de_pdf']= ''
        items = []
        for detalle in self.documento.detalles:
            item = {}
            item['unidad_de_medida'] = detalle.codUnidadMedida
            item['codigo'] = detalle.codUnidadMedida
            item['descripcion'] = detalle.codUnidadMedida
            item['cantidad'] = detalle.cantidad
            items.append(item)
        vals['items'] = items
        return vals
        
        
    def enviarDocumento(self, servidor):
        if self.documento.tipoDocumento in ['09']:
            vals = self.getGuia()
            print(vals)
        else:
            vals = self.getDocumento()
        try:
            response = requests.post(servidor.url,
                                   headers={
                                       'Content-Type': 'application/json',
                                       'Authorization': 'Token token=%s' % servidor.clave
                                   }, json= vals)
        except Exception:
            return {'estado':False}
        
        res = self._procesarRespuesta(response)
        if not res:
            return {'estado':False, 'respuesta': response.text}
        else:
            return {'estado':True, 'respuesta': res}
    
    def estadoDocumento(self, servidor, nombre_documento, tipo):
        res = nombre_documento.split('-')
        if tipo in ['ticket', 'ra']:
            operacion = 'consultar_anulacion'
        else:
            operacion = 'consultar_comprobante'
        vals = {
                "operacion": operacion,
                "tipo_de_comprobante": data['tipo_de_comprobante'].get(res[1]),
                "serie": res[2],
                "numero": res[3]
            }
        
        try:
            response = requests.post(servidor.url,
                                   headers={
                                       'Content-Type': 'application/json',
                                       'Authorization': 'Token token=%s' % servidor.clave
                                   }, json= vals)
        except Exception:
            return {'estado':False}
        
        res = self._procesarRespuesta(response)
        if not res:
            return {'estado':False, 'respuesta': response.text}
        else:
            return {'estado':True, 'respuesta': res}
    
    def anularDocumento(self, servidor):
        res = {}
        for anulado in self.documento.documentosAnulados:
            vals = {
                    "operacion": "generar_anulacion",
                    "tipo_de_comprobante": data['tipo_de_comprobante'].get(anulado.tipoDocumento),
                    "serie": anulado.serie,
                    "numero": anulado.numero,
                    "motivo": anulado.descripcion,
                    "codigo_unico": ""
                }
            
            try:
                response = requests.post(servidor.url,
                                       headers={
                                           'Content-Type': 'application/json',
                                           'Authorization': 'Token token=%s' % servidor.clave
                                       }, json= vals)
            except Exception:
                return {'estado':False}
            
        res = self._procesarRespuesta(response)
        if not res:
            return {'estado':False, 'respuesta': response.text}
        else:
            return {'estado':True, 'respuesta': res}
    
    
    @staticmethod
    def _procesarRespuesta(response):
        res = {}
        try:
            res = response.json()
        except Exception:
            return {}
        return res
    
    