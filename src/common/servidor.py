
class Servidor:
    
    def __init__(self, ):
        self.servidores = {
            'sunat':'SUNAT',
            'nubefact_pse':'NubeFact PSE'
        }
    
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
        return self