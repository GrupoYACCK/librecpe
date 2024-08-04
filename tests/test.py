
import json

from librecpe import LibreCPE, LibreCpeError

librecpe = LibreCPE()

factura_demo = {
    "numero": "F001-1",
    "fecEmision": "2019-06-11 12:00:00",
    "fecVencimiento": "2019-07-11",
    "tipoDocumento": "01",
    "tipOperacion": "0101",
    "tipMoneda": "PEN",
    "leyendas": [
        {
            "codLeyenda": "1000",
            "desLeyenda": "TRESCIENTOS CUARENTA Y DOS Y 20/100 SOLES",
            }
        ],
    "emisor": {
        "nombre": "GRUPO YACCK S.A.C.",
        "tipoDocumento": "6",
        "numDocumento": "20490416910",
        "direccion": "AV. PANAMERICANA NRO. SN (2DO PISO COOP. SR SOCLLACASA)",
        "urbanizacion": "",
        "ubigeo": "030201",
        "distrito": "CHALHUANCA",
        "provincia": "AYMARAES",
        "region": "APURIMAC",
        "codPais": "PE",
        "codEstablecimiento": "0000"
        },
    "adquirente": {
        "nombre": "GRUPO DE COMERCIOY CONSULTORIA ESTRATEGICA E.I.R.L.",
        "tipoDocumento": "6",
        "numDocumento": "20392923862",
        "direccion": "MZA. U LOTE. 19",
        "urbanizacion": "URB.  LOS JARDINES DE SAN JUAN  (2DA ETAPA.)",
        "ubigeo": "140112",
        "distrito": "SAN JUAN DE LURIGANCHO",
        "provincia": "LIMA",
        "region": "LIMA",
        "codPais": "PE"
        },
    "guias": [{
        "numero": "T001-0001",
        # "tipoDocumento": "09"
        }],
    "totalValVenta": 290,
    "totalImpVenta": 342.2,
    "totalDescuentos": 0.0,
    "totalCargos": 0.0,
    "totalAnticipos": 0.0,
    "totalVenta": 342.2,
    
    "totalTributos": 52.2,
    "tributos": [{
        "ideTributo": "1000",
        "nomTributo": "IGV",
        "codTipTributo": "VAT",
        "montoTributo": 52.2,
        "baseTributo": 290.0,
        "procentaje": 18.0
        }
        ],
    "detalles": [
        {
            "codUnidadMedida": "NIU",
            "cantidad": 2.0,
            "codProducto": "123456",
            "codProductoSUNAT": "12334",
            "placa": "XYZ-123",
            "descripcion": "Gasolina 95",
            "mtoValorUnitario": 100.0,
            "mtoPrecioVentaUnitario": 118.0,
            "mtoValorReferencialUnitario": 0.0,
            "sumTotTributosItem":36.0,
            "tipAfectacion": "10",
            "tributos": [
                {
                    "ideTributo": "1000",
                    "nomTributo": "IGV",
                    "codTipTributo": "VAT",
                    "montoTributo": 36,
                    "baseTributo": 200,
                    "procentaje": 18
                    }
                ],
            "mtoValorVentaItem": 236
        },
        {
            "codUnidadMedida": "NIU",
            "cantidad": 1.0,
            "mtoValorVentaItem": 90,
            "mtoPrecioVentaUnitario": 118.0,
            "mtoValorReferencialUnitario": 0.0,
            "sumTotTributosItem":36.0,
            "tipAfectacion": "10",
            "cargoDescuentos": [
                {
                    "tipo": "descuento",
                    "monto": 10.0,
                    "base":100.0
                    }
                ],
            "tributos": [
                {
                    "ideTributo": "1000",
                    "nomTributo": "IGV",
                    "codTipTributo": "VAT",
                    "montoTributo": 16.2,
                    "baseTributo": 90,
                    "procentaje": 18
                    }
                ],
            "descripcion": "Gasolina 95",
            "codProducto": "123456",
            "codProductoSUNAT": "12334",
            "placa": "XYZ-123",
            "mtoValorUnitario": 100.0,
        }
        ]
}


import configparser
config = configparser.RawConfigParser()
config.read('src/common/servidores.conf')
config_details = dict(config.items('SUNAT'))
print(config_details)
