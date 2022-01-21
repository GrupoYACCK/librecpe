
from lxml import etree
from io import BytesIO

from . import ubl21
from . import ubl20
from librecpe.common import LibreCpeError

class LibreCPE:
    
    def __init__(self, documento = None):
        self.documento = documento
    
    def firmarDocumento(self, xml, key, cer, clave=None):
        import xmlsec
        parser = etree.XMLParser(strip_cdata=False)
        if not type(xml) == bytes:
            xml_iofile=BytesIO(xml.encode('utf-8'))
        else:
            xml_iofile=BytesIO(xml)
        root=etree.parse(xml_iofile, parser).getroot()
        signature_node = xmlsec.tree.find_node(root, xmlsec.Node.SIGNATURE)
        assert signature_node is not None
        assert signature_node.tag.endswith(xmlsec.Node.SIGNATURE)
        ctx = xmlsec.SignatureContext()
        key = xmlsec.Key.from_memory(key, xmlsec.KeyFormat.PEM)
        assert key is not None
        key.load_cert_from_memory(cer, xmlsec.KeyFormat.PEM)
        
        ctx.key = key
        assert ctx.key is not None
        # Sign the template.
        # key = xmlsec.Key.from_memory(key, xmlsec.KeyFormat.PKCS12_PEM, clave)
        ctx.sign(signature_node)
        xml = etree.tostring(root,  pretty_print=True, xml_declaration = True, encoding='utf-8', standalone=False)
        return xml
    
    def getFirma(self, xml):
        tag = etree.QName('http://www.w3.org/2000/09/xmldsig#', 'DigestValue')
        if not type(xml) == bytes:
            xml_sign=xml.encode('utf-8')
        else:
            xml_sign=xml
        root = etree.fromstring(xml_sign)
        digest= root.find('.//'+tag.text)
        resumen = None
        if digest!=-1:
            resumen = digest.text
        tag = etree.QName('http://www.w3.org/2000/09/xmldsig#', 'SignatureValue')
        sign= root.find('.//'+tag.text)
        firma = None
        if sign!=-1:
            firma = sign.text
        return resumen, firma

    def getDocumento(self, key=None, cer=None, xml = None):
        if not self.documento and not xml:
            raise LibreCpeError("El Comprobante/Documento no esta definido")
        if not xml:
            if self.documento.tipoDocumento in ['ra', 'rc']:
                xml = ubl20.Ubl20(self.documento).getDocumento()
            elif self.documento.tipoDocumento in ['01','03', '07', '08', '09']:
                xml = ubl21.Ubl21(self.documento).getDocumento()
            else:
                raise LibreCpeError("Documento No Soportado")
        xml = xml
        xml_firmado = key and cer and self.firmarDocumento(xml, key, cer) or ''
        
        return xml, xml_firmado #xml_str.decode("utf-8") # xml_str, self._firmarDocumento(xml_str, key, cer)
        # return xml_str.decode("utf-8")
        # return None