import unittest
from datetime import datetime

from librecpe.common.documento import Documento
from librecpe.cpe.ubl21 import Ubl21

class TestFactura(unittest.TestCase):
    def test_generar_factura(self):
        doc = Documento(tipo='01')
        doc.setDocument({
            'tipoDocumento': '01',
            'fecEmision': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'tipMoneda': 'PEN',
            'emisor': {
                'tipoDocumento': '6',
                'numDocumento': '20490416910',
                'nombre': 'GRUPO YACCK S.A.C.',
                'nomComercial': '-',
                'direccion': 'AV. PANAMERICANA NRO. SN',
                'ubigeo': '030401',
                'urbanizacion': '-',
                'provincia': '-',
                'region': '-',
                'distrito': '-',
                'codPais': 'PE',
                'codEstablecimiento': '0000'
            },
            'adquirente': {
                'tipoDocumento': '6',
                'numDocumento': '20406293271',
                'nombre': 'IND. ALIMENT. NEGOLATINA S.C.R.L.',
                'direccion': 'AV. LA FLORAL NRO. 940 URB. VALLECITO',
                'ubigeo': '210101',
                'codPais': 'PE'
            },
            'detalles': [
                {
                    'cantidad': 1,
                    'descripcion': 'Producto de prueba',
                    'codProducto': 'P001',
                    'codUnidadMedida': 'NIU',
                    'mtoValorUnitario': 100.00,
                    'mtoValorVentaItem': 100.00,
                    'mtoPrecioVentaUnitario': 118.00,
                    'sumTotTributosItem': 18.00,
                    'tributos': [
                        {
                            'ideTributo': '1000',
                            'nomTributo': 'IGV',
                            'codTipTributo': 'VAT',
                            'montoTributo': 18.00,
                            'baseTributo': 100.00,
                            'procentaje': 18.00
                        }
                    ],
                    'tipAfectacion': '10'
                }
            ],
            'totalValVenta': 100.00,
            'totalImpVenta': 18.00,
            'totalVenta': 118.00,
            'totalTributos': 18.00,
            'tributos': [
                 {
                    'ideTributo': '1000',
                    'nomTributo': 'IGV',
                    'codTipTributo': 'VAT',
                    'montoTributo': 18.00,
                    'baseTributo': 100.00,
                    'procentaje': 18.00
                }
            ],
            'leyendas': [
                {'codLeyenda': '1000', 'desLeyenda': 'SON CIENTO DIECIOCHO CON 00/100 SOLES'}
            ]
        })

        # Generate XML using Ubl21 directly to skip signing requirement for test
        ubl = Ubl21(doc)
        xml = ubl.getDocumento()
        
        # Verify basic structure
        self.assertIn(b'20490416910', xml)
        self.assertIn(b'GRUPO YACCK S.A.C.', xml)
        self.assertIn(b'20406293271', xml)
        self.assertIn(b'IND. ALIMENT. NEGOLATINA S.C.R.L.', xml)
        self.assertIn(b'Producto de prueba', xml)
        self.assertIn(b'100.0', xml)
        self.assertIn(b'18.0', xml)
        self.assertIn(b'118.0', xml)

if __name__ == '__main__':
    unittest.main()
