from datetime import datetime
import pytz
from base64 import encodebytes, decodebytes
from . import Emisor, Adquirente, Servidor, Transportista
from . import LibreCpeError
from librecpe.cpe import LibreCPE, ClienteCpe, Cliente
from librecpe.nubefact import NubeFactPSE
import re

class Documento:
    
    def __init__(self, servidor= None, tipo = None):
        self.servidor = servidor or 'SUNAT' # vals.get('servidor','sunat')
        self.tipo = tipo
        self.tipoCAmbio = 1
        self.numero = ""
        self.tipoDocumento = ""
            
        self.emisor = Emisor()
        self.fecEmision = ""
        self.documentosAnulados = set()
        self.documentos = set()
        
        self.tipMoneda = ''
        self.adquirente = Adquirente({})
                    
        self.condicion = '1'
        self.motivo = ''
        self.codigoNota = ''
        self.totalValVenta = 0.0
        self.totalImpVenta = 0.0
        self.totalDescuentos = 0.0
        self.totalCargos = 0.0
        self.totalAnticipos = 0.0
        self.totalVenta = 0.0
        self.totalTributos = 0.0
        self.documentosModificados = set()
        self.tributos = set()
        self.operaciones = set()
        self.fecVencimiento = ""
        self.tipOperacion = ""
        self.referencia = ""
        self.guias = set()
        self.leyendas = set()
        self.cargoDescuentos = set()
                    
        self.detalles = set()
            
        self.medioPago = MedioPago() 
        
        self.observacion = ""
        
        self.documentosRelacionados = set()
            
        self.remitente = Adquirente()
        self.destinatario = Adquirente()
        
        self.establecimientoTercero = Adquirente()
                    
        self.descripcion = ""
        self.transbordo = ""
        self.pesoBruto = 0.0
        self.bultos = 0.0
        
        self.modoTraslado = ""
        self.fechaTraslado = ""
        
        self.transportistas = set()
        
        self.placa = ""
        
        self.ubigeoLlegada = ''
        self.direccionLlegada = ""
        
        self.vehículos = set()
        
        self.contenedor = ''
            
        self.ubigeoPartida = ''
        self.direccionPartida = ''
            
        self.puerto = ''
        self.anticipos = set()
        self.notas = ''

        self.detraccion = set()
        self.retencion = set()
    
    def validate(self):
        if not self.tributos:
            raise LibreCpeError("tributos", "No esta defenifido")

    def setDocument(self, vals):
        self.numero = vals.get('numero', '')
        self.tipoDocumento = vals.get('tipoDocumento', '')
            
        if self.tipo in ['rc', 'ra']:
            self.emisor = Emisor(vals.get('emisor', {}))
            try:
                self.fecEmision = datetime.strptime(vals.get('fecEmision', datetime.now(tz=pytz.timezone('America/Lima')).strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S")
            except Exception:
                raise LibreCpeError("fecEmision", "No esta defenifido o no cumple el formato 'AAA-mm-dd HH:MM:SS'")
            
            if self.tipoDocumento in ['rc', 'ra']:
                try:
                    self.fecEnvio = datetime.strptime(vals.get('fecEnvio', datetime.now(tz=pytz.timezone('America/Lima')).strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S")
                except Exception:
                    raise LibreCpeError("fecEnvio", "No esta defenifido o no cumple el formato 'AAA-mm-dd HH:MM:SS'")
            if self.tipo in ['ra']:
                for anulado in vals.get('documentosAnulados',[]):
                    self.documentosAnulados.add(DocumentoAnulado(**anulado))
            elif self.tipo in ['rc']:
                if self.tipoDocumento in ['rc']:
                    for documento in vals.get('documentos'):
                        doc = Documento(tipo=self.tipo)
                        doc.setDocument(documento)
                        self.documentos.add(doc)
                else:
                    self.tipMoneda = vals.get('tipMoneda', '')
                    self.adquirente = Adquirente(vals.get('adquirente', {}))
                    # Valido solo para Boletas
                    self.condicion = vals.get('condicion', '1')
                    self.motivo = vals.get('motivo', '')
                    self.codigoNota = vals.get('codigoNota', '')
                    self.totalValVenta = round(vals.get('totalValVenta', 0.0), 2)
                    self.totalImpVenta = round(vals.get('totalImpVenta', 0.0), 2)
                    self.totalDescuentos = round(vals.get('totalDescuentos', 0.0), 2)
                    self.totalCargos = round(vals.get('totalCargos', 0.0), 2)
                    self.totalAnticipos = round(vals.get('totalAnticipos', 0.0), 2)
                    self.totalVenta = round(vals.get('totalVenta', 0.0), 2)
                    for documentoModificado in vals.get('documentosModificados', []):
                        self.documentosModificados.add(DocumentoRelacionado(documentoModificado.get('numero',''), documentoModificado.get('tipoDocumento')))
                    self.totalTributos = round(vals.get('totalTributos', 0.0), 2)
                    for tributo in vals.get('tributos', []):
                        self.tributos.add(Tributo(tributo))
                    for operacion in vals.get('operaciones', []):
                        self.operaciones.add(TotalOperaciones(**operacion))
        elif self.tipoDocumento in ['01','03','07','08']:
            self.emisor = Emisor(vals.get('emisor', {}))
            try:
                self.fecEmision = datetime.strptime(vals.get('fecEmision', datetime.now(tz=pytz.timezone('America/Lima')).strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S")
            except Exception:
                raise LibreCpeError("fecEmision", "No esta defenifido o no cumple el formato 'AAA-mm-dd HH:MM:SS'")
            self.tipoDeCambio = round(vals.get('tipoDeCambio', 1), 3)
            self.fecVencimiento = vals.get('fecVencimiento', '')
            self.tipOperacion = vals.get('tipOperacion', '')
            self.tipMoneda = vals.get('tipMoneda', '')
            self.adquirente = Adquirente(vals.get('adquirente', {}))
            self.referencia = vals.get('referencia','')
            for guia in vals.get('guias', []):
                self.guias.add(Guia(guia))
            for leyenda in vals.get('leyendas', []):
                self.leyendas.add(Leyenda(leyenda.get('codLeyenda', ''), leyenda.get('desLeyenda', '')))
            for cargoDescuento in vals.get("cargoDescuentos",[]):
                self.cargoDescuentos.add(CargoDescuento(cargoDescuento))
            self.motivo = vals.get('motivo', '')
            self.codigoNota = vals.get('codigoNota', '')
            
            self.totalValVenta = round(vals.get('totalValVenta', 0.0), 2)
            self.totalImpVenta = round(vals.get('totalImpVenta', 0.0), 2)
            self.totalDescuentos = round(vals.get('totalDescuentos', 0.0), 2)
            self.totalCargos = round(vals.get('totalCargos', 0.0), 2)
            self.totalAnticipos = round(vals.get('totalAnticipos', 0.0), 2)
            self.totalVenta = round(vals.get('totalVenta', 0.0), 2)
                        
            for documentoModificado in vals.get('documentosModificados', []):
                self.documentosModificados.add(DocumentoRelacionado(documentoModificado.get('numero',''), documentoModificado.get('tipoDocumento')))
            
            self.totalTributos = round(vals.get('totalTributos', 0.0), 2)
            
            for tributo in vals.get('tributos', []):
                self.tributos.add(Tributo(tributo))
            
            for detalle in vals.get('detalles', []):
                self.detalles.add(Detalle(detalle))            
            self.medioPago = MedioPago(vals.get("medioPago", {})) 
            for anticipo in vals.get('anticipos', []):
                self.anticipos.add(Anticipo(anticipo)) 
            self.notas = vals.get("notas")

            if vals.get('detraccion'):
                self.detraccion = Detraccion(vals.get('detraccion'))
            if vals.get('retencion'):
                self.retencion = Retencion(vals.get('retencion'))

        elif self.tipoDocumento in ['09']:
            self.observacion = vals.get('observacion')
            self.fecEmision = datetime.strptime(vals.get('fecEmision', datetime.now(tz=pytz.timezone('America/Lima')).strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S")
            self.emisor = Emisor(vals.get('emisor', {}))
            for anulado in vals.get('documentosAnulados',[]):
                self.documentosAnulados.add(DocumentoAnulado(**anulado))
            for documentoModificado in vals.get('documentosRelacionados', []):
                self.documentosRelacionados.add(DocumentoRelacionado(documentoModificado.get('numero',''), documentoModificado.get('tipoDocumento')))            
            self.remitente = Adquirente(vals.get('remitente', {}))
            self.destinatario = Adquirente(vals.get('destinatario', {}))
            self.establecimientoTercero = vals.get('establecimientoTercero', {}) and Adquirente(vals.get('establecimientoTercero', {})) or vals.get('establecimientoTercero', {})
            
            # Datos de envio
            self.motivo = vals.get('motivo', "")
            
            self.descripcion = vals.get('descripcion', "")
            self.transbordo = vals.get('transbordo', "false")
            self.pesoBruto = vals.get('pesoBruto', 0.0)
            self.bultos = vals.get('bultos', 0.0)
            self.modoTraslado = vals.get('modoTraslado', "")
            self.fechaTraslado = vals.get('fechaTraslado', "")
            
            for transportista in vals.get('transportistas', []):
                self.transportistas.add(Transportista(transportista))
            # VEHICULO (Transporte Privado)
            self.placa = vals.get('placa', '')
            
            # CONDUCTOR (Transporte Privado)
            #self.conductor = Adquirente(vals.get('conductor', {}))
            
            # Direccion punto de llegada
            self.ubigeoLlegada = vals.get('ubigeoLlegada', '')
            self.direccionLlegada = vals.get('direccionLlegada', '')[:100]
            
            # Datos del vehículos
            for vehículo in vals.get('vehículos', []):
                self.vehículos.add(Vehículo(vehículo))
                self.placa = vals.get('placa', '')
            
            # Datos del contenedor (Motivo Importación)
            self.contenedor = vals.get('contenedor', '')
            
            # Direccion del punto de partida
            self.ubigeoPartida = vals.get("ubigeoPartida", '')
            self.direccionPartida = vals.get('direccionPartida', '')[:100]
            
            # Puerto o Aeropuerto de embarque/desembarque
            self.puerto = vals.get("puerto", "")
            
            # BIENES A TRANSPORTAR
            for detalle in vals.get('detalles', []):
                self.detalles.add(DetalleBienes(detalle))

    def getDocumento(self, key=None, cer=None, xml=None):
        vals = {}
        if self.servidor in ['SUNAT']:
            if not key:
                raise LibreCpeError("certificado", "No esta definido el certificado/Clave Privada")
            if not cer:
                raise LibreCpeError("certificado", "No esta definido el certificado/Clave Publica")
            librecpe = LibreCPE(self)
            if xml and not type(xml) == bytes:
                xml=xml.encode('utf-8')
            xml, xml_firmado = librecpe.getDocumento(key, cer, xml)
            resumen, firma = librecpe.getFirma(xml_firmado)
            vals['xml'] = encodebytes(xml)
            vals['xml_firmado'] = encodebytes(xml_firmado)
            vals['resumen'] = resumen
            vals['firma'] = firma
        return vals
    
    def enviarDocumento(self, servidor, nombre_documento=None, tipo=None, xml=None):
        servidor_obj = Servidor()
        servidor_obj.setServidor(servidor)
        if servidor_obj.servidor in ['sunat']:
            ruc = servidor.get('ruc')
            cliente_soap = ClienteCpe(ruc, servidor_obj, tipo)
            cliente = Cliente()
            xml = decodebytes(xml)
            zip, estado_respuesta, respuesta, datos_respuesta = cliente.procesar(document_name=nombre_documento, type=tipo, xml=xml, client=cliente_soap)
            return {'estado': estado_respuesta, 'respuesta':respuesta, 'datos_respuesta': datos_respuesta}
        elif servidor_obj.servidor in ['nubefact_pse']:
            nubefact = NubeFactPSE(self)
            if tipo == 'ra':
                return nubefact.anularDocumento(servidor_obj)
            else: 
                return nubefact.enviarDocumento(servidor_obj)
        else:
            return {}

    def obtenerEstadoDocumento(self, soap, nombre_documento, tipo, ticket = None):
        ruc = soap.get('ruc')
        servidor = Servidor()
        servidor.setServidor(soap)
        if servidor.servidor in ['sunat']:
            cliente_soap = ClienteCpe(ruc, servidor, tipo)
            cliente = Cliente()
            zip, estado_respuesta, respuesta, datos_respuesta  = cliente.get_status(document_name=nombre_documento, type=tipo, client=cliente_soap, ticket=ticket)
            return {'estado': estado_respuesta, 'respuesta':respuesta, 'datos_respuesta': datos_respuesta}
        elif servidor.servidor in ['nubefact_pse']:
            nubefact = NubeFactPSE(self)
            return nubefact.estadoDocumento(servidor, nombre_documento, tipo)

    def obtenerRespuesta(self, file, name):
        cliente = Cliente()
        codigo, descripcion, respuesta, nota = cliente.obtenerRespuesta(file, name)
        return {'codigo': codigo, 'descripcion': descripcion, 'respuesta':respuesta, 'nota': nota}

class DetalleBienes:
    
    def __init__(self, vals={}):
        
        self.cantidad = round(vals.get('cantidad', 0.0), 10)
        self.codUnidadMedida = vals.get('codUnidadMedida', 'NIU')
        self.descripcion = vals.get('descripcion', '').replace("\n", " ")[:250].strip()
        self.codProducto = vals.get('codProducto', '')

class Vehículo:
    def __init__(self, vals={}):
        self.principal = vals.get('principal', False)
        self.placa = vals.get('placa')

class TotalOperaciones:
    
    def __init__(self, codigo='', total=0.0):
        self.total = round(total,2)
        self.codigo = codigo


class DocumentoAnulado:
    def __init__(self, numero='', tipoDocumento='', descripcion=''):
        self.tipoDocumento = tipoDocumento
        self.descripcion = descripcion
        self.validar_numero(numero)
        self.numero = numero.split('-')[-1]
        self.serie = numero.split('-')[0]
    
    def validar_numero(self, numero):
        if self.tipoDocumento in ['01','03','07','08']:
            if not re.match(r'^(B|F){1}[A-Z0-9]{3}\-\d+$', numero):
                raise LibreCpeError("documentosAnulados/numero", "El numero del documento ingresado no cumple con el estandar.\nEjemplo F001-0001 o BN01-0001")
        if self.tipoDocumento in ['09']:
            if not re.match(r'^(T|E){1}[A-Z0-9]{3}\-\d+$', numero):
                raise LibreCpeError("documentosAnulados/numero", "El numero del documento ingresado no cumple con el estandar.\nEjemplo F001-0001 o BN01-0001")
        

class DocumentoRelacionado:
    def __init__(self, numero='', tipoDocumento=''):
        self.tipoDocumento = tipoDocumento
        self.numero = numero

class Detalle:
    
    def __init__(self, vals={}):
        self.codUnidadMedida = vals.get('codUnidadMedida', 'NIU')
        self.cantidad = round(vals.get('cantidad', 0.0), 10)
        self.codProducto = vals.get('codProducto', '')
        self.codProductoSUNAT = vals.get('codProductoSUNAT', '')
        self.codProductoGTIN = vals.get('codProductoGTIN', '')
        self.tipoProductoGTIN = vals.get('tipoProductoGTIN', '')
        self.descripcion = vals.get('descripcion', '').strip()
        self.mtoValorUnitario = round(vals.get('mtoValorUnitario', 0.0), 10)
        self.sumTotTributosItem = round(vals.get('sumTotTributosItem', 0.0),2)
        tributos = []
        for tributo in vals.get('tributos', []):
            tributos.append(Tributo(tributo))
        self.tributos = tributos
        self.mtoPrecioVentaUnitario = round(vals.get('mtoPrecioVentaUnitario', 0.0),10)
        self.mtoValorVentaItem = round(vals.get('mtoValorVentaItem', 0.0),2)
        self.mtoValorReferencialUnitario = round(vals.get('mtoValorReferencialUnitario', 0.0),10)
        
        cargoDescuentos = []
        for cargoDescuento in vals.get('cargoDescuentos',[]):
            cargoDescuentos.append(CargoDescuento(cargoDescuento, True))
        self.cargoDescuentos = cargoDescuentos
        # Afectación al IGV o IVAP cuando corresponda
        self.tipAfectacion = vals.get('tipAfectacion', '')
        # Placa de vehiculo
        self.placa = vals.get('placa', "")
        #Tipo de sistema de ISC
        self.tipISC = vals.get('tipISC', "")

    def validate(self):
        if not self.tributos:
            raise LibreCpeError("detalles/tributos", "No esta defenifido")
        if not self.sumTotTributosItem:
            sumTotTributosItem = 0.0
            for tributo in self.tributos:
                sumTotTributosItem += tributo.montoTributo
            self.sumTotTributosItem = round(sumTotTributosItem, 2)

            
class Leyenda:
    
    def __init__(self, codLeyenda='', desLeyenda=''):
        self.codLeyenda = codLeyenda
        self.desLeyenda = desLeyenda

    
class CargoDescuento:
    
    def __init__(self, vals={}, item = False):
        self.tipo = vals.get('tipo', 'descuento')
        if vals.get('tipo', '') == 'cargo':
            self.indicador = 'true'
        else:
            self.indicador = 'false'
        self.codigo = vals.get('codigo') or (item and '00') or '02'
        self.monto = round(vals.get('monto', 0.0), 2)
        self.base = round(vals.get('base', 0.0), 2)
        if not vals.get('porcentaje', 0.0):
            self.porcentaje = round(vals.get('monto', 0.0)/(vals.get('base', 0.0) or 1),5)
        else:
            self.porcentaje = round(vals.get('porcentaje', 0.0), 5)
        
    def validate(self):
        if self.monto == 0.0:
            raise LibreCpeError("cargoDescuento/monto", "Debe ser mayo que 0.0")
        if self.base == 0.0:
            raise LibreCpeError("cargoDescuento/base", "Debe ser mayo que 0.0")
        

class Tributo:
    
    def __init__(self, vals={}):
        self.ideTributo = vals.get('ideTributo', '')
        self.nomTributo = vals.get('nomTributo', '')
        self.codTipTributo = vals.get('codTipTributo', '')
        self.montoTributo = vals.get('montoTributo', 0.0)
        self.baseTributo = vals.get('baseTributo', 0.0)
        self.procentaje = vals.get('procentaje', 0.0)
        if vals.get('ideTributo', '') == '7152':
            self.cantidad = vals.get('cantidad') and vals.get('cantidad') or int(round(vals.get('montoTributo', 0.0)/(vals.get('procentaje', 0.0) or 1)))
        else:
            self.cantidad = 0


class Guia:

    def __init__(self, vals={}):
        self.numero = vals.get("numero")
        self.tipoDocumento = vals.get("tipoDocumento", "09")

class MedioPago:
    def __init__(self, vals={}):
        self.tipo = vals.get('tipo', 'Contado')
        monto = 0
        cuotas = set()
        for cuota in vals.get("cuotas", []):
            monto += cuota.get('monto', 0.0)
            cuotas.add(Cuota(cuota))
        self.cuotas = cuotas
        self.monto = round(monto,2)

class Cuota:
    
    def __init__(self, vals={}):
        self.monto = round(vals.get('monto', 0.0),2)
        self.fecha = vals.get('fecha', '')
        #self.nombre = vals.get('nombre', '')

class Anticipo:
    def __init__(self, vals={}):
        self.numero = vals.get('numero', '')
        self.tipoDocumento = vals.get('tipoDocumento', '')
        self.tipoCodigo = vals.get('tipoCodigo', '')
        if not self.tipoCodigo and self.tipoDocumento:
            if self.tipoDocumento == '01':
                self.tipoCodigo = '02'
            elif self.tipoDocumento == '03':
                self.tipoCodigo = '03'
        self.monto = round(vals.get('monto', 0.0),2)
        #self.impuestos = round(vals.get('impuestos', 0.0),2)
        self.fecha = vals.get('fecha', '')
        self.tributos = set()
        for tributo in vals.get('tributos', []):
            self.tributos.add(Tributo(tributo))

class Detraccion:

    def __init__(self, vals={}):
        self.cuentaBanco = vals.get('cuentaBanco')
        self.medioPago = vals.get('medioPago', '001')
        self.codigo = vals.get('codigo', '')
        self.monto = round(vals.get('monto', 0.0), 2)
        self.porcentaje = round(vals.get('porcentaje', 0.0), 5)

class Retencion:
    def __init__(self, vals={}):
        self.codigo = vals.get('codigo', '')
        self.base = round(vals.get('base', 0.0), 2)
        self.monto = round(vals.get('monto', 0.0), 2)
        self.porcentaje = round(vals.get('porcentaje', 0.0)/100, 5)
