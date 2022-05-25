from collections import OrderedDict
from lxml import etree
import re 


class Ubl21:
    
    def __init__(self, documento = None):
        self.documento = documento
        self._root = None
        self._cac = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        self._cbc = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        self._ccts = "urn:un:unece:uncefact:documentation:2"
        self._ds = "http://www.w3.org/2000/09/xmldsig#"
        self._ext = "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        self._qdt = "urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2"
        self._sac = "urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1"
        self._udt = "urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2"
        self._xsi = "http://www.w3.org/2001/XMLSchema-instance"
    
    def _getX509Template(self):
        tag = etree.QName(self._ext, 'UBLExtensions')
        extensions=etree.SubElement(self._root, tag.text, nsmap={'ext':tag.namespace})
        
        tag = etree.QName(self._ext, 'UBLExtension')
        extension=etree.SubElement(extensions, tag.text, nsmap={'ext':tag.namespace})
        
        tag = etree.QName(self._ext, 'ExtensionContent')
        content=etree.SubElement(extension, tag.text, nsmap={'ext':tag.namespace})
        tag = etree.QName(self._ds, 'Signature')   
        signature=etree.SubElement(content, tag.text, Id="signatureGrupoYACCK", nsmap={'ds':tag.namespace})
        tag = etree.QName(self._ds, 'SignedInfo')   
        signed_info=etree.SubElement(signature, tag.text, nsmap={'ds':tag.namespace})
        tag = etree.QName(self._ds, 'CanonicalizationMethod')   
        etree.SubElement(signed_info, tag.text, Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315", nsmap={'ds':tag.namespace})
        tag = etree.QName(self._ds, 'SignatureMethod')   
        etree.SubElement(signed_info, tag.text, Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1", nsmap={'ds':tag.namespace})
        tag = etree.QName(self._ds, 'Reference')   
        reference=etree.SubElement(signed_info, tag.text, URI="", nsmap={'ds':tag.namespace})
        tag = etree.QName(self._ds, 'Transforms')   
        transforms=etree.SubElement(reference, tag.text, nsmap={'ds':tag.namespace})
        tag = etree.QName(self._ds, 'Transform')   
        etree.SubElement(transforms, tag.text, Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature", nsmap={'ds':tag.namespace})
        tag = etree.QName(self._ds, 'DigestMethod')   
        etree.SubElement(reference, tag.text, Algorithm="http://www.w3.org/2000/09/xmldsig#sha1", nsmap={'ds':tag.namespace})
        tag = etree.QName(self._ds, 'DigestValue')   
        etree.SubElement(reference, tag.text, nsmap={'ds':tag.namespace})
        tag = etree.QName(self._ds, 'SignatureValue')   
        etree.SubElement(signature, tag.text, nsmap={'ds':tag.namespace})
        tag = etree.QName(self._ds, 'KeyInfo')   
        key_info=etree.SubElement(signature, tag.text, nsmap={'ds':tag.namespace})
        tag = etree.QName(self._ds, 'X509Data')   
        data=etree.SubElement(key_info, tag.text, nsmap={'ds':tag.namespace})
        tag = etree.QName(self._ds, 'X509SubjectName')   
        etree.SubElement(data, tag.text, nsmap={'ds':tag.namespace})
        tag = etree.QName(self._ds, 'X509Certificate')   
        etree.SubElement(data, tag.text, nsmap={'ds':tag.namespace})
    
    def _getFirma(self):
        #es parte de la firma
        tag = etree.QName(self._cac, 'Signature')   
        signature=etree.SubElement(self._root, tag.text, nsmap={'cac':tag.namespace})
        tag = etree.QName(self._cbc, 'ID')   
        etree.SubElement(signature, tag.text, nsmap={'cbc':tag.namespace}).text= self.documento.numero
        tag = etree.QName(self._cac, 'SignatoryParty')   
        party=etree.SubElement(signature, tag.text, nsmap={'cac':tag.namespace})
        tag = etree.QName(self._cac, 'PartyIdentification')   
        identification=etree.SubElement(party, tag.text, nsmap={'cac':tag.namespace})
        tag = etree.QName(self._cbc, 'ID')   
        etree.SubElement(identification, tag.text, nsmap={'cbc':tag.namespace}).text=self.documento.emisor.numDocumento
        tag = etree.QName(self._cac, 'PartyName')   
        name=etree.SubElement(party, tag.text, nsmap={'cac':tag.namespace})
        tag = etree.QName(self._cbc, 'Name')   
        etree.SubElement(name, tag.text, nsmap={'cbc':tag.namespace}).text= self.documento.emisor.nombre
        tag = etree.QName(self._cac, 'DigitalSignatureAttachment')   
        attachment=etree.SubElement(signature, tag.text, nsmap={'cac':tag.namespace})
        tag = etree.QName(self._cac, 'ExternalReference')   
        reference=etree.SubElement(attachment, tag.text, nsmap={'cac':tag.namespace})
        tag = etree.QName(self._cbc, 'URI')   
        etree.SubElement(reference, tag.text, nsmap={'cbc':tag.namespace}).text="#signatureGrupoYACCK" 
    
    def _nsmap(self, documento):
        nsmap = OrderedDict([(None, "urn:oasis:names:specification:ubl:schema:xsd:%s" % documento),
                            ('cac', self._cac), ('cbc', self._cbc), ('ccts', self._ccts),
                            ('ds', self._ds), ('ext', self._ext), ('qdt', self._qdt), ('sac', self._sac), ('udt', self._udt),
                            ('xsi', self._xsi)])
        return nsmap
    
    
    def _getDocumento(self):
        etree.SubElement(self._root, "{%s}%s" % (self._cbc, 'ID'), nsmap={'cbc':self._cbc}).text = self.documento.numero or ''
        etree.SubElement(self._root, "{%s}%s" % (self._cbc, 'IssueDate'), nsmap={'cbc':self._cbc}).text = self.documento.fecEmision.strftime("%Y-%m-%d")
        if self.documento.tipoDocumento  not in ['09']:
            etree.SubElement(self._root, "{%s}%s" % (self._cbc, 'IssueTime'), nsmap={'cbc':self._cbc}).text = self.documento.fecEmision.strftime("%H:%M:%S")
        if self.documento.tipoDocumento  in ['01', '03']:
            if self.documento.fecVencimiento:
                etree.SubElement(self._root, "{%s}%s" % (self._cbc, 'DueDate'), nsmap={'cbc':self._cbc}).text = self.documento.fecVencimiento or ''
            etree.SubElement(self._root, "{%s}%s" % (self._cbc, 'InvoiceTypeCode'), listID=self.documento.tipOperacion, listAgencyName="PE:SUNAT", listName="Tipo de Documento" ,
                             listURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo01", nsmap={'cbc':self._cbc}).text = self.documento.tipoDocumento
        if self.documento.tipoDocumento  in ['09']:
            tag = etree.QName(self._cbc, 'DespatchAdviceTypeCode')   
            etree.SubElement(self._root, tag.text, nsmap={'cbc':tag.namespace}).text='09'
            if self.documento.observacion:
                tag = etree.QName(self._cbc, 'Note')   
                etree.SubElement(self._root, tag.text, nsmap={'cbc':tag.namespace}).text=self.documento.observacion or '-'
        # Leyenda
        if self.documento.tipoDocumento  not in ['09']:
            for leyenda in self.documento.leyendas:
                tag = etree.QName(self._cbc, 'Note')
                etree.SubElement(self._root, tag.text, languageLocaleID=leyenda.codLeyenda, nsmap={'cbc':tag.namespace}).text = leyenda.desLeyenda
            
            etree.SubElement(self._root, "{%s}%s" % (self._cbc, 'DocumentCurrencyCode'), listID='ISO 4217 Alpha', listName='Currency', listAgencyName='United Nations Economic Commission for Europe',
                             nsmap={'cbc':self._cbc}).text = self.documento.tipMoneda
        
            tag = etree.QName(self._cbc, 'LineCountNumeric')
            etree.SubElement(self._root, tag.text, nsmap={'cbc':tag.namespace}).text = str(len(self.documento.detalles))
            
            if self.documento.referencia and self.documento.tipoDocumento in ['01', '03']:
                ref = self.documento.referencia.replace(" ","").replace("-","").replace("/","")
                if ref and re.match(r'^[a-zA-Z0-9]*$', ref):
                    tag = etree.QName(self._cac, 'OrderReference')   
                    order=etree.SubElement(self._root, tag.text, nsmap={'cac':tag.namespace})
                    tag = etree.QName(self._cbc, 'ID')
                    etree.SubElement(order, tag.text, nsmap={'cbc':tag.namespace}).text=ref
            if self.documento.tipoDocumento in ['01', '03']:
                for guia in self.documento.guias:
                    despatch = etree.SubElement(self._root, "{%s}%s" % (self._cac, 'DespatchDocumentReference'), nsmap={'cac':self._cac})
                    etree.SubElement(despatch, "{%s}%s" % (self._cbc, 'ID'), nsmap={'cbc':self._cbc}).text = guia.numero
                    etree.SubElement(despatch, "{%s}%s" % (self._cbc, 'DocumentTypeCode'), listAgencyName="PE:SUNAT",
                                     listName="Tipo de Documento", listURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo01",
                                     nsmap={'cbc':self._cbc}).text = guia.tipoDocumento

    def _getDetraccion(self):
        if self.documento.detraccion:
            payment = etree.SubElement(self._root, "{%s}%s" % (self._cac, 'PaymentMeans'), nsmap={'cac': self._cac})
            etree.SubElement(payment, "{%s}%s" % (self._cbc, 'ID'), nsmap={'cbc': self._cbc}).text = 'Detraccion'
            etree.SubElement(payment, "{%s}%s" % (self._cbc, 'PaymentMeansCode'),
                             nsmap={'cbc': self._cbc}).text = self.documento.detraccion.medioPago

            payee = etree.SubElement(payment, "{%s}%s" % (self._cac, 'PayeeFinancialAccount'), nsmap={'cac': self._cac})
            etree.SubElement(payee, "{%s}%s" % (self._cbc, 'ID'),
                             nsmap={'cbc': self._cbc}).text = self.documento.detraccion.cuentaBanco

            payment = etree.SubElement(self._root, "{%s}%s" % (self._cac, 'PaymentTerms'), nsmap={'cac': self._cac})
            #etree.SubElement(payment, "{%s}%s" % (self._cbc, 'ID'), nsmap={'cbc': self._cbc}).text = 'Detraccion'
            etree.SubElement(payment, "{%s}%s" % (self._cbc, 'PaymentMeansID'),
                             nsmap={'cbc': self._cbc}).text = self.documento.detraccion.codigo

            etree.SubElement(payment, "{%s}%s" % (self._cbc, 'PaymentPercent'),
                             nsmap={'cbc': self._cbc}).text = str(self.documento.detraccion.procentaje)

            etree.SubElement(payment, "{%s}%s" % (self._cbc, 'Amount'), currencyID=self.documento.tipMoneda,
                             nsmap={'cbc': self._cbc}).text = str(self.documento.detraccion.monto)

    def _getMedioPago(self):
        if (self.documento.tipoDocumento in ['07'] and self.documento.medioPago.tipo == 'Credito') or self.documento.tipoDocumento not in ['07']:
            payment = etree.SubElement(self._root, "{%s}%s" % (self._cac, 'PaymentTerms'), nsmap={'cac':self._cac})
            etree.SubElement(payment, "{%s}%s" % (self._cbc, 'ID'), nsmap={'cbc':self._cbc}).text = 'FormaPago'
            etree.SubElement(payment, "{%s}%s" % (self._cbc, 'PaymentMeansID'), nsmap={'cbc':self._cbc}).text = self.documento.medioPago.tipo
        if self.documento.medioPago.tipo == 'Credito':
            etree.SubElement(payment, "{%s}%s" % (self._cbc, 'Amount'), currencyID=self.documento.tipMoneda, 
                         nsmap={'cbc':self._cbc}).text= str(self.documento.medioPago.monto)
            i=1
            for cuota in self.documento.medioPago.cuotas:
                payment = etree.SubElement(self._root, "{%s}%s" % (self._cac, 'PaymentTerms'), nsmap={'cac':self._cac})
                etree.SubElement(payment, "{%s}%s" % (self._cbc, 'ID'), nsmap={'cbc':self._cbc}).text = 'FormaPago'
                etree.SubElement(payment, "{%s}%s" % (self._cbc, 'PaymentMeansID'), nsmap={'cbc':self._cbc}).text = "Cuota%03d" % i
                etree.SubElement(payment, "{%s}%s" % (self._cbc, 'Amount'), currencyID=self.documento.tipMoneda, 
                             nsmap={'cbc':self._cbc}).text= str(cuota.monto)
                etree.SubElement(payment, "{%s}%s" % (self._cbc, 'PaymentDueDate'), 
                             nsmap={'cbc':self._cbc}).text= str(cuota.fecha)
                i+=1
    
    def _getEmisor(self):
        emisor = self.documento.emisor
        if self.documento.tipoDocumento in ['09']:
            tag = etree.QName(self._cac, 'DespatchSupplierParty')
            supplier=etree.SubElement(self._root, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cbc, 'CustomerAssignedAccountID')   
            etree.SubElement(supplier, tag.text, schemeID=emisor.tipoDocumento,
                             nsmap={'cbc':tag.namespace}).text=emisor.numDocumento
            
            tag = etree.QName(self._cac, 'Party')
            party=etree.SubElement(supplier, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cac, 'PartyLegalEntity')   
            party_name=etree.SubElement(party, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cbc, 'RegistrationName')   
            etree.SubElement(party_name, tag.text, nsmap={'cbc':tag.namespace}).text= etree.CDATA(emisor.nombre) 
        else:
            supplier = etree.SubElement(self._root, "{%s}%s" % (self._cac, 'AccountingSupplierParty'), nsmap={'cac':self._cac})
            party = etree.SubElement(supplier, "{%s}%s" % (self._cac, 'Party'), nsmap={'cac':self._cac})
            identification = etree.SubElement(party, "{%s}%s" % (self._cac, 'PartyIdentification'), nsmap={'cac':self._cac})
            etree.SubElement(identification, "{%s}%s" % (self._cbc, 'ID'), schemeID=emisor.tipoDocumento, schemeName="Documento de Identidad",
                             schemeAgencyName="PE:SUNAT", schemeURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo06", nsmap={'cbc':self._cbc}).text = emisor.numDocumento
            if emisor.nomComercial and emisor.nomComercial!='-':
                name = etree.SubElement(party, "{%s}%s" % (self._cac, 'PartyName'), nsmap={'cac':self._cac})
                etree.SubElement(name, "{%s}%s" % (self._cbc, 'Name'), nsmap={'cbc':self._cbc}).text = etree.CDATA(emisor.nomComercial)
            entity = etree.SubElement(party, "{%s}%s" % (self._cac, 'PartyLegalEntity'), nsmap={'cac':self._cac})
            etree.SubElement(entity, "{%s}%s" % (self._cbc, 'RegistrationName'), nsmap={'cbc':self._cbc}).text = etree.CDATA(emisor.nombre)
            
            address = etree.SubElement(entity, "{%s}%s" % (self._cac, 'RegistrationAddress'), nsmap={'cac':self._cac})
                        
            #Nuevo
            tag = etree.QName(self._cbc, 'ID')   
            etree.SubElement(address, tag.text, schemeAgencyName='PE:INEI', schemeName='Ubigeos', nsmap={'cbc':tag.namespace}).text=emisor.ubigeo
            
            etree.SubElement(address, "{%s}%s" % (self._cbc, 'AddressTypeCode'), nsmap={'cbc':self._cbc}).text = emisor.codEstablecimiento
            
            tag = etree.QName(self._cbc, 'CitySubdivisionName')   
            etree.SubElement(address, tag.text, nsmap={'cbc':tag.namespace}).text=etree.CDATA(emisor.urbanizacion or 'SN')
            tag = etree.QName(self._cbc, 'CityName')   
            etree.SubElement(address, tag.text, nsmap={'cbc':tag.namespace}).text=etree.CDATA(emisor.provincia)
            
            tag = etree.QName(self._cbc, 'CountrySubentity')   
            etree.SubElement(address, tag.text, nsmap={'cbc':tag.namespace}).text=etree.CDATA(emisor.region)
            
            tag = etree.QName(self._cbc, 'District')   
            etree.SubElement(address, tag.text, nsmap={'cbc':tag.namespace}).text=etree.CDATA(emisor.distrito)
            
            tag = etree.QName(self._cac, 'AddressLine')   
            address_line=etree.SubElement(address, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cbc, 'Line')   
            etree.SubElement(address_line, tag.text, nsmap={'cbc':tag.namespace}).text=etree.CDATA(emisor.direccion)
            
            tag = etree.QName(self._cac, 'Country')   
            country=etree.SubElement(address, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cbc, 'IdentificationCode')   
            etree.SubElement(country, tag.text, listID='ISO 3166-1', listAgencyName='United Nations Economic Commission for Europe', 
                             listName='Country', nsmap={'cbc':tag.namespace}).text=emisor.codPais
            
    
    def _getAdquirente(self, detalle = None, adquirente = None, tercero = None):
        if self.documento.tipoDocumento in ['09']:
            destinatario = tercero and self.documento.establecimientoTercero or  self.documento.destinatario
            if tercero:
                tag = etree.QName(self._cac, 'SellerSupplierParty')  
            else:
                tag = etree.QName(self._cac, 'DeliveryCustomerParty')   
            customer=etree.SubElement(self._root, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cbc, 'CustomerAssignedAccountID')   
            etree.SubElement(customer, tag.text, schemeID= destinatario.tipoDocumento or '-',
                             nsmap={'cbc':tag.namespace}).text= destinatario.numDocumento or '-'
            tag = etree.QName(self._cac, 'Party')  
            party=etree.SubElement(customer, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cac, 'PartyLegalEntity')   
            entity=etree.SubElement(party, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cbc, 'RegistrationName')   
            etree.SubElement(entity, tag.text, nsmap={'cbc':tag.namespace}).text= etree.CDATA(destinatario.nombre)
        else:
            adquirente = adquirente or self.documento.adquirente
            supplier = etree.SubElement(self._root, "{%s}%s" % (self._cac, 'AccountingCustomerParty'), nsmap={'cac':self._cac})
            party = etree.SubElement(supplier, "{%s}%s" % (self._cac, 'Party'), nsmap={'cac':self._cac})
            identification = etree.SubElement(party, "{%s}%s" % (self._cac, 'PartyIdentification'), nsmap={'cac':self._cac})
            etree.SubElement(identification, "{%s}%s" % (self._cbc, 'ID'), schemeID=adquirente.tipoDocumento, schemeName="Documento de Identidad",
                             schemeAgencyName="PE:SUNAT", schemeURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo06", nsmap={'cbc':self._cbc}).text = adquirente.numDocumento
            entity = etree.SubElement(party, "{%s}%s" % (self._cac, 'PartyLegalEntity'), nsmap={'cac':self._cac})
            etree.SubElement(entity, "{%s}%s" % (self._cbc, 'RegistrationName'), nsmap={'cbc':self._cbc}).text = etree.CDATA(adquirente.nombre)
            
            #if adquirente.direccion:
            #    address = etree.SubElement(entity, "{%s}%s" % (self._cac, 'RegistrationAddress'), nsmap={'cac':self._cac})
            #    etree.SubElement(address, "{%s}%s" % (self._cbc, 'Line'), nsmap={'cbc':self._cbc}).text = adquirente.direccion
            #if adquirente.urbanizacion:
            #    etree.SubElement(address, "{%s}%s" % (self._cbc, 'CitySubdivisionName'), nsmap={'cbc':self._cbc}).text = adquirente.urbanizacion
            #if adquirente.provincia:
            #    etree.SubElement(address, "{%s}%s" % (self._cbc, 'CityName'), nsmap={'cbc':self._cbc}).text = adquirente.provincia
            #if adquirente.ubigeo:
            #    etree.SubElement(address, "{%s}%s" % (self._cbc, 'ID'), schemeAgencyName="PE:INEI", schemeName="Ubigeos", nsmap={'cbc':self._cbc}).text = adquirente.ubigeo
            #if adquirente.region:
            #    etree.SubElement(address, "{%s}%s" % (self._cbc, 'CountrySubentity'), nsmap={'cbc':self._cbc}).text = adquirente.region
            #if adquirente.distrito:
            #    etree.SubElement(address, "{%s}%s" % (self._cbc, 'District'), nsmap={'cbc':self._cbc}).text = adquirente.distrito
            #if adquirente.codPais:
            #    country = etree.SubElement(address, "{%s}%s" % (self._cac, 'Country'), nsmap={'cac':self._cac})
            #    etree.SubElement(country, "{%s}%s" % (self._cbc, 'IdentificationCode'), listID="ISO 3166-1", listAgencyName="United Nations Economic Commission for Europe",
        #                     listName="Country", nsmap={'cbc':self._cbc}).text = adquirente.codPais
        

        # Falta otros
    # Falta Información adicional - Datos del sujeto que realiza la operación por cuenta del adquirente o usuario.
    def _getDocumentoRelacionado(self):
        if self.documento.tipoDocumento  in ['09']:
            for relacionado in self.documento.documentosRelacionados:
                tag = etree.QName(self._cac, 'AdditionalDocumentReference')
                reference= etree.SubElement(self._root, tag.text, nsmap={'cac':tag.namespace})
                tag = etree.QName(self._cbc, 'ID')   
                etree.SubElement(reference, tag.text, nsmap={'cbc':tag.namespace}).text=relacionado.numero
                tag = etree.QName(self._cbc, 'DocumentTypeCode')   
                etree.SubElement(reference, tag.text, nsmap={'cbc':tag.namespace}).text=relacionado.tipoDocumento
        
    def _getAnticipos(self):
        if self.documento.tipoDocumento  in ['01', '03']:
            i = 1
            for anticipo in self.documento.anticipos:
                tag = etree.QName(self._cac, 'AdditionalDocumentReference')   
                additional=etree.SubElement(self._root, tag.text, nsmap={'cac':tag.namespace})
                tag = etree.QName(self._cbc, 'ID')   
                etree.SubElement(additional, tag.text, schemeID=self.documento.tipoDocumento, nsmap={'cbc':tag.namespace}).text=anticipo.numero
                
                tag = etree.QName(self._cbc, 'DocumentTypeCode')
                etree.SubElement(additional, tag.text, listName='Documento Relacionado', listAgencyName='PE:SUNAT', 
                                 listURI='urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo12', nsmap={'cbc':tag.namespace}).text=anticipo.tipoCodigo
                
                tag = etree.QName(self._cbc, 'DocumentStatusCode')   
                etree.SubElement(additional, tag.text, listName="Anticipo", listAgencyName="PE:SUNAT",
                                 nsmap={'cbc':tag.namespace}).text=str(i)
                i+=1
                tag = etree.QName(self._cac, 'IssuerParty')   
                issuer_party=etree.SubElement(additional, tag.text, nsmap={'cac':tag.namespace})
                tag = etree.QName(self._cac, 'PartyIdentification')   
                party=etree.SubElement(issuer_party, tag.text, nsmap={'cac':tag.namespace})
                
                tag = etree.QName(self._cbc, 'ID')   
                etree.SubElement(party, tag.text, schemeID=self.documento.emisor.tipoDocumento, schemeName='Documento de Identidad', 
                                 schemeAgencyName='PE:SUNAT', schemeURI='urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo06', 
                                 nsmap={'cbc':tag.namespace}).text=self.documento.emisor.numDocumento
    
    def _getMontoAnticipos(self):
        if self.documento.tipoDocumento  in ['01', '03']:
            i = 1
            for anticipo in self.documento.anticipos:
                tag = etree.QName(self._cac, 'PrepaidPayment')   
                prepaid = etree.SubElement(self._root, tag.text, nsmap={'cac':tag.namespace})
                tag = etree.QName(self._cbc, 'ID')
                etree.SubElement(prepaid, tag.text, schemeName='Anticipo', schemeAgencyName='PE:SUNAT', nsmap={'cbc':tag.namespace}).text= str(i) # line.move_name
                i+=1
                tag = etree.QName(self._cbc, 'PaidAmount')
                etree.SubElement(prepaid, tag.text, currencyID=self.documento.tipMoneda, nsmap={'cbc':tag.namespace}).text=str(anticipo.monto)
                
    
        # Falta Tipo y número de otro documento o código relacionado con la operación
    
    def _getCargoDescuentos(self, root, cargoDescuentos, detalle = False):
        for cargoDescuento in cargoDescuentos:
            tag = etree.QName(self._cac, 'AllowanceCharge')   
            allowance_charge=etree.SubElement(root, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cbc, 'ChargeIndicator')  
            etree.SubElement(allowance_charge, tag.text, nsmap={'cbc':tag.namespace}).text=cargoDescuento.indicador
            
            tag = etree.QName(self._cbc, 'AllowanceChargeReasonCode')
            if detalle:
                etree.SubElement(allowance_charge, tag.text, nsmap={'cbc':tag.namespace}).text= cargoDescuento.codigo # Verificar cattalogo 53
            else:
                etree.SubElement(allowance_charge, tag.text, listAgencyName='PE:SUNAT', listName='Cargo/descuento', 
                                 listURI='urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo53', nsmap={'cbc':tag.namespace}).text= cargoDescuento.codigo # Verificar cattalogo 53
            
            tag = etree.QName(self._cbc, 'MultiplierFactorNumeric')  
            etree.SubElement(allowance_charge, tag.text, nsmap={'cbc':tag.namespace}).text= str(cargoDescuento.porcentaje) 
            
            tag = etree.QName(self._cbc, 'Amount')  
            etree.SubElement(allowance_charge, tag.text, currencyID=self.documento.tipMoneda, nsmap={'cbc':tag.namespace}).text= str(cargoDescuento.monto)
    
            tag = etree.QName(self._cbc, 'BaseAmount')  
            etree.SubElement(allowance_charge, tag.text, currencyID=self.documento.tipMoneda, 
                             nsmap={'cbc':tag.namespace}).text=str(cargoDescuento.base)
    
    def _getTributos(self, root, total, detalle = None, tributos = None):
        tax_total = etree.SubElement(root, "{%s}%s" % (self._cac, 'TaxTotal'), nsmap={'cac':self._cac})
        etree.SubElement(tax_total, "{%s}%s" % (self._cbc, 'TaxAmount'), currencyID=self.documento.tipMoneda, nsmap={'cbc':self._cbc}).text = str(round(total,2))
        tributos = tributos or self.documento.tributos
        for tributo in tributos:
            tax_subtotal = etree.SubElement(tax_total, "{%s}%s" % (self._cac, 'TaxSubtotal'), nsmap={'cac':self._cac})
            if detalle and tributo.ideTributo not in ['7152']:
                etree.SubElement(tax_subtotal, "{%s}%s" % (self._cbc, 'TaxableAmount'), currencyID=self.documento.tipMoneda, nsmap={'cbc':self._cbc}).text = str(round(tributo.baseTributo,2))
            elif not detalle:
                if tributo.ideTributo not in ['7152']:
                    etree.SubElement(tax_subtotal, "{%s}%s" % (self._cbc, 'TaxableAmount'), currencyID=self.documento.tipMoneda, nsmap={'cbc':self._cbc}).text = str(round(tributo.baseTributo,2))
            etree.SubElement(tax_subtotal, "{%s}%s" % (self._cbc, 'TaxAmount'), currencyID=self.documento.tipMoneda, nsmap={'cbc':self._cbc}).text = str(round(tributo.montoTributo,2))
            if detalle and tributo.ideTributo in ['7152']:
                etree.SubElement(tax_subtotal, "{%s}%s" % (self._cbc, 'BaseUnitMeasure'), unitCode="NIU", nsmap={'cbc':self._cbc}).text=str(tributo.cantidad)
            tax_category = etree.SubElement(tax_subtotal, "{%s}%s" % (self._cac, 'TaxCategory'), nsmap={'cac':self._cac})
            if detalle:
                if tributo.ideTributo in ['7152']:
                    etree.SubElement(tax_category, "{%s}%s" % (self._cbc, 'Percent'), nsmap={'cbc':self._cbc}).text = str(0.0)
                    etree.SubElement(tax_category, "{%s}%s" % (self._cbc, 'PerUnitAmount'), currencyID=self.documento.tipMoneda, nsmap={'cbc':self._cbc}).text= str(tributo.procentaje)
                else:    
                    etree.SubElement(tax_category, "{%s}%s" % (self._cbc, 'Percent'), nsmap={'cbc':self._cbc}).text = str(tributo.procentaje)
                if tributo.ideTributo == "2000":
                    etree.SubElement(tax_category, "{%s}%s" % (self._cbc, 'Percent'), nsmap={'cbc':self._cbc}).text= detalle.tipISC
                else:
                    if tributo.ideTributo not in ['7152']:
                        etree.SubElement(tax_category, "{%s}%s" % (self._cbc, 'TaxExemptionReasonCode'), listAgencyName="PE:SUNAT", listName="Afectacion del IGV",
                                         listURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo07", nsmap={'cbc':self._cbc}).text = detalle.tipAfectacion
            tax_scheme = etree.SubElement(tax_category, "{%s}%s" % (self._cac, 'TaxScheme'), nsmap={'cac':self._cac})
            etree.SubElement(tax_scheme, "{%s}%s" % (self._cbc, 'ID'), schemeAgencyName="PE:SUNAT", schemeName="Codigo de tributos", 
                             schemeURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo05", nsmap={'cbc':self._cbc}).text = tributo.ideTributo
            etree.SubElement(tax_scheme, "{%s}%s" % (self._cbc, 'Name'), nsmap={'cbc':self._cbc}).text = tributo.nomTributo
            etree.SubElement(tax_scheme, "{%s}%s" % (self._cbc, 'TaxTypeCode'), nsmap={'cbc':self._cbc}).text = tributo.codTipTributo

                
    
    def _getMontosGlobales(self):
        if self.documento.tipoDocumento=="08":
            tag = etree.QName(self._cac, 'RequestedMonetaryTotal')
        else:
            tag = etree.QName(self._cac, 'LegalMonetaryTotal')   
        total=etree.SubElement(self._root, tag.text, nsmap={'cac':tag.namespace})

        # Total valor de venta
        tag = etree.QName(self._cbc, 'LineExtensionAmount')  
        etree.SubElement(total, tag.text, currencyID=self.documento.tipMoneda, 
                         nsmap={'cbc':tag.namespace}).text= str(self.documento.totalValVenta)
             
        # Subtotal de la factura   
        tag = etree.QName(self._cbc, 'TaxInclusiveAmount')  
        etree.SubElement(total, tag.text, currencyID=self.documento.tipMoneda, 
                         nsmap={'cbc':tag.namespace}).text= str(self.documento.totalImpVenta)
        
        # Sumatoria otros descuentos (que no afectan la base imponible de IGV)
        tag = etree.QName(self._cbc, 'AllowanceTotalAmount')  
        etree.SubElement(total, tag.text, currencyID=self.documento.tipMoneda, 
                         nsmap={'cbc':tag.namespace}).text= str(self.documento.totalDescuentos)

        # Sumatoria otros cargos (que no afectan la base imponible del IGV)
        tag = etree.QName(self._cbc, 'ChargeTotalAmount')  
        etree.SubElement(total, tag.text, currencyID=self.documento.tipMoneda, 
                         nsmap={'cbc':tag.namespace}).text=str(self.documento.totalCargos)
        
        tag = etree.QName(self._cbc, 'PrepaidAmount')
        etree.SubElement(total, tag.text, currencyID=self.documento.tipMoneda, 
                         nsmap={'cbc':tag.namespace}).text=str(self.documento.totalAnticipos) 
        
        #Importe total de la venta, cesión en uso o del servicio prestado
        tag = etree.QName(self._cbc, 'PayableAmount')  
        etree.SubElement(total, tag.text, currencyID=self.documento.tipMoneda, 
                         nsmap={'cbc':tag.namespace}).text=str(self.documento.totalVenta)
        
        #/Invoice/cac:LegalMonetaryTotal/cbc:PayableRoundingAmount
        
    def _getDetalle(self):
        cont = 1
        for detalle in self.documento.detalles:
            if self.documento.tipoDocumento=="08":
                tipo_linea = "DebitNoteLine"
            elif self.documento.tipoDocumento=="07":
                tipo_linea = "CreditNoteLine"
            else:
                tipo_linea = "InvoiceLine"
            line = etree.SubElement(self._root, "{%s}%s" % (self._cac, tipo_linea), nsmap={'cac':self._cac})
            etree.SubElement(line, "{%s}%s" % (self._cbc, 'ID'), nsmap={'cbc':self._cbc}).text = str(cont)
            cont+=1
            if self.documento.tipoDocumento=="08":
                cantidad_linea = 'DebitedQuantity'
            elif self.documento.tipoDocumento=="07":
                cantidad_linea =  'CreditedQuantity'
            else:
                cantidad_linea =  'InvoicedQuantity'
            etree.SubElement(line, "{%s}%s" % (self._cbc, cantidad_linea), unitCode=detalle.codUnidadMedida,
                             unitCodeListID='UN/ECE rec 20', unitCodeListAgencyName='United Nations Economic Commission for Europe',
                             nsmap={'cbc':self._cbc}).text = str(detalle.cantidad)
            # Valor de venta por ítem
            etree.SubElement(line, "{%s}%s" % (self._cbc, 'LineExtensionAmount'), currencyID=self.documento.tipMoneda, nsmap={'cbc':self._cbc}).text = str(detalle.mtoValorVentaItem)
            
            # Precio de venta unitario por ítem
            reference = etree.SubElement(line, "{%s}%s" % (self._cac, 'PricingReference'), nsmap={'cac':self._cac})
            condition_price = etree.SubElement(reference, "{%s}%s" % (self._cac, 'AlternativeConditionPrice'), nsmap={'cac':self._cac})
            if detalle.mtoValorReferencialUnitario == 0.0:
                etree.SubElement(condition_price, "{%s}%s" % (self._cbc, 'PriceAmount'), currencyID=self.documento.tipMoneda, nsmap={'cbc':self._cbc}).text = str(detalle.mtoPrecioVentaUnitario)
                etree.SubElement(condition_price, "{%s}%s" % (self._cbc, 'PriceTypeCode'), listName="Tipo de Precio", listAgencyName="PE:SUNAT",
                                 listURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo16", nsmap={'cbc':self._cbc}).text = "01"
            else:
                # Valor referencial unitario por ítem en operaciones gratuitas (no onerosas)
                etree.SubElement(condition_price, "{%s}%s" % (self._cbc, 'PriceAmount'), currencyID=self.documento.tipMoneda, nsmap={'cbc':self._cbc}).text = str(detalle.mtoValorReferencialUnitario)
                etree.SubElement(condition_price, "{%s}%s" % (self._cbc, 'PriceTypeCode'), listName="Tipo de Precio", listAgencyName="PE:SUNAT",
                                 listURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo16", nsmap={'cbc':self._cbc}).text = "02"
            
            #Cargo/descuento por ítem
            if self.documento.tipoDocumento not in ["07","08"]:
                self._getCargoDescuentos(line, detalle.cargoDescuentos, True)
            
            # Afectación al IGV por ítem / Afectación IVAP por ítem
            self._getTributos(line, detalle.sumTotTributosItem, detalle, detalle.tributos)                
            
            item = etree.SubElement(line, "{%s}%s" % (self._cac, 'Item'), nsmap={'cac':self._cac})
            # Detalle
            etree.SubElement(item, "{%s}%s" % (self._cbc, 'Description'), nsmap={'cbc':self._cbc}).text = etree.CDATA(detalle.descripcion.replace("\n", " ")[:250])
            
            # Código de producto
            identification = etree.SubElement(item, "{%s}%s" % (self._cac, 'SellersItemIdentification'), nsmap={'cac':self._cac})
            etree.SubElement(identification, "{%s}%s" % (self._cbc, 'ID'), nsmap={'cbc':self._cbc}).text = detalle.codProducto
            
            # Código de producto SUNAT
            if detalle.codProductoSUNAT:
                classification = etree.SubElement(item, "{%s}%s" % (self._cac, 'CommodityClassification'), nsmap={'cac':self._cac})
                etree.SubElement(classification, "{%s}%s" % (self._cbc, 'ItemClassificationCode'), listID="UNSPSC", listAgencyName="GS1 US", 
                                 listName="Item Classification",nsmap={'cbc':self._cbc}).text = detalle.codProductoSUNAT
        
            # codigo GTIN
            if detalle.codProductoGTIN and detalle.tipoProductoGTIN:
                standard = etree.SubElement(item, "{%s}%s" % (self._cac, 'StandardItemIdentification'), nsmap={'cac':self._cac})
                etree.SubElement(standard, "{%s}%s" % (self._cbc, 'ItemClassificationCode'), schemeID=detalle.tipoProductoGTIN,
                                 nsmap={'cbc':self._cbc}).text = detalle.codProductoGTIN
            
            if detalle.placa:
                identification = etree.SubElement(item, "{%s}%s" % (self._cac, 'AdditionalItemProperty'), nsmap={'cac':self._cac})
                etree.SubElement(identification, "{%s}%s" % (self._cbc, 'Name'), nsmap={'cbc':self._cbc}).text = 'Gastos Art. 37 Renta: Número de Placa'
                etree.SubElement(identification, "{%s}%s" % (self._cbc, 'NameCode'), listName='Propiedad del item', listAgencyName='PE:SUNAT',
                                 listURI='urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo55', nsmap={'cbc':self._cbc}).text = '7000'
                etree.SubElement(identification, "{%s}%s" % (self._cbc, 'Value'), nsmap={'cbc':self._cbc}).text = detalle.placa
            
            # Valor unitario por ítem
            price = etree.SubElement(line, "{%s}%s" % (self._cac, 'Price'), nsmap={'cac':self._cac})
            etree.SubElement(price, "{%s}%s" % (self._cbc, 'PriceAmount'), currencyID=self.documento.tipMoneda, nsmap={'cbc':self._cbc}).text = str(detalle.mtoValorUnitario)
                
    
    def _getUbl(self, customization = '1.0'):
        if self.documento.tipoDocumento == '09':
            etree.SubElement(self._root, "{%s}%s" % (self._cbc, 'UBLVersionID'), nsmap={'cbc':self._cbc}).text = '2.1'
            etree.SubElement(self._root, "{%s}%s" % (self._cbc, 'CustomizationID'), nsmap={'cbc':self._cbc}).text = customization or '1.0'
        else:
            etree.SubElement(self._root, "{%s}%s" % (self._cbc, 'UBLVersionID'), nsmap={'cbc':self._cbc}).text = '2.1'
            etree.SubElement(self._root, "{%s}%s" % (self._cbc, 'CustomizationID'), schemeAgencyName='PE:SUNAT', nsmap={'cbc':self._cbc}).text = '2.0'
        
    def _getFactura(self):
        if self.documento.tipoDocumento in ['07']:
            nsmap = self._nsmap("CreditNote-2")
            self._root = etree.Element("{urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2}CreditNote", nsmap=nsmap)
        elif self.documento.tipoDocumento in ['08']:
            nsmap = self._nsmap("DebitNote-2")
            self._root = etree.Element("{urn:oasis:names:specification:ubl:schema:xsd:DebitNote-2}DebitNote", nsmap=nsmap)
        else:
            nsmap = self._nsmap("Invoice-2")
            self._root = etree.Element("{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}Invoice", nsmap=nsmap)
        self._getX509Template()
        self._getUbl()
        self._getDocumento()
        self._getAnticipos()
        if self.documento.tipoDocumento in ['07', '08']:
            self._getMotivoNota()
            self._getDocumentosModificados(self.documento.documentosModificados)
        self._getFirma()
        self._getEmisor()
        self._getAdquirente()
        self._getDetraccion()
        self._getMedioPago()
        if self.documento.tipoDocumento in ['01', '03']:
            self._getMontoAnticipos()
        self._getDocumentoRelacionado()
        self._getCargoDescuentos(self._root, self.documento.cargoDescuentos)
        self._getTributos(self._root, self.documento.totalTributos)
        self._getMontosGlobales()
        self._getDetalle()
    
    def _getMotivoNota(self):
        tag = etree.QName(self._cac, 'DiscrepancyResponse')   
        discrepancy=etree.SubElement(self._root, tag.text, nsmap={'cac':tag.namespace})
        tag = etree.QName(self._cbc, 'ResponseCode')   
        if self.documento.tipoDocumento in ['08']:
            etree.SubElement(discrepancy, tag.text, listAgencyName="PE:SUNAT", listURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo10", nsmap={'cbc':tag.namespace}).text=self.documento.codigoNota
        elif self.documento.tipoDocumento in ['07']:
            etree.SubElement(discrepancy,  tag.text, listAgencyName="PE:SUNAT", listURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo09", nsmap={'cbc':tag.namespace}).text=self.documento.codigoNota
        tag = etree.QName(self._cbc, 'Description')   
        etree.SubElement(discrepancy, tag.text, nsmap={'cbc':tag.namespace}).text=etree.CDATA(self.documento.motivo)

    def _getDocumentosModificados(self, documentosModificados, detalle = False):
        for documentoModificado in documentosModificados:
            tag = etree.QName(self._cac, 'BillingReference')   
            reference=etree.SubElement(self._root, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cac, 'InvoiceDocumentReference')   
            invoice=etree.SubElement(reference, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cbc, 'ID')
            etree.SubElement(invoice, tag.text, nsmap={'cbc':tag.namespace}).text=documentoModificado.numero
            tag = etree.QName(self._cbc, 'DocumentTypeCode')   
            etree.SubElement(invoice, tag.text, listAgencyName='PE:SUNAT', listName='Tipo de Documento', 
                             listURI='urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo01', nsmap={'cbc':tag.namespace}).text=documentoModificado.tipoDocumento

    def getDocumento(self):
        if self.documento.tipoDocumento in ['09']:
            self._getGuia()
        else:
            self._getFactura()
        xml = etree.tostring(self._root, pretty_print=True, xml_declaration=True, encoding='utf-8', standalone=False)
        return xml

    def _getGuia(self):
        xmlns=etree.QName("urn:oasis:names:specification:ubl:schema:xsd:DespatchAdvice-2", 'DespatchAdvice')
        nsmap1=OrderedDict([(None, xmlns.namespace), ('cac', self._cac), ('cbc', self._cbc), ('ccts', self._ccts), 
                            ('ds', self._ds), ('ext', self._ext), ('qdt', self._qdt), ('sac', self._sac), ('udt', self._udt), 
                            ('xsi', self._xsi)] )
        self._root=etree.Element(xmlns.text, nsmap=nsmap1)
        self._getX509Template()
        self._getUbl()
        
        self._getDocumento()
        
        self._getDocumentoRelacionado()
        self._getFirma()
        self._getEmisor()
        self._getAdquirente()
        if self.documento.establecimientoTercero:
            self._getAdquirente(tercero=True)
        
        tag = etree.QName(self._cac, 'Shipment')
        shipment = etree.SubElement(self._root, tag.text, nsmap={'cac':tag.namespace})
        
        tag = etree.QName(self._cbc, 'ID')
        etree.SubElement(shipment, tag.text, nsmap={'cbc':tag.namespace}).text = '1'
        
        tag = etree.QName(self._cbc, 'HandlingCode')
        etree.SubElement(shipment, tag.text, nsmap={'cbc':tag.namespace}).text = self.documento.motivo
        if self.documento.descripcion:
            tag = etree.QName(self._cbc, 'Information')
            etree.SubElement(shipment, tag.text, nsmap={'cbc':tag.namespace}).text = etree.CDATA(self.documento.descripcion)
        tag = etree.QName(self._cbc, 'GrossWeightMeasure')
        etree.SubElement(shipment, tag.text, unitCode="KGM", 
                         nsmap={'cbc':tag.namespace}).text = str(self.documento.pesoBruto)
        if self.documento.motivo == '08':
            tag = etree.QName(self._cbc, 'TotalTransportHandlingUnitQuantity')
            etree.SubElement(shipment, tag.text, nsmap={'cbc':tag.namespace}).text = str(self.documento.bultos)
        
        tag = etree.QName(self._cbc, 'SplitConsignmentIndicator')
        etree.SubElement(shipment, tag.text, nsmap={'cbc':tag.namespace}).text = self.documento.transbordo
        
        
        # ShipmentStage
        tag = etree.QName(self._cac, 'ShipmentStage')
        stage= etree.SubElement(shipment, tag.text, nsmap={'cac':tag.namespace})
        
        tag = etree.QName(self._cbc, 'ID')
        etree.SubElement(stage, tag.text, nsmap={'cbc':tag.namespace}).text = '1'
        
        tag = etree.QName(self._cbc, 'TransportModeCode')
        etree.SubElement(stage, tag.text, nsmap={'cbc':tag.namespace}).text = self.documento.modoTraslado
        
        tag = etree.QName(self._cac, 'TransitPeriod')
        period = etree.SubElement(stage, tag.text, nsmap={'cac':tag.namespace})
        tag = etree.QName(self._cbc, 'StartDate')
        etree.SubElement(period, tag.text, nsmap={'cbc':tag.namespace}).text = self.documento.fechaTraslado
        
        if self.documento.modoTraslado == '01':
            for transportista in self.documento.transportistas:
                tag = etree.QName(self._cac, 'CarrierParty')   
                customer=etree.SubElement(stage, tag.text, nsmap={'cac':tag.namespace})
                tag = etree.QName(self._cac, 'PartyIdentification')   
                ident=etree.SubElement(customer, tag.text, nsmap={'cac':tag.namespace})
                tag = etree.QName(self._cbc, 'ID')
                etree.SubElement(ident, tag.text, schemeID= transportista.tipoDocumento or '-',
                                 nsmap={'cbc':tag.namespace}).text= transportista.numDocumento or '-'
                
                tag = etree.QName(self._cac, 'PartyName')  
                party=etree.SubElement(customer, tag.text, nsmap={'cac':tag.namespace})
                tag = etree.QName(self._cbc, 'Name')   
                etree.SubElement(party, tag.text, nsmap={'cbc':tag.namespace}).text= etree.CDATA(transportista.nombre)
                break
        else:
            tag = etree.QName(self._cac, 'TransportMeans')
            transport= etree.SubElement(stage, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cac, 'RoadTransport')
            road= etree.SubElement(transport, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cbc, 'LicensePlateID')
            etree.SubElement(road, tag.text, nsmap={'cbc':tag.namespace}).text = self.documento.placa
        
            for transportista in self.documento.transportistas:
                tag = etree.QName(self._cac, 'DriverPerson')   
                customer=etree.SubElement(stage, tag.text, nsmap={'cac':tag.namespace})
                tag = etree.QName(self._cbc, 'ID')   
                etree.SubElement(customer, tag.text, schemeID= transportista.numDocumento  or '-',
                                 nsmap={'cbc':tag.namespace}).text=transportista.numDocumento or '-'
            
        tag = etree.QName(self._cac, 'Delivery')
        delivery = etree.SubElement(shipment, tag.text, nsmap={'cac':tag.namespace})
        tag = etree.QName(self._cac, 'DeliveryAddress')   
        address=etree.SubElement(delivery, tag.text, nsmap={'cac':tag.namespace})
        tag = etree.QName(self._cbc, 'ID')    
        etree.SubElement(address, tag.text, nsmap={'cbc':tag.namespace}).text= self.documento.ubigeoLlegada
        tag = etree.QName(self._cbc, 'StreetName')   
        etree.SubElement(address, tag.text, nsmap={'cbc':tag.namespace}).text= self.documento.direccionLlegada
        
        if self.documento.modoTraslado == '02':
            tag = etree.QName(self._cac, 'TransportHandlingUnit')   
            transport=etree.SubElement(shipment, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cbc, 'ID')   
            etree.SubElement(transport, tag.text, nsmap={'cbc':tag.namespace}).text=self.documento.placa
            
            for vehículo in self.documento.vehículos:
                if vehículo.placa != self.documento.placa:
                    tag = etree.QName(self._cac, 'TransportEquipment')   
                    equipment=etree.SubElement(transport, tag.text, nsmap={'cac':tag.namespace})
                    tag = etree.QName(self._cbc, 'ID')   
                    etree.SubElement(equipment, tag.text, nsmap={'cbc':tag.namespace}).text=vehículo.placa
        
        # Aqui va datos del contenedor
        
        tag = etree.QName(self._cac, 'OriginAddress')   
        oaddress=etree.SubElement(shipment, tag.text, nsmap={'cac':tag.namespace})
        tag = etree.QName(self._cbc, 'ID')
           
        etree.SubElement(oaddress, tag.text, nsmap={'cbc':tag.namespace}).text= self.documento.ubigeoPartida
        tag = etree.QName(self._cbc, 'StreetName')   
        etree.SubElement(oaddress, tag.text, nsmap={'cbc':tag.namespace}).text= self.documento.direccionPartida
        
        #Puerto/Aeropuerto
        cont=1
        for detalle in self.documento.detalles:
            tag = etree.QName(self._cac, 'DespatchLine')   
            despatch=etree.SubElement(self._root, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cbc, 'ID')   
            etree.SubElement(despatch, tag.text, nsmap={'cbc':tag.namespace}).text=str(cont)
            tag = etree.QName(self._cbc, 'DeliveredQuantity')   
            etree.SubElement(despatch, tag.text, unitCode= detalle.codUnidadMedida,
                             nsmap={'cbc':tag.namespace}).text=str(detalle.cantidad)
            tag = etree.QName(self._cac, 'OrderLineReference')   
            ref=etree.SubElement(despatch, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cbc, 'LineID')   
            etree.SubElement(ref, tag.text, nsmap={'cbc':tag.namespace}).text=str(cont)
            cont+=1
            
            tag = etree.QName(self._cac, 'Item')   
            item=etree.SubElement(despatch, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cbc, 'Name')   
            etree.SubElement(item, tag.text, nsmap={'cbc':tag.namespace}).text=etree.CDATA(detalle.descripcion.replace("\n", " ")[:250])
            
            tag = etree.QName(self._cac, 'SellersItemIdentification')   
            ident=etree.SubElement(item, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cbc, 'ID')   
            etree.SubElement(ident, tag.text, nsmap={'cbc':tag.namespace}).text= detalle.codProducto
        
        

