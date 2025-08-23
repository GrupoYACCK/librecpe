from zeep.wsse.username import UsernameToken
from zeep import Client, Settings, helpers
from zeep.transports import Transport
from .tci import TCI
from base64 import encodebytes

DOC_CODE = {
    '01': 'Factura',
    '03': 'Boleta',
    '07': 'NotaCredito',
    '08': 'NotaDebito',
}
class ClienteTCI:
    def __init__(self, servidor):
        self.servidor = servidor
        self.client = self._crear_cliente()

    def _crear_cliente(self):
        settings = Settings(strict=False)
        transport = Transport()
        # transport.session.verify = False
        return Client(self.servidor.url, transport=transport, settings=settings)

    def registrar(self, documento):
        def process_response(response):
            res = helpers.serialize_object(response)
            vals = {}
            vals['respuesta'] = {}
            if res.get('RegistrarResult'):
                vals['estado'] = True
            else:
                vals['estado'] = False
            if res.get('Cadena'):
                vals['respuesta']['Cadena'] = response.Cadena
            if res.get('CodigoBarras'):
                vals['respuesta']['CodigoBarras'] = response.CodigoBarras and encodebytes(response.CodigoBarras) or response.CodigoBarras
            error = []
            if res.get('ListaError') and res.get('ListaError', {}).get('ENErrorComunicacion'):
                for item in response.ListaError.ENErrorComunicacion:
                    error.append(item)
            vals['respuesta']['ListaError'] = error
            print(vals)
            return vals
        tci = TCI(documento)
        params = tci.get_documento()
        # params['oTipoComprobante'] = documento.tipoDocumento
        # params['TipoCodigo'] = ''
        # params['CodigoBarras'] = ''
        # params['CodigoHash'] = ''
        # params['IdComprobanteCliente'] = ''
        try:
            response = self.client.service.Registrar(params,
                                                     oTipoComprobante=DOC_CODE.get(documento.tipoDocumento, 'Factura'),
                                                     Cadena="",
                                                     ListaError=[],
                                                     Otorgar=1)
            res =  process_response(response)
            # Procesar rpta de la sunat
            if res.get('respuesta') and res.get('respuesta', {}).get('CodigoBarras'):
                document_name = documento.emisor.numDocumento+"-"+documento.tipoDocumento+"-"+documento.numero
                response_vals = self.consulta_estado_comprobantes(document_name)
                if response_vals.get('respuesta', {}).get('Estado') and response_vals.get('respuesta', {}).get('MensajeEstado'):
                    res['respuesta']['Cadena'] = response_vals.get('respuesta', {}).get('MensajeEstado')
                else:
                    res['respuesta']['Cadena'] = response_vals.get('respuesta', {}).get('Mensaje')
                xml_vals = self.obtener_xml(document_name)
                if xml_vals.get('estado') and xml_vals.get('respuesta', {}).get('ArchivoXML'):
                    res['respuesta']['ArchivoXML'] = xml_vals.get('respuesta', {}).get('ArchivoXML')
                pdf_vals = self.obtener_pdf(document_name)
                if pdf_vals.get('estado') and pdf_vals.get('respuesta', {}).get('ArchivoPDF'):
                    res['respuesta']['ArchivoPDF'] = xml_vals.get('respuesta', {}).get('ArchivoPDF')
            return res
        except Exception as e:
            respuesta = {
                'faultcode': e.code,
                'faultstring': e.message,
            }
            return {'estado': False, 'respuesta': respuesta, 'datos_respuesta': {}}

    def registrar_grr(self, documento):
        def process_response(response):
            # {
            #     'at_NivelResultado': False,
            #     'at_MensajeResultado': 'Debe colocar el correo principal. [El atributo CorreoPrincipal es nulo o está vacío. - Proceso: GeneracionXmlComprobanteGuiaRemisionRemitente_V2]',
            #     'at_CodigoHash': None,
            #     'at_NombreXML': None,
            #     'at_CodigoError': -1
            # }

            res = helpers.serialize_object(response)
            vals = {}
            vals['respuesta'] = {}
            if res.get('at_NivelResultado'):
                vals['estado'] = True
            else:
                vals['estado'] = False
            if res.get('at_MensajeResultado'):
                vals['respuesta']['respuesta'] = response.at_MensajeResultado
                vals['respuesta']['nota'] = response.at_MensajeResultado
            if res.get('at_CodigoHash'):
                vals['respuesta']['hashqr'] = response.at_CodigoHash
            return vals


        tci = TCI(documento)
        params = tci.get_documento()
        try:
            response = self.client.service.RegistrarGRR20(params)
            return process_response(response)
        except Exception as e:
            respuesta = {
                'faultstring': str(e),
            }
            return {'estado': False, 'respuesta': respuesta, 'datos_respuesta': {}}
    def obtener_pdf(self, document_name):
        res = document_name.split("-")
        def process_response(response):
            res = helpers.serialize_object(response)
            vals = {}
            vals['respuesta'] = {}
            if res.get('Obtener_PDFResult', {}) and res.get('Obtener_PDFResult', {}).get('ArchivoPDF'):
                vals['respuesta']['NombrePDF'] = res.get('Obtener_PDFResult', {}).get('NombrePDF')
                vals['respuesta']['ArchivoPDF'] = encodebytes(res.get('Obtener_PDFResult', {}).get('ArchivoPDF'))
                vals['estado'] = True
            else:
                vals['estado'] = False
                vals['respuesta'] = str(response)
            return vals

        params = {
            'Numero': int(res[3]),
            'Ruc': self.servidor.usuario,
            'Serie': res[2],
            'TipoComprobante': res[1],
            'Autenticacion': {
                'Ruc': self.servidor.usuario,
            }
        }
        try:
            response = self.client.service.Obtener_PDF(params)
            return process_response(response)
        except Exception as e:
            respuesta = {
                'faultstring': str(e),
            }
            return {'estado': False, 'respuesta': respuesta, 'datos_respuesta': {}}

    def obtener_xml(self, document_name):
        res = document_name.split("-")
        def process_response(response):
            res = helpers.serialize_object(response)
            vals = {}
            vals['respuesta'] = {}
            if res.get('Obtener_XMLResult') and res.get('Obtener_XMLResult', {}).get('ArchivoXML'):
                vals['respuesta']['NombreXML'] = res.get('Obtener_XMLResult', {}).get('NombreXML')
                vals['respuesta']['ArchivoXML'] = encodebytes(res.get('Obtener_XMLResult', {}).get('ArchivoXML'))
                vals['estado'] = True
            else:
                vals['estado'] = False
                vals['respuesta'] = str(response)
            return vals

        params = {
            'Numero': int(res[3]),
            'Ruc': self.servidor.usuario,
            'Serie': res[2],
            'TipoComprobante': res[1],
            'Autenticacion': {
                'Ruc': self.servidor.usuario,
            }
        }
        try:
            response = self.client.service.Obtener_XML(params)
            return process_response(response)
        except Exception as e:
            respuesta = {
                'faultstring': str(e),
            }
            return {'estado': False, 'respuesta': respuesta, 'datos_respuesta': {}}

    def consulta_estado_comprobantes(self, document_name):
        res = document_name.split("-")
        def process_response(response):
            res = helpers.serialize_object(response)
            vals = {}
            vals['respuesta'] = {}
            vals['respuesta']['Mensaje'] = res.get('Mensaje')
            if res.get('EstadoSUNAT') and res.get('EstadoSUNAT').get('MensajeEstado'):
                vals['estado'] = True
                vals['respuesta']['MensajeEstado'] = res.get('EstadoSUNAT').get('MensajeEstado')
            else:
                vals['estado'] = False
            return vals

        params = {
            'Numero': int(res[3]),
            'Ruc': self.servidor.usuario,
            'Serie': res[2],
            'TipoComprobante': res[1],
            'Autenticacion': {
                'Ruc': self.servidor.usuario,
            }
        }
        try:
            response = self.client.service.ConsultaIndividualEstadoComprobante(params)
            res = process_response(response)
            if res.get('estado') and res.get('respuesta', {}).get('MensajeEstado'):
                xml_vals = self.obtener_xml(document_name)
                if xml_vals.get('estado') and xml_vals.get('respuesta', {}).get('ArchivoXML'):
                    res['respuesta']['ArchivoXML'] = xml_vals.get('respuesta', {}).get('ArchivoXML')
                pdf_vals = self.obtener_pdf(document_name)
                if pdf_vals.get('estado') and pdf_vals.get('respuesta', {}).get('ArchivoPDF'):
                    res['respuesta']['ArchivoPDF'] = pdf_vals.get('respuesta', {}).get('ArchivoPDF')
            return res
        except Exception as e:
            respuesta = {
                'faultstring': str(e),
            }
            return {'estado': False, 'respuesta': respuesta, 'datos_respuesta': {}}

    def registrar_comunicacion_baja(self, documento):
        def process_response(response):
            res = helpers.serialize_object(response)
            print(res)
            return res
        tci = TCI(documento)
        params = tci.get_comunicacion_baja()
        try:
            response = self.client.service.RegistrarComunicacionBaja(params, Cadena="", ListaError=[], IdCliente="0")
            res = process_response(response)
        except Exception as e:
            respuesta = {
                'faultstring': str(e),
            }
            return {'estado': False, 'respuesta': respuesta, 'datos_respuesta': {}}
        return {'estado': True, 'respuesta': res, 'datos_respuesta': {}}

if __name__ == '__main__':
    from librecpe.common import Servidor
    servidor = Servidor()
    servidor.setServidor({'servidor':'tci', 'url':'https://egestor.efacturacion.pe/WCF_TCI/Service.svc?wsdl', 'usuario':'20100157315', 'clave':'20100157315'})
    cliente = ClienteTCI(servidor)
    document_name = '20100157315-01-F009-55774'
    pdf_data = cliente.obtener_pdf(document_name)
    pdf_name = pdf_data.get('NombrePDF')
    pdf_file = pdf_data.get('ArchivoPDF')
    binary_file = open(pdf_name, "wb")
    binary_file.write(pdf_file)
    binary_file.close()
