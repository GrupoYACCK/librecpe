from .error import LibreCpeError


class Empresa:
    
    def __init__(self, vals={}):
        self.nombre = vals.get('nombre', '').strip()
        self.nomComercial = vals.get('nomComercial', '-').strip()
        self.tipoDocumento = vals.get('tipoDocumento', '').strip()
        self.numDocumento = vals.get('numDocumento', '').strip()
        self.direccion = vals.get('direccion', '').strip()
        self.urbanizacion = vals.get('urbanizacion', '').strip()
        self.ubigeo = vals.get('ubigeo', '').strip()
        self.distrito = vals.get('distrito', '').strip()
        self.provincia = vals.get('provincia', '').strip()
        self.region = vals.get('region', '').strip()
        self.codPais = vals.get('codPais', '').strip()
        self.codEstablecimiento = vals.get('codEstablecimiento', '0000').strip()
        self.email = vals.get('email', '').strip()
    
    def validate(self):
        if not self.nombre:
            raise LibreCpeError("(emisor,adquiriente)/nombre", "No esta defenifido")
        if not self.tipoDocumento:
            raise LibreCpeError("(emisor,adquiriente)/tipoDocumento", "No esta defenifido")
        if not self.tipoDocumento:
            raise LibreCpeError("(emisor,adquiriente)/numDocumento", "No esta defenifido")
        return True


class Emisor(Empresa):
    
    def __init__(self, vals={}):
        super(Emisor, self).__init__(vals)
        self.codSucursal = vals.get('codSucursal', '0000').strip()
    
    def validate(self):
        res = super(Emisor, self).validate()
        if not self.codSucursal:
            raise LibreCpeError("emisor/codSucursal", "No esta defenifido")
        return res

    
class Adquirente(Empresa):
    
    def __init__(self, vals={}):
        super(Adquirente, self).__init__(vals)
        self.nomPersona = vals.get('nomPersona', '').strip()
        self.apPaterno = vals.get('apPaterno', '').strip()
        self.apMaterno = vals.get('apMaterno', '').strip()
        self.codSucursal = vals.get('codSucursal', '0000').strip()
        if not self.nombre:
            if self.nomPersona and self.apPaterno:
                self.nombre = "%s %s, %s" % (self.apPaterno, self.apMaterno, self.nomPersona)    
    
    def validate(self):
        res = super(Adquirente, self).validate()
        return res
        
class Transportista(Adquirente):
    def __init__(self, vals={}):
        super(Transportista, self).__init__(vals)
        self.licencia = vals.get('licencia', '').strip()
