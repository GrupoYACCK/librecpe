from zeep.wsse.username import UsernameToken
from zeep import Client, Settings
from zeep.transports import Transport
from .tci import TCI
from base64 import encodebytes

class ClienteTCI:
    def __init__(self, servidor):
        self.servidor = servidor
        self.client = self._crear_cliente()

    def _crear_cliente(self):
        settings = Settings(strict=False)
        transport = Transport()
        # transport.session.verify = False
        return Client(self.servidor.url, transport=transport, settings=settings)

    def obtener_pdf(self, document_name):
        res = document_name.split("-")

        def process_response(response):
            try:
                vals = {
                    'NombrePDF': response.Obtener_PDFResult.NombrePDF,
                    'ArchivoPDF': response.Obtener_PDFResult.ArchivoPDF
                }
                return vals
            except Exception as e:
                return {'error': str(response)}

        params = {
            'Numero': res[3],
            'Ruc': self.servidor.usuario,
            'Serie': res[2],
            'TipoComprobante': res[1],
            'Autenticacion': {
                'Ruc': self.servidor.usuario,
            }
        }
        response = self.client.service.Obtener_PDF(params)
        return process_response(response)

    def registrar(self, documento):
        def process_response(response):
            vals = {}
            if response.RegistrarResult:
                vals['estado'] = True
            else:
                vals['estado'] = False
            vals['respuesta'] = {}
            vals['respuesta']['Cadena'] = response.Cadena
            vals['respuesta']['CodigoBarras'] = response.CodigoBarras and encodebytes(response.CodigoBarras) or response.CodigoBarras
            error = []
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
            response = self.client.service.Registrar(params, Otorgar=1)
            return process_response(response)
        except Exception as e:
            respuesta = {
                'faultcode': e.code,
                'faultstring': e.message,
            }
            return {'estado': False, 'respuesta': respuesta, 'datos_respuesta': {}}

    def registrar_comunicacion_baja(self, documento):
        tci = TCI(documento)
        params = tci.get_documento()
        response = self.client.service.RegistrarComunicacionBaja(params)
        return response

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
