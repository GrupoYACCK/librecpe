import re

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

    def consultar_xml_gr(self, document_name):
        def process_response(response):
            # {
            #     'at_NivelResultado': 1,
            #     'at_MensajeResultado': 'Se ha consultado el xml satisfactoriamente',
            #     'ent_ResultadoXML': {
            #         'at_XML': b'<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<ar:ApplicationResponse xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2" xmlns:ar="urn:oasis:names:specification:ubl:schema:xsd:ApplicationResponse-2"><ext:UBLExtensions><ext:UBLExtension><ext:ExtensionContent><Signature xmlns="http://www.w3.org/2000/09/xmldsig#">\n<SignedInfo>\n  <CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#WithComments"/>\n  <SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha512"/>\n  <Reference URI="">\n    <Transforms>\n      <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>\n      <Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#WithComments"/>\n    </Transforms>\n    <DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>\n    <DigestValue>ZjgssOd/Wdh3HLp3kOAyPE9yqTw=</DigestValue>\n  </Reference>\n</SignedInfo>\n    <SignatureValue>azPbC9d+bLUqtfTZoBihuRvGxON3ENheZAEZUnd6YNth02j9on3bcvzJ4C7XOP7UBszTnM/jLknaj39eP+y/dCcBmxoo2zjuI7OlFaKO3wuX30KccS1QKu04Xz9/1QCIX5WD9Gii+I9rpJEKY9LmmQ+Dv1bskr4b08qaHw0A0NIup52Gh/RzEbTZen/w1gAVHSwmD2L8AQGNmOWAjxJDXD2eolHcYhA8XeC9UT7hVnc8iEMpw9oAPkuLqqUhJ8wErvPqG6esvm/41YE1wE11MYuD5qordKkuI/bp+xtpRap62mGmhAK+kAUTL92viPTPImIOe2G8EBB3PefIyUtRDw==</SignatureValue><KeyInfo><X509Data><X509Certificate>MIIFrjCCBJagAwIBAgIIf9Td7Evg0UswDQYJKoZIhvcNAQELBQAwRjEkMCIGA1UEAwwbTGxhbWEucGUgU0hBMjU2IFN0YW5kYXJkIENBMREwDwYDVQQKDAhMTEFNQS5QRTELMAkGA1UEBhMCUEUwHhcNMjQwODA5MTYxNTM5WhcNMjcwODA5MTYxNTAwWjCCAVQxKzApBgNVBAkMIkFWLiBHQVJDSUxBU08gREUgTEEgVkVHQSBOUk8uIDE0NzIxIjAgBgkqhkiG9w0BCQEWE3JtZXphZ0BzdW5hdC5nb2IucGUxQTA/BgNVBAMMOFNVUEVSSU5ULiBOQUMuIERFIEFEVUFOQVMgWSBERSBBRE1JTklTVFJBQ0lPTiBUUklCVVRBUklBMRwwGgYDVQQLDBNBR0VOVEUgQVVUT01BVElaQURPMS4wLAYDVQQLDCVWYWxpZGFkbyBwb3IgQUJDIElERU5USURBRCBESUdJVEFMIEVSMVQwUgYDVQQKDEtTVVBFUklOVEVOREVOQ0lBIE5BQ0lPTkFMIERFIEFEVUFOQVMgWSBERSBBRE1JTklTVFJBQ0lPTiBUUklCVVRBUklBIC0gU1VOQVQxDTALBgNVBAcMBExJTUExCzAJBgNVBAYTAlBFMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1apapJOwMj9tBpgKAgjRwIloUk+xwvQZxc0s/4yl4mDSrc/F/PKZ3QBmKb43fFwivqPUvsr68fQTfyLKM14B+xXwlbQ/yh3+87sMyulLhOPmtSOU0PE8Rw0PsmGVxf1L0HPAPc3Gvuhq4Z9Dx5ByED6s+VppDmncvctlJ/NrzYZCk9H91OinTTPVZrDtbmqnOYra8PaTRoCI9Fmndeo9Oo7esM7KVX9f53NEd/mNQqzAOrgSXthFuBZN7zOsGxJ4ZGrVzHSlCH/jFLgObEizHrqisgL1cxKj8QvbGLUjNtUuTvR5IY6hwRLCxbliTa84BN10E0jC7hhAnnuEIAFJiwIDAQABo4IBjjCCAYowDAYDVR0TAQH/BAIwADAfBgNVHSMEGDAWgBRdiFut62X7/mii5NlvPVdyou8rmTBnBggrBgEFBQcBAQRbMFkwNQYIKwYBBQUHMAKGKWh0dHA6Ly9jcnQubGxhbWEucGUvbGxhbWFwZXN0YW5kYXJkY2EuY2VyMCAGCCsGAQUFBzABhhRodHRwOi8vb2NzcC5sbGFtYS5wZTAeBgNVHREEFzAVgRNybWV6YWdAc3VuYXQuZ29iLnBlMEYGA1UdIAQ/MD0wOwYNKwYBBAGDl3cAAQADATAqMCgGCCsGAQUFBwIBFhxodHRwczovL2xsYW1hLnBlL3JlcG9zaXRvcnkvMB0GA1UdJQQWMBQGCCsGAQUFBwMCBggrBgEFBQcDBDA6BgNVHR8EMzAxMC+gLaArhilodHRwOi8vY3JsLmxsYW1hLnBlL2xsYW1hcGVzdGFuZGFyZGNhLmNybDAdBgNVHQ4EFgQUuRkPCyM25gAu5se9GraC/UO07X8wDgYDVR0PAQH/BAQDAgbAMA0GCSqGSIb3DQEBCwUAA4IBAQBC8+YM7moZ7bKYCS+VzJ8wzydSboWeNuAs2CfkhI8hRMQr1r5WZg8pDlroCslF/r6SjbkrjuDHcGKJTM2riGEjlOD4CLU9VjOP7Td6CIZyJRLaz63pZYOwE0H0weG/PvYpopDZzJ6AXYzZxwYkJ03/x/vwaCss9ZvmsEn2E1xtGbnMe9MEsg8oF0ul3uRn8Qy5gF37fM7YKuF/r4iBS5uSvBcA5J2FbI/PQls7OgICDyb3W16GeluaT9krY5wQxilJSpGVU++nv5NzmRHkquH3ic2It/KP6MZ9X2tfg6FhpF6JaUz7MSY+J0KnDDcfJlhxgnkgoT5tV3Sr6z5PpQH6</X509Certificate><X509IssuerSerial><X509IssuerName>C=PE, O=LLAMA.PE, CN=Llama.pe SHA256 Standard CA</X509IssuerName><X509SerialNumber>9211231144834552139</X509SerialNumber></X509IssuerSerial></X509Data></KeyInfo><Proposito>Cumple proposito</Proposito><Revocacion>Cumple revocacion</Revocacion><TSL>Cumple tsl</TSL><Expiracion>No ha expirado</Expiracion></Signature></ext:ExtensionContent></ext:UBLExtension></ext:UBLExtensions>\n\t<cbc:UBLVersionID>2.0</cbc:UBLVersionID>\n\t<cbc:CustomizationID>1.0</cbc:CustomizationID>\n\t<cbc:ID><![CDATA[c98f9700-9147-4891-a9ec-99416fe2d5ba]]></cbc:ID>\n\t<cbc:IssueDate>2025-08-24</cbc:IssueDate>\n\t<cbc:IssueTime>03:43:06.881</cbc:IssueTime>\n\t<cbc:ResponseDate>2025-08-24</cbc:ResponseDate>\n\t<cbc:ResponseTime>03:43:07</cbc:ResponseTime>\n\t<cac:Signature>\n\t\t<cbc:ID><![CDATA[SignSUNAT]]></cbc:ID>\n\t\t<cac:SignatoryParty>\n\t\t\t<cac:PartyIdentification>\n\t\t\t\t<cbc:ID><![CDATA[20131312955]]></cbc:ID>\n\t\t\t</cac:PartyIdentification>\n\t\t\t<cac:PartyName>\n\t\t\t\t<cbc:Name><![CDATA[SUNAT]]></cbc:Name>\n\t\t\t</cac:PartyName>\n\t\t</cac:SignatoryParty>\n\t\t<cac:DigitalSignatureAttachment>\n\t\t\t<cac:ExternalReference>\n\t\t\t\t<cbc:URI>#SignSUNAT</cbc:URI>\n\t\t\t</cac:ExternalReference>\n\t\t</cac:DigitalSignatureAttachment>\n\t</cac:Signature>\n\t<cac:SenderParty>\n\t\t<cac:PartyIdentification>\n\t\t\t<cbc:ID><![CDATA[20131312955]]></cbc:ID>\n\t\t</cac:PartyIdentification>\n\t</cac:SenderParty>\n\t<cac:ReceiverParty>\n\t\t<cac:PartyIdentification>\n\t\t\t<cbc:ID><![CDATA[20100157315]]></cbc:ID>\n\t\t</cac:PartyIdentification>\n\t</cac:ReceiverParty>\n\t<cac:DocumentResponse>\n\t\t<cac:Response>\n\t\t\t<cbc:ReferenceID>TP01-2</cbc:ReferenceID>\n\t\t\t\t<cbc:ResponseCode>2555</cbc:ResponseCode>\n\t\t\t\t<cbc:Description><![CDATA[Destinatario no debe ser igual al remitente. : error: INFO : errorCode 2555 (nodo: "cac:PartyIdentification/cbc:ID" valor: "20100157315")]]></cbc:Description>\n\t\t</cac:Response>\n\t\t<cac:DocumentReference>\n\t\t\t<cbc:ID><![CDATA[TP01-2]]></cbc:ID>\n\t\t</cac:DocumentReference>\n\t\t<cac:RecipientParty>\n\t\t\t<cac:PartyIdentification>\n\t\t\t\t<cbc:ID><![CDATA[6-20100157315]]></cbc:ID>\n\t\t\t</cac:PartyIdentification>\n\t\t</cac:RecipientParty>\n\t</cac:DocumentResponse>\n</ar:ApplicationResponse>',
            #         'at_NombreXML': 'R-20100157315-09-TP01-2-1.xml',
            #         'at_FechaXML': '2025-08-24 03:43:09'
            #     }
            # }
            res = helpers.serialize_object(response)
            vals = {}
            vals['respuesta'] = {}
            if res.get('ent_ResultadoXML', {}).get('at_XML'):
                vals['estado'] = True
                vals['xml_firmado'] = encodebytes(res.get('ent_ResultadoXML', {}).get('at_XML'))
                xml = str(res.get('ent_ResultadoXML', {}).get('at_XML'), 'utf-8')
                sub = re.sub("<soap-env:Envelope.*/soap-env:Envelope>", "", xml, 1)
                print(sub)
            else:
                vals['estado'] = False
            return vals

        res = document_name.split("-")
        params = {
            'ent_ComprobanteConsultarXML': {
                'at_Numero': int(res[3]),
                'at_Serie': res[2],
                'at_NumeroRespuesta': 0
            },
            'at_NumeroDocumentoIdentidad': self.servidor.usuario,
            'ent_Autenticacion': {
                'at_Ruc': self.servidor.usuario,
            }
        }
        try:
            response = self.client.service.ConsultarXMLGRR(params)
            res = process_response(response)
        except Exception as e:
            respuesta = {
                'faultstring': str(e),
            }
            return {'estado': False, 'respuesta': respuesta, 'datos_respuesta': {}}
        return {'estado': True, 'respuesta': res, 'datos_respuesta': {}}

    def consulta_individual_gr(self, document_name):
        def process_response(response):
            # {
            #     'at_NivelResultado': 1,
            #     'at_MensajeResultado': 'El comprobante de Guia de Remisión TP01-2, se encuentra Pendiente de Otorgar y Pendiente de Leer',
            #     'ent_InformacionComprobante': {
            #         'at_FechaGeneracion': '2025-08-24 03:42:30',
            #         'at_FechaTransmision': '2025-08-24 03:43:05',
            #         'at_FechaOtorgamiento': None,
            #         'at_FechaReversion': None,
            #         'at_FechaLeido': None,
            #         'at_CodigoHash': '271dzar4QjMZpMZXm81YiZPts1Q=',
            #         'l_respuestas': {
            #             'en_Respuestas': [
            #                 {
            #                     'at_NroRespuesta': 1,
            #                     'at_CodigoRespuesta': '3',
            #                     'at_Descripcion': 'Rechazado',
            #                     'at_FechaSunat': '2025-08-24 03:43:09'
            #                 }
            #             ]
            #         }
            #     }
            # }
            return {}

        res = document_name.split("-")
        params = {
            'at_Numero': int(res[3]),
            'at_NumeroDocumentoIdentidad': self.servidor.usuario,
            'at_Serie': res[2],
            'ent_Autenticacion': {
                'at_Ruc': self.servidor.usuario,
            }
        }
        try:
            response = self.client.service.ConsultaIndividualGRR(params)
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
    servidor.setServidor({'servidor':'tci', 'url':'https://egestor.efacturacion.pe/WS_eCica_HTTPS/GuiaRemisionRemitente/ServicioGuiaRemisionRemitente.svc?wsdl', 'usuario':'20100157315', 'clave':'20100157315'})
    cliente = ClienteTCI(servidor)
    document_name = '20100157315-09-TP01-2'
    pdf_data = cliente.consultar_xml_gr(document_name)
    print(pdf_data)
