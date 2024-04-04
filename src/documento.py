from datetime import datetime
import pytz
from base64 import encodebytes, decodebytes
from .common import Emisor, Adquirente
from .common import LibreCpeError
from .cpe import LibreCPE, Soap, Cliente
import re
import configparser

class Documento:
    
    def __init__(self, servidor= None, tipo = None):
        self.servidor = servidor or 'SUNAT' # vals.get('servidor','sunat')
        self.tipo = tipo
    
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
                documentosAnulados = []
                for anulado in vals.get('documentosAnulados',[]):
                    documentosAnulados.append(DocumentoAnulado(**anulado))
                self.documentosAnulados = documentosAnulados
            elif self.tipo in ['rc']:
                if self.tipoDocumento in ['rc']:
                    documentos = []
                    for documento in vals.get('documentos'):
                        doc = Documento(tipo=self.tipo)
                        doc.setDocument(documento)
                        documentos.append(doc)
                    self.documentos = documentos
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
                    documentosModificados = []
                    for documentoModificado in vals.get('documentosModificados', []):
                        documentosModificados.append(DocumentoRelacionado(documentoModificado.get('numero',''), documentoModificado.get('tipoDocumento')))
                    self.documentosModificados = documentosModificados
                    self.totalTributos = round(vals.get('totalTributos', 0.0), 2)
                    tributos = []
                    for tributo in vals.get('tributos', []):
                        tributos.append(Tributo(tributo))
                    self.tributos = tributos
                    operaciones = []
                    for operacion in vals.get('operaciones', []):
                        operaciones.append(TotalOperaciones(**operacion))
                    self.operaciones = operaciones
        elif self.tipoDocumento in ['01','03','07','08']:
            self.emisor = Emisor(vals.get('emisor', {}))
            try:
                self.fecEmision = datetime.strptime(vals.get('fecEmision', datetime.now(tz=pytz.timezone('America/Lima')).strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S")
            except Exception:
                raise LibreCpeError("fecEmision", "No esta defenifido o no cumple el formato 'AAA-mm-dd HH:MM:SS'")
            
            self.fecVencimiento = vals.get('fecVencimiento', '')
            self.tipOperacion = vals.get('tipOperacion', '')
            self.tipMoneda = vals.get('tipMoneda', '')
            self.adquirente = Adquirente(vals.get('adquirente', {}))
            self.referencia = vals.get('referencia','')
            guias = []
            for guia in vals.get('guias', []):
                guias.append(Guia(guia))
            self.guias = guias
            leyendas = []
            for leyenda in vals.get('leyendas', []):
                leyendas.append(Leyenda(leyenda.get('codLeyenda', ''), leyenda.get('desLeyenda', '')))
            self.leyendas = leyendas
            cargoDescuentos = []
            for cargoDescuento in vals.get("cargoDescuentos",[]):
                cargoDescuentos.append(CargoDescuento(cargoDescuento))
            self.cargoDescuentos = cargoDescuentos
            
            self.motivo = vals.get('motivo', '')
            self.codigoNota = vals.get('codigoNota', '')
            
            self.totalValVenta = round(vals.get('totalValVenta', 0.0), 2)
            self.totalImpVenta = round(vals.get('totalImpVenta', 0.0), 2)
            self.totalDescuentos = round(vals.get('totalDescuentos', 0.0), 2)
            self.totalCargos = round(vals.get('totalCargos', 0.0), 2)
            self.totalAnticipos = round(vals.get('totalAnticipos', 0.0), 2)
            self.totalVenta = round(vals.get('totalVenta', 0.0), 2)
                        
            
            documentosModificados = []
            for documentoModificado in vals.get('documentosModificados', []):
                documentosModificados.append(DocumentoRelacionado(documentoModificado.get('numero',''), documentoModificado.get('tipoDocumento')))
            self.documentosModificados = documentosModificados
            
            self.totalTributos = round(vals.get('totalTributos', 0.0), 2)
            
            tributos = []
            for tributo in vals.get('tributos', []):
                tributos.append(Tributo(tributo))
            self.tributos = tributos
            
            detalles = []
            for detalle in vals.get('detalles', []):
                detalles.append(Detalle(detalle))
            self.detalles = detalles
            
            self.medioPago = MedioPago(vals.get("medioPago", {})) 
            
            
        elif self.tipoDocumento in ['09']:
            self.observacion = vals.get('observacion')
            self.fecEmision = datetime.strptime(vals.get('fecEmision'),'%Y-%m-%d') # datetime.strptime(vals.get('fecEmision'), datetime.now(tz=pytz.timezone('America/Lima'))).strftime("%Y-%m-%d"), "%Y-%m-%d") 
            self.emisor = Emisor(vals.get('emisor', {}))
            documentosAnulados = []
            for anulado in vals.get('documentosAnulados',[]):
                documentosAnulados.append(DocumentoAnulado(**anulado))
            self.documentosAnulados = documentosAnulados
            documentosRelacionados = []
            for documentoModificado in vals.get('documentosRelacionados', []):
                documentosRelacionados.append(DocumentoRelacionado(documentoModificado.get('numero',''), documentoModificado.get('tipoDocumento')))
            self.documentosRelacionados = documentosRelacionados
            
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
            
            # Transportista (Transporte Público)
            transportistas = []
            for transportista in vals.get('transportistas', []):
                transportistas.append(Adquirente(transportista))
            
            self.transportistas = transportistas # vals.get('transportistas', {}) and Adquirente(vals.get('transportista', {})) or vals.get('transportista', {})
            
            # VEHICULO (Transporte Privado)
            self.placa = vals.get('placa', '')
            
            # CONDUCTOR (Transporte Privado)
            #self.conductor = Adquirente(vals.get('conductor', {}))
            
            # Direccion punto de llegada
            self.ubigeoLlegada = vals.get('ubigeoLlegada', '')
            self.direccionLlegada = vals.get('direccionLlegada', '')[:100]
            
            # Datos del vehículos
            vehículos = []
            for vehículo in vals.get('vehículos', []):
                vehículos.append(Vehículo(vehículo))
                if vehículo.get('principal'):
                    self.placa = vals.get('placa', '')
            self.vehículos = vehículos
            
            # Datos del contenedor (Motivo Importación)
            self.contenedor = vals.get('contenedor', '')
            
            # Direccion del punto de partida
            self.ubigeoPartida = vals.get("ubigeoPartida", '')
            self.direccionPartida = vals.get('direccionPartida', '')[:100]
            
            # Puerto o Aeropuerto de embarque/desembarque
            self.puerto = vals.get("puerto", "")
            
            # BIENES A TRANSPORTAR
            detalles = []
            for detalle in vals.get('detalles', []):
                detalles.append(DetalleBienes(detalle))
            self.detalles = detalles

    def getDocumento(self, key=None, cer=None, xml=None):
        vals = {}
        if self.servidor in ['SUNAT']:
            if not key:
                raise LibreCpeError("certificado", "No esta definido el certificado/Clave Privada")
            if not cer:
                raise LibreCpeError("certificado", "No esta definido el certificado/Clave Publica")
            if not xml:
                if self.tipoDocumento in ['rc','ra']:
                    librecpe = LibreCPE(self, '2.0')
                else:
                    librecpe = LibreCPE(self)
            else:
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
    
    def enviarDocumento(self, soap, nombre_documento, tipo, xml):
        if not soap.get('url'):
            config = configparser.RawConfigParser()
            config.read('common/servidores.conf')
            config_details = dict(config.items('SUNAT'))
            #config.readfp(open(r'abc.txt'))
            soap['url']
        cliente_soap = Soap(**soap)
        cliente = Cliente()
        xml = decodebytes(xml)
        zip, estado_respuesta, respuesta, datos_respuesta = cliente.procesar(document_name=nombre_documento, type=tipo, xml=xml, client=cliente_soap)
        return {'estado': estado_respuesta, 'respuesta':respuesta, 'datos_respuesta': datos_respuesta}

    def obtenerEstadoDocumento(self, soap, nombre_documento, tipo, ticket = None):
        cliente_soap = Soap(**soap)
        cliente = Cliente()
        zip, estado_respuesta, respuesta, datos_respuesta  = cliente.get_status(document_name=nombre_documento, type=tipo, client=cliente_soap, ticket=ticket)
        return {'estado': estado_respuesta, 'respuesta':respuesta, 'datos_respuesta': datos_respuesta}

    def obtenerRespuesta(self, file, name):
        cliente = Cliente()
        codigo, descripcion, respuesta, nota, documento = cliente.obtenerRespuesta(file, name)
        return {'codigo': codigo, 'descripcion': descripcion, 'respuesta':respuesta, 'nota': nota, 'documento':documento}

class DetalleBienes:
    
    def __init__(self, vals):
        
        self.cantidad = round(vals.get('cantidad', 0.0), 10)
        self.codUnidadMedida = vals.get('codUnidadMedida', 'NIU')
        self.descripcion = vals.get('descripcion', '').replace("\n", " ")[:250].strip()
        self.codProducto = vals.get('codProducto', '')

class Vehículo:
    def __init__(self, vals):
        self.principal = vals.get('principal', False)
        self.placa = vals.get('placa')

class TotalOperaciones:
    
    def __init__(self, codigo, total):
        self.total = round(total,2)
        self.codigo = codigo


class DocumentoAnulado:
    def __init__(self, numero, tipoDocumento, descripcion):
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
    def __init__(self, numero, tipoDocumento):
        self.tipoDocumento = tipoDocumento
        self.numero = numero

class Detalle:
    
    def __init__(self, vals):
        self.codUnidadMedida = vals.get('codUnidadMedida', 'NIU')
        self.cantidad = round(vals.get('cantidad', 0.0), 10)
        self.codProducto = vals.get('codProducto', '')
        self.codProductoSUNAT = vals.get('codProductoSUNAT', '')
        self.codProductoGTIN = vals.get('codProductoGTIN', '')
        self.tipoProductoGTIN = vals.get('tipoProductoGTIN', '')
        self.descripcion = vals.get('descripcion', '').replace("\n", " ")[:250].strip()
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
    
    def __init__(self, codLeyenda, desLeyenda):
        self.codLeyenda = codLeyenda
        self.desLeyenda = desLeyenda

    
class CargoDescuento:
    
    def __init__(self, vals, item = False):
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
    
    def __init__(self, vals):
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

    def __init__(self, vals):
        self.numero = vals.get("numero")
        self.tipoDocumento = vals.get("tipoDocumento", "09")

class MedioPago:
    def __init__(self, vals):
        self.tipo = vals.get('tipo', 'Contado')
        monto = 0
        cuotas = set()
        for cuota in vals.get("cuotas", []):
            monto += cuota.get('monto', 0.0)
            cuotas.add(Cuota(cuota))
        self.cuotas = cuotas
        self.monto = round(monto,2)

class Cuota:
    
    def __init__(self, vals):
        self.monto = round(vals.get('monto', 0.0),2)
        self.fecha = vals.get('fecha', '')
        #self.nombre = vals.get('nombre', '')

