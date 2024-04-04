# -*- coding: utf-8 -*-
from io import BytesIO
import io
import zipfile
import base64

#from pysimplesoap.client import SoapClient, SoapFault

from zeep.wsse.username import UsernameToken
from zeep import Client, Settings
from zeep.transports import Transport
from pysimplesoap.client import SoapClient, SoapFault

from lxml import etree
import logging
import requests
import hashlib

log = logging.getLogger(__name__)


class Cliente(object):

    def __init__(self, servidor=None):
        self._servidor = servidor
        self._xml = None
        self._type = None
        self._document_name = None
        self._client = None
        self._response = None
        self._sunat_response = {}
        self._response_code = None
        self._zip_file = None
        self._response_status = None
        self._response_data = None
        self._ticket = None
        self._hashqr = None
        self.in_memory_data = BytesIO()
        self.in_memory_zip = zipfile.ZipFile(self.in_memory_data, "w", zipfile.ZIP_DEFLATED, False)

    def generaArchivoZip(self, filename, filecontent):
        self.in_memory_zip.writestr(filename, filecontent)

    def preparaZip(self):
        self._zip_filename = '{}.zip'.format(self._document_name)
        xml_filename = '{}.xml'.format(self._document_name)
        self.generaArchivoZip(xml_filename, self._xml)
        for zfile in self.in_memory_zip.filelist:
            zfile.create_system = 0
        self.in_memory_zip.close()

    def enviar(self):
        if self._type in ["sync", "guia"] and not self._ticket:
            self._zip_file = base64.b64encode(self.in_memory_data.getvalue())
            self._hashqr = hashlib.sha256(self.in_memory_data.getvalue()).hexdigest()
            self._response_status, self._response = self._client.send_bill(self._zip_filename, self._zip_file, self._hashqr)
        elif self._type in ["ticket", "guia"]:
            self._response_status, self._response = self._client.get_status(self._ticket)
        elif self._type == "status":
            self._response_status, self._response = self._client.get_status_cdr(self._document_name)
        else:
            self._zip_file = base64.b64encode(self.in_memory_data.getvalue())
            self._response_status, self._response = self._client.send_summary(self._zip_filename, self._zip_file)

    def generarHashqr(self, document_name=None, xml=None):
        if document_name:
            self._document_name = document_name
        if xml:
            self._xml = xml
        if not self.in_memory_data:
            self.preparaZip()
        hashqr = hashlib.sha256(self.in_memory_data.getvalue()).hexdigest()
        return hashqr

    def procesarRespuesta(self):
        if not self._response:
            if self._response_status:
                self._response_status = False
        elif self._response.get('applicationResponse'):
            self._response_data = self._response['applicationResponse']
            try:
                xml_filename = 'R-%s.xml' % (self._document_name)
                codigo, descripcion, respuesta, nota, documento = self.obtenerRespuesta(self._response_data, xml_filename)
                self._sunat_response.update(
                    {'codigo': codigo, 'descripcion': descripcion, 'respuesta': respuesta, 'nota': nota, 'documento': documento})
            except Exception:
                pass
        elif self._response.get('status', {}).get('content'):
            self._response_data = self._response['status']['content']
            try:
                xml_filename = 'R-%s.xml' % (self._document_name)
                codigo, descripcion, respuesta, nota, documento = self.obtenerRespuesta(self._response_data, xml_filename)
                self._sunat_response.update(
                    {'codigo': codigo, 'descripcion': descripcion, 'respuesta': respuesta, 'nota': nota, 'documento': documento})
            except Exception:
                pass
        elif self._response.get('statusCdr', {}).get('content', None):
            self._response_data = self._response.get('statusCdr', {}).get('content', None)
            try:
                xml_filename = 'R-%s.xml' % (self._document_name)
                codigo, descripcion, respuesta, nota, documento = self.obtenerRespuesta(self._response_data, xml_filename)
                self._sunat_response.update(
                    {'codigo': codigo, 'descripcion': descripcion, 'respuesta': respuesta, 'nota': nota, 'documento': documento})
            except Exception:
                pass
        elif self._response.get('arcCdr'):
            self._response_data = self._response.get('arcCdr')
            try:
                xml_filename = 'R-%s.xml' % (self._document_name)
                codigo, descripcion, respuesta, nota, documento = self.obtenerRespuesta(self._response_data, xml_filename)
                self._sunat_response.update(
                    {'codigo': codigo, 'descripcion': descripcion, 'respuesta': respuesta, 'nota': nota, 'documento':documento})
            except Exception:
                pass
        elif self._response.get('ticket'):
            self._response_data = self._response['ticket']
        elif self._response.get('numTicket'):
            self._sunat_response = {"hashqr": self._hashqr}
            self._response_data = self._response['numTicket']
        elif self._response.get('status') and self._response.get('status', {}).get('statusCode'):
            res = self._response
            self._response_status = False
            self._sunat_response = {'faultcode': res['status'].get('statusCode', False), 'faultstring': ""}
        elif self._response.get('statusCdr', {}).get('statusCode', False):
            self._response_status = False
            self._sunat_response = {'faultcode': self._response.get('statusCdr', {}).get('statusCode', False),
                                    'faultstring': self._response.get('statusCdr', {}).get('statusMessage', False)}
        elif self._response.get('faultcode'):
            self._response_status = False
            self._sunat_response = {'faultcode': self._response.get('faultcode'),
                                    "faultstring": self._response.get('faultstring', "")}
        elif self._response.get('error'):
            self._response_status = False
            self._sunat_response = {'faultcode': '',
                                    "faultstring": str(self._response.get('error', ""))}

    def procesar(self, document_name, type, xml, client):
        self._xml = xml
        self._type = type
        self._document_name = document_name
        self._client = client
        self.preparaZip()
        self.enviar()
        self.procesarRespuesta()
        return self._zip_file, self._response_status, self._sunat_response, self._response_data

    def obtenerRespuesta(self, file, name):
        zf = zipfile.ZipFile(BytesIO(base64.b64decode(file)))
        xml = zf.open(name).read()
        res = self.obtenerRespuestaXML(xml)
        res_code = res.get('codigo')
        description = res.get('descripcion')
        response = res.get('respuesta')
        note = res.get('nota')
        document_desc = res.get('documento_desc')
        zf.close()
        return res_code, description, response, note, document_desc

    @staticmethod
    def obtenerRespuestaXML(xml):
        sunat_response = etree.fromstring(xml)
        cbc = 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
        # tag = etree.QName(cbc, 'ResponseDate')
        # date=sunat_response.find('.//'+tag.text)
        # tag = etree.QName(cbc, 'ResponseTime')
        # time= sunat_response.find('.//'+tag.text)
        # if time!=-1 and date!=-1:
        #    self.date_end = fields.Datetime.context_timestamp(self, datetime.now())
        tag = etree.QName(cbc, 'ResponseCode')
        code = sunat_response.find('.//' + tag.text)
        res_code = ""
        if code != -1:
            res_code = "%04d" % int(code.text)
        tag = etree.QName(cbc, 'Description')
        description = sunat_response.find('.//' + tag.text)
        res_desc = ""
        if description != -1:
            res_desc = description.text
        response = "%s - %s" % (res_code, res_desc)
        notes = sunat_response.xpath(".//cbc:Note", namespaces={
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
        res_note = ""
        tag = etree.QName(cbc, 'DocumentDescription')
        documento = sunat_response.find('.//' + tag.text)
        documento_desc = ""
        if documento != -1:
            documento_desc = documento.text
        for note in notes:
            res_note += note.text + "\n"
        note = res_note

        return {'codigo': res_code, 'descripcion': description, 'respuesta': response, 'nota': note, 'documento_desc': documento_desc}

    def get_status(self, document_name, type, client, ticket=None):
        # self._type="ticket"
        self._ticket = ticket
        self._type = type
        self._document_name = document_name
        self._client = client
        self.enviar()
        self.procesarRespuesta()
        return self._zip_file, self._response_status, self._sunat_response, self._response_data

    def get_status_cdr(self, document_name, client):
        self._type = "status"
        self._client = client
        self._document_name = document_name
        self.enviar()
        self.procesarRespuesta()
        return self._response_status, self._response, self._response_data


class ClienteCpe(object):

    def __init__(self, ruc, servidor=None, tipo=None):
        self.servidor = servidor
        self.tipo = tipo
        if servidor:
            if servidor.servidor in ['sunat', 'nubefact_ose']:
                self._username = "%s%s" % (ruc, servidor.usuario)
            else:
                self._username = servidor.usuario
            self._password = servidor.clave
            self._version = 'v1'
            self._url2 = BytesIO(b'''

            <wsdl:definitions xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" xmlns:soap11="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:soap12="http://schemas.xmlsoap.org/wsdl/soap12/" xmlns:http="http://schemas.xmlsoap.org/wsdl/http/" xmlns:mime="http://schemas.xmlsoap.org/wsdl/mime/" xmlns:wsp="http://www.w3.org/ns/ws-policy" xmlns:wsp200409="http://schemas.xmlsoap.org/ws/2004/09/policy" xmlns:wsp200607="http://www.w3.org/2006/07/ws-policy" xmlns:ns0="http://service.gem.factura.comppago.registro.servicio.sunat.gob.pe/" xmlns:ns1="http://service.sunat.gob.pe" xmlns:ns2="http://www.datapower.com/extensions/http://schemas.xmlsoap.org/wsdl/soap12/" targetNamespace="http://service.gem.factura.comppago.registro.servicio.sunat.gob.pe/">
            <wsdl:import location="https://e-factura.sunat.gob.pe/ol-ti-itcpfegem/billService?ns1.wsdl" namespace="http://service.sunat.gob.pe"/>
            <wsdl:binding name="BillServicePortBinding" type="ns1:billService">
                <soap11:binding transport="http://schemas.xmlsoap.org/soap/http" style="document"/>
                <wsdl:operation name="getStatus">
                <soap11:operation soapAction="urn:getStatus" style="document"/>
                <wsdl:input name="getStatusRequest">
                    <soap11:body use="literal"/>
                </wsdl:input>
                <wsdl:output name="getStatusResponse">
                    <soap11:body use="literal"/>
                </wsdl:output>
                </wsdl:operation>
                <wsdl:operation name="sendBill">
                <soap11:operation soapAction="urn:sendBill" style="document"/>
                <wsdl:input name="sendBillRequest">
                    <soap11:body use="literal"/>
                </wsdl:input>
                <wsdl:output name="sendBillResponse">
                    <soap11:body use="literal"/>
                </wsdl:output>
                </wsdl:operation>
                <wsdl:operation name="sendPack">
                <soap11:operation soapAction="urn:sendPack" style="document"/>
                <wsdl:input name="sendPackRequest">
                    <soap11:body use="literal"/>
                </wsdl:input>
                <wsdl:output name="sendPackResponse">
                    <soap11:body use="literal"/>
                </wsdl:output>
                </wsdl:operation>
                <wsdl:operation name="sendSummary">
                <soap11:operation soapAction="urn:sendSummary" style="document"/>
                <wsdl:input name="sendSummaryRequest">
                    <soap11:body use="literal"/>
                </wsdl:input>
                <wsdl:output name="sendSummaryResponse">
                    <soap11:body use="literal"/>
                </wsdl:output>
                </wsdl:operation>
            </wsdl:binding>
            <wsdl:service name="billService">
                <wsdl:port name="BillServicePort" binding="ns0:BillServicePortBinding">
                <soap11:address location="https://e-factura.sunat.gob.pe:443/ol-ti-itcpfegem/billService"/>
                </wsdl:port>
                <wsdl:port name="BillServicePort.0" binding="ns2:BillServicePortBinding">
                <soap12:address location="https://e-factura.sunat.gob.pe:443/ol-ti-itcpfegem/billService"/>
                </wsdl:port>
                <wsdl:port name="BillServicePort.3" binding="ns0:BillServicePortBinding">
                <soap11:address location="https://e-factura.sunat.gob.pe:443/ol-ti-itcpfegem/billService"/>
                </wsdl:port>
            </wsdl:service>
            </wsdl:definitions>''')
            self._url = servidor.url
            self._clientePython = servidor.clientePython
            self._api_id = servidor.idCliente
            self._api_clave = servidor.claveCliente
            if tipo != 'guia':
                self._connect()
        self._method = ""
        self._token = ""
        self._service = ""
        level = logging.DEBUG
        logging.basicConfig(level=level)
        log.setLevel(level)

    def _get_envio_guia(self):
        # "https://api-cpe.sunat.gob.pe/v1/contribuyente/gem/comprobantes/{numRucEmisor}-{codCpe}-{numSerie}-{numCpe}"
        # "https://api-cpe.sunat.gob.pe/v1/contribuyente/gem/comprobantes/envios/{numTicket}"
        return "%s/contribuyente/gem/comprobantes/%s" % (self._version, self._service)

    @staticmethod
    def _get_response(response):
        try:
            log.debug(response)
            log.debug(str(response.url))
            res = response.json()
            log.debug(res)
            if response.status_code not in [200, 201]:
                return False, {'error': str(res)}
            return True, res
        except Exception:
            return False, {'error': response.text}

    @staticmethod
    def _process_soap_response(soap_response):
        if not soap_response:
            return {}
        response_tree = etree.fromstring(soap_response)
        if response_tree.find('.//{*}Fault') is not None:
            message_element = response_tree.find('.//{*}faultstring')
            code_element = response_tree.find('.//{*}faultcode')
            code = False
            if code_element is not None:
                code_parsed = code_element.text.split('.')
                if code_parsed:
                    code = code_parsed[-1]
            message = message_element.text
            return {'faultcode': code, 'faultstring': message}
        if response_tree.find('.//{*}sendBillResponse') is not None:
            applicationResponse = response_tree.find('.//{*}applicationResponse').text
            return {'applicationResponse': applicationResponse}
        if response_tree.find('.//{*}getStatusResponse') is not None:
            content = response_tree.find('.//{*}content').text
            return {'status': {'content': content}}

        if response_tree.find('.//{*}sendSummaryResponse') is not None:
            ticket = response_tree.find('.//{*}ticket').text
            return {'ticket': ticket}
        if response_tree.find('.//{*}getStatusCdrResponse') is not None:
            code = response_tree.find('.//{*}statusCode').text
            message = response_tree.find('.//{*}statusMessage').text
            if response_tree.find('.//{*}content') is not None:
                content = response_tree.find('.//{*}content').text
                return {'statusCdr': {'content': content}}

            else:
                return {'faultcode': code, 'faultstring': message}

        return {}

    @staticmethod
    def _get_header(token):
        headers = {}
        headers['Authorization'] = "Bearer %s" % token
        headers['Content-Type'] = 'application/json'
        return headers

    def _get_token(self):
        url = "https://api-seguridad.sunat.gob.pe/%s/clientessol/%s/oauth2/token/" % (self._version, self._api_id)
        params = {
            "grant_type":"password",
            "client_id": self._api_id,
            "client_secret": self._api_clave,
            "username": self._username,
            "password": self._password,
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(url, params, headers=headers)
        status, values = self._get_response(response)
        token = False
        if status:
            token = values.get("access_token")
        return status, token or values

    def _connect(self):
        if self.tipo != 'guia':
            if self._clientePython == 'pysimplesoap':
                try:
                    self._client = SoapClient(wsdl=self._url, cache=None, ns='tzmed', soap_ns='soapenv',
                                              soap_server="jbossas6",
                                              trace=True)  # SoapClient(location=self._location, action= self._soapaction, namespace=self._namespace)
                    self._client['wsse:Security'] = {
                        'wsse:UsernameToken': {
                            'wsse:Username': self._username,
                            'wsse:Password': self._password
                        }
                    }
                except Exception:
                    self._client = False
            elif self._clientePython == 'zeep':
                try:
                    settings = Settings(raw_response=True)
                    transport = Transport(operation_timeout=15, timeout=15)
                    client = Client(wsdl=self._url, wsse=UsernameToken(self._username, self._password),  settings=settings, transport=transport)
                    self._client = client.service
                except Exception as e:
                    self._client = False
            else:
                self._client = False

    def _call_service(self, name, params):
        if self.tipo == 'guia':
            url = self._url + self._get_envio_guia()
            log.debug(params)
            status, token = self._get_token()
            if not status:
                return status, token
            headers = self._get_header(token)
            try:
                if params:
                    response = requests.post(url, json=params, headers=headers)
                else:
                    response = requests.get(url, headers=headers)
                return self._get_response(response)
            except Exception:
                return False, {}
        if not self._client:
            return False, {}
        if self._clientePython == 'pysimplesoap':
            try:
                service = getattr(self._client, name)
                return True, service(**params)
            except SoapFault as ex:
                return False, {'faultcode': ex.faultcode, 'faultstring': ex.faultstring}
            except Exception as e:
                return False, {}
        elif self._clientePython == 'zeep':
            try:
                service = getattr(self._client, name)
                result = service(**params)
                result.raise_for_status()
                log.info(result.content)
                response = self._process_soap_response(result.content)
                if response:
                    if response.get('faultstring'):
                        return False, response
                    return True, response
                else:
                    return False, response
            except Exception as e:
                return False, {}

    def send_bill(self, filename, content_file, hash=None):
        if self.tipo == 'guia':
            self._service = "%s" % filename.split(".")[0]
            params = {
                "archivo": {
                    "nomArchivo": filename,
                    "arcGreZip": str(content_file, 'utf-8'),
                    "hashZip": hash
                }
            }
        else:
            params = {
                'fileName': filename,
                'contentFile': self._clientePython == 'zeep' and base64.decodebytes(content_file) or str(content_file, 'utf-8')
            }
            if self._clientePython == 'zeep' and not self._client:
                try:
                    settings = Settings(raw_response=True)
                    transport = Transport(operation_timeout=700, timeout=700)
                    client = Client(wsdl=self._url2, wsse=UsernameToken(self._username, self._password),
                                    settings=settings,
                                    transport=transport)
                    self._client = client.service
                except Exception as e:
                    self._client = False
        return self._call_service('sendBill', params)

    def send_summary(self, filename, content_file):
        params = {
            'fileName': filename,
            'contentFile': self._clientePython == 'zeep' and base64.decodebytes(content_file) or str(content_file, 'utf-8')
        }
        if self._clientePython == 'zeep' and not self._client:
            try:
                settings = Settings(raw_response=True)
                transport = Transport(operation_timeout=700, timeout=700)
                client = Client(wsdl=self._url2, wsse=UsernameToken(self._username, self._password), settings=settings,
                                transport=transport)
                self._client = client.service
            except Exception as e:
                self._client = False
        return self._call_service('sendSummary', params)

    def get_status(self, ticket_code):
        if self.tipo != 'guia':
            params = {
                'ticket': ticket_code
            }
            if self._clientePython == 'zeep' and not self._client:
                try:
                    settings = Settings(raw_response=True)
                    transport = Transport(operation_timeout=700, timeout=700)
                    client = Client(wsdl=self._url2, wsse=UsernameToken(self._username, self._password),
                                    settings=settings,
                                    transport=transport)
                    self._client = client.service
                except Exception as e:
                    self._client = False
        else:
            self._service = "envios/%s" % ticket_code
            params = {}
        return self._call_service('getStatus', params)

    def get_status_cdr(self, document_name):
        res = document_name.split("-")
        params = {
            'rucComprobante': res[0],
            'tipoComprobante': res[1],
            'serieComprobante': res[2],
            'numeroComprobante': res[3]
        }
        return self._call_service('getStatusCdr', params)
