
class Servidor:
    
    def __init__(self, ):
        self.servidores = {
            'sunat':'SUNAT',
            'nubefact_pse':'NubeFact PSE',
            'nubefact_ose':'NubeFact OSE',
            'otros':'Otros'
        }
        self.webservices = {
            'sunat' : {
                'desarrollo': {

                },
                'produccion': {
                    
                }
            },
            'nubefact_ose': {
                'desarrollo': {
                    'cpe': 'https://demo-ose.nubefact.com/ol-ti-itcpe/billService?wsdl'
                },
                'produccion': {

                }
            }
        }

    def getWebserviceServidores(self, servidor, tipo):
        return self.webservices.get(servidor, {}).get(tipo, {})

    def getServidores(self):
        res = []
        for codigo, nombre in self.servidores.items():
            res.append((codigo,nombre))
        return res
    
    def setServidor(self, vals={}):
        self.servidor = vals.get('servidor', 'sunat')
        self.url = vals.get('url', '')
        self.usuario = vals.get('usuario', '')
        self.clave = vals.get('clave', '')
        self.idCliente = vals.get('idCliente', '')
        self.claveCliente = vals.get('claveCliente', '')
        self.clientePython = vals.get('clientePython', 'pysimplesoap')
        return self