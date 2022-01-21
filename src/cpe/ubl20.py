from collections import OrderedDict
from lxml import etree

class Ubl20:
    
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
        #self.version = version
    
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
        nsmap=OrderedDict([(None, "urn:sunat:names:specification:ubl:peru:schema:xsd::%s" % documento), ('cac', self._cac), ('cbc', self._cbc), ('ds', self._ds), 
                            ('ext', self._ext), ('sac', self._sac), ('xsi', self._xsi)] )
        return nsmap 
    
    def _getEmisor(self):
        emisor = self.documento.emisor
        tag = etree.QName(self._cac, 'AccountingSupplierParty')   
        supplier=etree.SubElement(self._root, tag.text, nsmap={'cac':tag.namespace})
        tag = etree.QName(self._cbc, 'CustomerAssignedAccountID')   
        etree.SubElement(supplier, tag.text, nsmap={'cbc':tag.namespace}).text=emisor.numDocumento
        
        tag = etree.QName(self._cbc, 'AdditionalAccountID')   
        etree.SubElement(supplier, tag.text, nsmap={'cbc':tag.namespace}).text=emisor.tipoDocumento
        tag = etree.QName(self._cac, 'Party')
        party=etree.SubElement(supplier, tag.text, nsmap={'cac':tag.namespace})
        if emisor.nomComercial !='-':
            tag = etree.QName(self._cac, 'PartyName')   
            party_name=etree.SubElement(party, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cbc, 'Name')   
            etree.SubElement(party_name, tag.text, nsmap={'cbc':tag.namespace}).text= etree.CDATA(emisor.nomComercial) 
        
        tag = etree.QName(self._cac, 'PostalAddress')   
        address=etree.SubElement(party, tag.text, nsmap={'cac':tag.namespace})
        
        tag = etree.QName(self._cbc, 'AddressTypeCode')   
        etree.SubElement(address, tag.text, nsmap={'cbc':tag.namespace}).text=emisor.ubigeo
        tag = etree.QName(self._cac, 'PartyLegalEntity')   
        entity=etree.SubElement(party, tag.text, nsmap={'cac':tag.namespace})
        tag = etree.QName(self._cbc, 'RegistrationName')   
        etree.SubElement(entity, tag.text, nsmap={'cbc':tag.namespace}).text= etree.CDATA(emisor.nombre)
    
    def _getAdquirente(self, detalle = None, adquirente = None):
        tag = etree.QName(self._cac, 'AccountingCustomerParty')   
        customer=etree.SubElement(detalle, tag.text, nsmap={'cac':tag.namespace})
        tag = etree.QName(self._cbc, 'CustomerAssignedAccountID')
        etree.SubElement(customer, tag.text, nsmap={'cbc':tag.namespace}).text=adquirente.numDocumento or '0'
        tag = etree.QName(self._cbc, 'AdditionalAccountID')
        etree.SubElement(customer, tag.text, nsmap={'cbc':tag.namespace}).text=adquirente.tipoDocumento or '-'
    
    def _getTributos(self, root, total, documento = None):
        for tributo in documento.tributos:
            tag = etree.QName(self._cac, 'TaxTotal')   
            total=etree.SubElement(root, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cbc, 'TaxAmount')  
            etree.SubElement(total, tag.text, currencyID=documento.tipMoneda, 
                             nsmap={'cbc':tag.namespace}).text=str(round(tributo.montoTributo,2))
            tag = etree.QName(self._cac, 'TaxSubtotal')   
            tax_subtotal=etree.SubElement(total, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cbc, 'TaxAmount')   
            etree.SubElement(tax_subtotal, tag.text, currencyID=documento.tipMoneda, 
                             nsmap={'cbc':tag.namespace}).text=str(round(tributo.montoTributo,2))
            tag = etree.QName(self._cac, 'TaxCategory')   
            category=etree.SubElement(tax_subtotal, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cac, 'TaxScheme')   
            scheme=etree.SubElement(category, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cbc, 'ID')
            etree.SubElement(scheme, tag.text, nsmap={'cbc':tag.namespace}).text=tributo.ideTributo
            tag = etree.QName(self._cbc, 'Name')   
            etree.SubElement(scheme, tag.text, 
                                      nsmap={'cbc':tag.namespace}).text=tributo.nomTributo 
            tag = etree.QName(self._cbc, 'TaxTypeCode')   
            etree.SubElement(scheme, tag.text, 
                                      nsmap={'cbc':tag.namespace}).text=tributo.codTipTributo

    def _getUbl(self, customization = '1.0'):
        etree.SubElement(self._root, "{%s}%s" % (self._cbc, 'UBLVersionID'), nsmap={'cbc':self._cbc}).text = '2.0'
        etree.SubElement(self._root, "{%s}%s" % (self._cbc, 'CustomizationID'), nsmap={'cbc':self._cbc}).text = customization or '1.0'
        
    def _getResumen(self):
        xmlns=etree.QName("urn:sunat:names:specification:ubl:peru:schema:xsd:SummaryDocuments-1", 'SummaryDocuments')
        nsmap1=OrderedDict([(None, xmlns.namespace), ('cac', self._cac), ('cbc', self._cbc), ('ds', self._ds), 
                            ('ext', self._ext), ('sac', self._sac), ('xsi', self._xsi)] )
        self._root=etree.Element(xmlns.text, nsmap=nsmap1)
        self._getX509Template()
        self._getUbl("1.1")
        
        tag = etree.QName(self._cbc, 'ID')   
        etree.SubElement(self._root, tag.text, nsmap={'cbc':tag.namespace}).text=self.documento.numero
        tag = etree.QName(self._cbc, 'ReferenceDate')   
        etree.SubElement(self._root, tag.text, nsmap={'cbc':tag.namespace}).text=self.documento.fecEmision.strftime("%Y-%m-%d")
        #catalogo numero 1 -- falta procesar <cbc:IssueDate>2012-06-24</cbc:IssueDate>
        tag = etree.QName(self._cbc, 'IssueDate')   
        etree.SubElement(self._root, tag.text, nsmap={'cbc':tag.namespace}).text=self.documento.fecEnvio.strftime("%Y-%m-%d")
        
        self._getFirma()
        self._getEmisor()
        cont = 1
        for documento in self.documento.documentos:    
            tag = etree.QName(self._sac, 'SummaryDocumentsLine')   
            line=etree.SubElement(self._root, tag.text, nsmap={'sac':tag.namespace})
            tag = etree.QName(self._cbc, 'LineID')   
            etree.SubElement(line, tag.text, nsmap={'cbc':tag.namespace}).text=str(cont)
            cont+=1
            tag = etree.QName(self._cbc, 'DocumentTypeCode')   
            etree.SubElement(line, tag.text, nsmap={'cbc':tag.namespace}).text=documento.tipoDocumento
            
            
            tag = etree.QName(self._cbc, 'ID')   
            etree.SubElement(line, tag.text, nsmap={'cbc':tag.namespace}).text=documento.numero
            
            self._getAdquirente(line, adquirente=documento.adquirente)
            if documento.tipoDocumento in ['07', '08']:
                self._getDocumentosModificados(documento.documentosModificados, line)
            
            tag = etree.QName(self._cac, 'Status')   
            status = etree.SubElement(line, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cbc, 'ConditionCode')   
            #analizar los otros codigos  2 3 y 4
            etree.SubElement(status, tag.text, nsmap={'cbc':tag.namespace}).text= documento.condicion or '1'
            tag = etree.QName(self._sac, 'TotalAmount')   
            etree.SubElement(line, tag.text, currencyID=documento.tipMoneda, 
                             nsmap={'sac':tag.namespace}).text=str(documento.totalVenta)
            
            for operacion in documento.operaciones:
                tag = etree.QName(self._sac, 'BillingPayment')   
                billing=etree.SubElement(line, tag.text, nsmap={'sac':tag.namespace})
                tag = etree.QName(self._cbc, 'PaidAmount')   
                etree.SubElement(billing, tag.text, currencyID=documento.tipMoneda, nsmap={'cbc':tag.namespace}).text= str(operacion.total)
                tag = etree.QName(self._cbc, 'InstructionID')   
                etree.SubElement(billing, tag.text, nsmap={'cbc':tag.namespace}).text=operacion.codigo
            self._getTributos(line, documento.totalTributos, documento = documento)

    def _getAnulacion(self):
        xmlns=etree.QName("urn:sunat:names:specification:ubl:peru:schema:xsd:VoidedDocuments-1", 'VoidedDocuments')
        nsmap1=OrderedDict([(None, xmlns.namespace), ('cac', self._cac), ('cbc', self._cbc), ('ccts', self._ccts), 
                            ('ds', self._ds), ('ext', self._ext), ('qdt', self._qdt), ('sac', self._sac), ('udt', self._udt), 
                            ('xsi', self._xsi)] )
        self._root=etree.Element(xmlns.text, nsmap=nsmap1)
        self._getX509Template()
        self._getUbl()
        tag = etree.QName(self._cbc, 'ID')   
        etree.SubElement(self._root, tag.text, nsmap={'cbc':tag.namespace}).text=self.documento.numero
        tag = etree.QName(self._cbc, 'ReferenceDate')   
        etree.SubElement(self._root, tag.text, nsmap={'cbc':tag.namespace}).text=self.documento.fecEmision.strftime("%Y-%m-%d")
        tag = etree.QName(self._cbc, 'IssueDate')   
        etree.SubElement(self._root, tag.text, nsmap={'cbc':tag.namespace}).text=self.documento.fecEnvio.strftime("%Y-%m-%d")
        self._getFirma()
        self._getEmisor()
        cont = 1
        for anulado in self.documento.documentosAnulados:
            tag = etree.QName(self._sac, 'VoidedDocumentsLine')   
            line=etree.SubElement(self._root, tag.text, nsmap={'sac':tag.namespace})
            tag = etree.QName(self._cbc, 'LineID')   
            etree.SubElement(line, tag.text, nsmap={'cbc':tag.namespace}).text=str(cont)
            cont+=1
            tag = etree.QName(self._cbc, 'DocumentTypeCode')   
            etree.SubElement(line, tag.text, nsmap={'cbc':tag.namespace}).text= anulado.tipoDocumento
            tag = etree.QName(self._sac, 'DocumentSerialID')   
            etree.SubElement(line, tag.text, nsmap={'sac':tag.namespace}).text= anulado.serie
            tag = etree.QName(self._sac, 'DocumentNumberID')   
            etree.SubElement(line, tag.text, nsmap={'sac':tag.namespace}).text= anulado.numero
            tag = etree.QName(self._sac, 'VoidReasonDescription')   
            etree.SubElement(line, tag.text, nsmap={'sac':tag.namespace}).text= anulado.descripcion or 'Anulado'
    
    def _getDocumentosModificados(self, documentosModificados, detalle = False):
        for documentoModificado in documentosModificados:
            tag = etree.QName(self._cac, 'BillingReference')   
            reference=etree.SubElement(detalle, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cac, 'InvoiceDocumentReference')   
            invoice=etree.SubElement(reference, tag.text, nsmap={'cac':tag.namespace})
            tag = etree.QName(self._cbc, 'ID')
            etree.SubElement(invoice, tag.text, nsmap={'cbc':tag.namespace}).text=documentoModificado.numero
            tag = etree.QName(self._cbc, 'DocumentTypeCode')   
            etree.SubElement(invoice, tag.text, nsmap={'cbc':tag.namespace}).text=documentoModificado.tipoDocumento

    def getDocumento(self):
        if self.documento.tipoDocumento in ['ra']:
            self._getAnulacion()
        elif self.documento.tipoDocumento in ['rc']:
            self._getResumen()
        xml = etree.tostring(self._root, pretty_print=True, xml_declaration=True, encoding='utf-8', standalone=False)
        return xml

