from lxml import etree
import logging
import json

DOC_CODE = {
    '01': '01',
    '03': '03',
    '07': '07',
    '08': '08'
}

_logger = logging.getLogger(__name__)
class TCI:
    def __init__(self, documento=None):
        self.documento = documento
        self.oGeneral = {'oGeneral': {}}

    def get_empresa(self):

        vals = {
            "oENEmpresa": {
                "CodigoTipoDocumento": self.documento.emisor.tipoDocumento,
                "Ruc": self.documento.emisor.numDocumento,
                "CodPais": self.documento.emisor.codPais,
                "CodigoEstablecimientoSUNAT": self.documento.emisor.codEstablecimiento,
                "RazonSocial": self.documento.emisor.nombre,
                "CodDistrito": self.documento.emisor.ubigeo,
                "NombreComercial": self.documento.emisor.nomComercial,
                "Calle": self.documento.emisor.direccion,
                "Urbanizacion": self.documento.emisor.urbanizacion,
                "Departamento": self.documento.emisor.region,
                "Provincia": self.documento.emisor.provincia,
                "Distrito": self.documento.emisor.distrito,
                "Fax": self.documento.emisor.telefono,
                "IdEmpresa": "0",
                "IdEstado": "0",
                "IdPais": "0",
                "IdTipoDocumento": "0",
                "IdUsuario": "0",
                "Telefono": self.documento.emisor.telefono,
                "Correo": self.documento.emisor.email,
                "Web": self.documento.emisor.web
            },
            "Autenticacion": {
                "Ruc": self.documento.emisor.numDocumento
            },
            "IdSeguimiento": "0",
        }
        return vals

    def get_ubl(self):
        return {"VersionUbl": '2.1'}

    def get_descuento_cargo(self):
        descuentos = []
        desc = 0.0
        for descuento in self.documento.cargoDescuentos:
            if self.documento.tipoDocumento not in ['07', '08']:
                descuentos.append({
                    "ENDescuentoCargoCabecera": {
                        "CodigoMotivo": descuento.codigo,
                        # "Descripcion": descuento.descripcion or '',
                        "IdComprobanteDetalle": 0,
                        "IdDescuentoCargoCabecera": 0,
                        "Indicador": descuento.indicador == 'false' and '0' or '1',
                        "Monto": descuento.monto,
                        "MontoBase": descuento.base,
                        "Porcentaje": descuento.porcentaje * 100
                    }
                })
                if descuento.indicador == 'false':
                    desc+=descuento.monto
        return descuentos, desc

    def get_comprobante(self):

        vals = {
            "oENComprobante": {
                "CantidadRegistros": "0",
                "CargoNoAfecto": "0",
                "CodigoCliente": self.documento.adquirente.codigo,
                "ComprobanteDetalle": self.get_detalles(),
                "ComprobanteImpuestos": self.get_tributos(),
                "ComprobantePropiedadesAdicionales": self.get_propiedades_adicionales(),
                "ComprobanteGrillaCuenta": self.get_detalles_adicionales(),
                "CorreoElectronico": self.documento.adquirente.email,
                "DescuentoGlobal": self.documento.totalDescuentos,
                "DescuentoNoAfecto" : "0",
                "FiltroFechas": 'false',
                "Grabadas": "0",
                "IdComp": 0,
                "IdComprobante": 0,
                "IdComprobanteCabecera": 0,
                "IdCorreoRecepcion": 0,
                "IdEmpresa": 0,
                "IdPuntoVenta": 0,
                "IdSeguimiento": 0,
                "IdTipoOrigen": 0,
                "IdTransaccion": 0,
                "IdUsuario": 0,

                "Fecha": "0001-01-01T00:00:00",
                "FechaEmisionDesde": "0001-01-01T00:00:00",
                "FechaEmisionHasta": "0001-01-01T00:00:00",
                "FechaObtencion": "0001-01-01T00:00:00",
                "FechaPedido": "0001-01-01T00:00:00",
                "NumeroPagina": 0,
                "OtroConceptoPago": 0,

                "Serie": self.documento.numero.split('-')[0],
                "Numero": self.documento.numero.split('-')[-1],
                "FechaEmision": self.documento.fecEmision.strftime("%Y-%m-%dT%H:%M:%S"),
                "HoraEmision": self.documento.fecEmision.strftime("%H:%M:%S"),
                "TipoComprobante": self.documento.tipoDocumento,
                "Moneda": self.documento.tipMoneda,
                "Multiglosa": self.documento.notas and [self.documento.notas] or [],
                "TipoPago": self.documento.medioPago.tipo == 'Contado' and '1' or '0',
                "NroOrdenCompra": self.documento.referencia,
                "TotalPrepago": self.documento.totalAnticipos,
                "TipoOperacion": self.documento.tipOperacion,
                "TipoDocumentoIdentidad": self.documento.adquirente.tipoDocumento,
                "Ruc": self.documento.adquirente.numDocumento,
                "RazonSocial": self.documento.adquirente.nombre,
                "TotalCargo": self.documento.totalCargos,
                "ImporteTotal": self.documento.totalVenta,
                "MontoExonerado": "0.0",
                "MontoGratuito": "0.0",
                "MontoIGV": "0.0",
                "MontoISC": "0.0",
                "MontoISC": "0.0",
                "MontoInafecto": "0.0",
                "NrodePedido": self.documento.referencia,
                # "ComprobanteMotivosDocumentos": self.get_motivo(),
                "Receptor": self.get_receptor(),
                # "ComprobanteGrillaCuenta": self.get_detalles_adicionales(),
                # "Vendedor": self.get_vendedor(),
                "Sucursal": self.get_sucursal(),
                "FormaPago": self.get_forma_pago(),
                "FormaPagoSunat": self.get_forma_pago_sunat(),
                "MontosTotales": self.get_montos_totales(),
                "TotalImpuesto": self.documento.totalTributos,
                "TotalPrecioVenta": self.documento.totalVenta,
                "TotalValorVenta": self.documento.totalValVenta,
                "VersionUbl": "2.1",

            }
        }
        if self.documento.cargoDescuentos:
            descuentos, desc = self.get_descuento_cargo()
            vals['oENComprobante']['DescuentoCargoCabecera'] = descuentos
            vals['oENComprobante']['DescuentoGlobal'] = desc
        if self.documento.documentosModificados and self.documento.tipoDocumento in ['07', '08']:
            motivos, ref = self.get_motivo()
            vals['oENComprobante']['ComprobanteMotivosDocumentos'] = motivos
            vals['oENComprobante']['ComprobanteNotaCreditoDocRef'] = ref
        if self.documento.vendedor:
            vals['oENComprobante']['Vendedor'] = self.get_vendedor()
        # if self.documento.tipoDocumento in ['07', '08']:
        #     vals['oENComprobante']['ENComprobanteMotivoDocumento'] = self.get_motivo()
        vals['flagAdjunto'] = '0'
        # Detraccion
        # FormaPagoSunat
        return vals

    def get_detraccion(self):
        vals = {}
        if self.documento.detraccion:
            vals['ENDetraccion'] = {
                "BienesServicios" : {
                    "ENBienesServicios": {
                        "Codigo": '3000',
                        "Valor": self.documento.detraccion.codigo
                    }
                },
                "CodigoBienServicio": '0',
                "NumeroCuenta": {
                    "ENNumeroCuenta": {
                        "Codigo": '3001',
                        "CodigoFormaPago": self.documento.detraccion.medioPago,
                        "Valor": self.documento.detraccion.cuentaBanco
                    }
                },
                "Porcentaje": {
                    "ENPorcentaje": {
                        "Codigo": '2003',
                        "Valor": self.documento.detraccion.porcentaje
                    }
                }
            }
        return vals

    def get_montos_totales(self):
        vals = {}
        for tributo in self.documento.tributos:
            if tributo.ideTributo == '9997':
                vals['Exonerado']=  {'Total': tributo.montoTributo}
            if tributo.ideTributo == '9995':
                vals['Exportacion'] = {'Total': tributo.montoTributo}
            if tributo.ideTributo == '9996':
                vals['Gratuito'] = {'GratuitoImpuesto': {
                                        'Base': tributo.baseTributo,
                                        'ValorImpuesto': tributo.montoTributo},
                                    'Total': tributo.baseTributo
                                    }
            if tributo.ideTributo == '1000':
                vals['Gravado'] = {'GravadoIGV': {
                                        'Base': tributo.baseTributo,
                                        'Porcentaje': tributo.procentaje,
                                        'ValorImpuesto': tributo.montoTributo},
                    'Total': tributo.baseTributo
                }
        return vals

    def get_motivo(self):
        # oGeneral.ENComprobante. ENComprobanteMotivoDocumento
        mod = []
        ref = []
        for modificados in self.documento.documentosModificados:
            motivo = {"ENComprobanteMotivoDocumento": {
                    "SerieDocRef": modificados.numero.split('-')[0],
                    "NumeroDocRef": modificados.numero.split('-')[-1],
                    "CodigoMotivoEmision": self.documento.codigoNota,
                    "Sustentos": [
                        {"ENComprobanteMotivoDocumentoSustento" :{
                                "Sustento": self.documento.motivo
                            }
                        }
                    ]
                }
            }
            referencia = {
                "ENComprobanteNotaDocRef": {
                    "Serie": modificados.numero.split('-')[0],
                    "Numero": modificados.numero.split('-')[-1],
                    "TipoComprobante": modificados.tipoDocumento,
                    "FechaDocRef": modificados.fecEmision
                }
            }
            ref.append(referencia)
            mod.append(motivo)
        return mod, ref ##{'ENComprobanteMotivoDocumento': mod}

    # oGeneral.ENComprobante.ENComprobanteNotaDocRef
    # .Serie
    # .Numero
    # .TipoComprobante
    # .FechaDocRef

    def get_receptor(self):
        vals = {
            "ENReceptor": {
                "Calle": self.documento.adquirente.direccion,
                # "Urbanizacion": self.documento.adquirente.urbanizacion,
                "Departamento": self.documento.adquirente.region,
                "Provincia": self.documento.adquirente.provincia,
                "Distrito": self.documento.adquirente.distrito,
                "CodPais": self.documento.adquirente.codPais
            }
        }
        return vals

    def get_detalles(self):
        vals ={}
        detalles = []
        item = 1
        for detalle in self.documento.detalles:
            val = {
                "BaseComision": 0,
                "Bulto": 0,
                "Comision": 0,
                "Costo": 0,
                "DescuentoIncIgv": 0,
                "Determinante": 1,
                "IdComprobante": 0,
                "IdComprobanteDetalle": 0,
                "ImporteBrutoItem": 0,
                "PesoNeto": 0,
                "PrecioVentaItem": 0,
                "Nota": "SIRENA",
                "Fecha": "0001-01-01T00:00:00",
                "FechaCaducidad": "0001-01-01T00:00:00",
                "UnidadComercial": detalle.codUnidadMedida,
                "UnidadMedidaEmisor": detalle.codUnidadMedida,
                "Cantidad": detalle.cantidad,
                "Total": detalle.mtoValorVentaItem,
                "CodigoTipoPrecio": '01' if detalle.mtoValorReferencialUnitario == 0.0 else '02',
                # Es sin impuesto revisar
                "ValorVentaUnitario": detalle.mtoValorUnitario,
                "ValorVentaUnitarioIncIgv": detalle.mtoPrecioVentaUnitario,
                "Descripcion": detalle.descripcion,
                "Codigo": detalle.codProducto,
                "CodigoProductoSunat" : detalle.codProductoSUNAT,
                "Item": str(item),
                "ImpuestoTotal": detalle.sumTotTributosItem,
            }
            item+=1
            descuento_porcentaje = 0.0
            descuentos = []
            for descuento in detalle.cargoDescuentos:
                if self.documento.tipoDocumento not in ['07', '08']:
                    for desc in detalle.cargoDescuentos:
                        descuentos.append({
                            'ENDescuentoCargoDetalle': {
                                'CodigoAplicado': desc.codigo,
                                #'Descripcion': 0,
                                'IdComprobanteDetalle': 0,
                                'IdDescuentoCargoCabecera': 0,
                                'Indicador': desc.indicador == 'false' and '0' or '1',
                                'Monto': desc.monto,
                                'MontoBase': desc.base,
                                'Porcentaje': desc.porcentaje*100
                            }
                        })
                        if desc.indicador == 'false':
                            descuento_porcentaje += desc.porcentaje*100
            val['DescuentoCargoDetalle'] = descuentos
            if descuento_porcentaje:
                val['PorcentajeDescuento'] = descuento_porcentaje
            else:
                val['PorcentajeDescuento'] = 0.0
            val['ComprobanteDetalleImpuestos'] = []
            for tributo in detalle.tributos:
                impuesto = {}
                impuesto["ENComprobanteDetalleImpuestos"] = {
                    "IdComprobanteDetalle": 0,
                    "IdComprobanteDetalleImpuestos": 0,
                    "ImpuestoPorcentual": 0,
                    "ImpGratuito": 0,
                    "ImporteTributo": tributo.montoTributo,
                    "ImporteExplicito": tributo.montoTributo,
                    "AfectacionIGV": detalle.tipAfectacion,
                    "CodigoTributo": tributo.ideTributo,
                    "DesTributo": tributo.nomTributo,
                    "CodigoUN": tributo.codTipTributo,
                    "MontoBase" : tributo.baseTributo,
                    "TasaAplicada": tributo.procentaje
                }
                val['ComprobanteDetalleImpuestos'].append(impuesto)

            detalles.append(val)
        vals['ENComprobanteDetalle'] = detalles
        return vals

    def get_propiedades_adicionales(self):
        # oGeneral.ENComprobante.ENComprobantePropiedadesAdicionales
        adicionales = []
        for leyenda in self.documento.leyendas:
            propiedades_adicionales = {
                "Codigo": leyenda.codLeyenda,
                "IdComprobante": 0,
                "IdComprobantePropiedadesAdicionales": 0,
                "Valor": leyenda.desLeyenda
            }
            adicionales.append(propiedades_adicionales)

        vals = {
            "ENComprobantePropiedadesAdicionales": adicionales
        }
        return vals

    def get_detalles_adicionales(self):
        #ComprobanteGrillaCuenta
        grilla_cuenta = []

        for detalle in self.documento.detallesAdicionales:
            grilla_cuenta.append({
                "Codigo": detalle.descripcion,
                "Valor1": detalle.valor1,
                "Valor2": detalle.valor2,
                "Valor3": detalle.valor3
            })
        vals = {"ENComprobanteGrillaCuenta": grilla_cuenta}
        return vals

    def get_vendedor(self):
        if self.documento.vendedor:
            vals = {
                "ENVendedor": {
                    "Codigo": self.documento.vendedor.codigo,
                    "Nombre": self.documento.vendedor.nombre
                }
            }
            return vals
        else:
            return {}

    def get_prepago(self):
        vals = {}
        if self.documento.tipoDocumento in ['01', '03']:
            i = 1
            prepago = []
            for anticipo in self.documento.anticipos:
                prepago.append({
                    "Codigo": i,
                    "Monto": anticipo.monto,
                    "Valor": anticipo.valor
                })
                i += 1
            vals = {"ENPrepago": prepago}
        return vals

    def get_sucursal(self):
        vals = {
            "ENSucursal": {
                "Direccion": self.documento.emisor.direccion,
                "Distrito": self.documento.emisor.distrito,
                "Provincia": self.documento.emisor.provincia,
                "Departamento": self.documento.emisor.region,
                "Telefono": self.documento.emisor.telefono
            }
        }
        return vals

    def get_forma_pago(self):
        vals = {}
        vals.update({
            "ENFormaPago": {
                "CodigoFormaPago": '008',
                "DiasVencimiento": '0',
                "FechaVencimiento": self.documento.fecVencimiento or self.documento.fecEmision.strftime("%Y-%m-%d"), #, fecha or self.documento.fecEmision.strftime("%Y-%m-%d"),
                # Revisar
                "NotaInstruccion": "",
            }
        })
        return vals

    def get_forma_pago_sunat(self):
        vals = {}
        cuotas = []
        for cuota in self.documento.medioPago.cuotas:
            cuotas.append({
                'ENCuotaPago': {
                    'FechaPago': cuota.fecha,
                    'Monto': cuota.monto,
                }
            })
            # fecha = cuota.fecha
        vals.update({
            'MontoPendientePago': self.documento.medioPago.monto,
            'TipoFormaPago': self.documento.medioPago.tipo == 'Contado' and '1' or '2',
            'CuotaPago': cuotas
        })
        return vals

    def get_tributos(self):
        impuestos = []
        for tributo in self.documento.tributos:
            impuestos.append({
                "IdComprobante": 0,
                "IdComprobanteImpuestos": 0,
                "ImporteTributo": tributo.montoTributo,
                "ImporteExplicito": tributo.montoTributo,
                "CodigoTributo": tributo.ideTributo,
                "DesTributo": tributo.nomTributo,
                "Porcentaje": tributo.procentaje,
                "CodigoUN": tributo.codTipTributo,
                "MontoBase": 0.0, #tributo.baseTributo,
            })
        vals = {
            "ENComprobanteImpuestos": impuestos
        }
        return vals

    def get_documento(self):
        vals = {}
        if self.documento.tipoDocumento and self.documento.tipoDocumento not in ['09']:
            vals.update(self.get_empresa())
            vals.update(self.get_comprobante())
            vals['IdSeguimiento'] = '0'
        else:
            # ent_GuiaRemisionRemitente.at_ControlOtorgamiento
            documentos_relacionados = []
            for relacionado in self.documento.documentosRelacionados:
                documentos_relacionados.append({
                    "en_DocumentoRelacionadoGRR": {
                        "at_NumeroComprobante": relacionado.numero,
                        "at_TipoComprobante": relacionado.tipoDocumento,
                    }
                })
            vals.update({
                "ent_Autenticacion": {
                    "at_Ruc": self.documento.emisor.numDocumento,
                },
                "ent_RemitenteGRR": {
                    "at_NumeroDocumentoIdentidad": self.documento.emisor.numDocumento,
                    "at_RazonSocial": self.documento.emisor.nombre,
                    "at_NombreComercial": self.documento.emisor.nomComercial,
                    "at_Telefono": self.documento.emisor.telefono,
                    "at_CorreoContacto": self.documento.emisor.email,
                    "at_SitioWeb": self.documento.emisor.web,
                    "ent_DireccionFiscal": {
                        "at_Ubigeo": self.documento.emisor.ubigeo,
                        "at_DireccionDetallada": self.documento.emisor.direccion,
                        "at_Urbanizacion": self.documento.emisor.urbanizacion,
                        "at_Provincia": self.documento.emisor.provincia,
                        "at_Departamento": self.documento.emisor.region,
                        "at_Distrito": self.documento.emisor.distrito,
                        "at_CodigoPais": self.documento.emisor.codPais,
                    },
                },

                "ent_DestinatarioGRR": {
                    "at_TipoDocumentoIdentidad": self.documento.remitente.tipoDocumento,
                    "at_NumeroDocumentoIdentidad": self.documento.remitente.numDocumento,
                    "at_RazonSocial": self.documento.remitente.nombre,
                    "ent_Correo": {
                        "at_CorreoPrincipal": self.documento.remitente.email,
                        "aa_CorreoSecundario": ""
                    },
                },
                # ent_Proveedor
                # ent_DatosGenerales
                "ent_DatosGeneralesGRR": {
                    "at_FechaEmision": self.documento.fecEmision.strftime("%Y-%m-%d"),
                    "at_Serie": self.documento.numero.split('-')[0],
                    "at_Numero": self.documento.numero.split('-')[-1],
                    "at_Observacion": self.documento.observacion or '',
                    "at_FechaEnvio": self.documento.fecEmision.strftime("%Y-%m-%d %H:%M:%S"),
                    # Opcional
                    "at_HoraEmision": self.documento.fecEmision.strftime("%H:%M:%S"),
                    # l_ComprobanteAnteriorGRR
                    "l_DocumentoRelacionadoGRR": documentos_relacionados,
                    "ent_InformacionTrasladoGRR": {
                        "at_CodigoMotivo": self.documento.motivo,
                        "at_DescripcionMotivo": self.documento.descripcion,
                        "at_IndicadorMotivo": self.documento.transbordo,
                        "ent_InformacionPesoBrutoGRR": {
                            "at_Peso": self.documento.pesoBruto,
                            "at_UnidadMedida": self.documento.pesoBrutoUnidad,
                            "at_Cantidad": self.documento.bultos,
                        },
                        "l_InformacionTransporteGRR": self.get_informacion_transporte(),
                        "l_BienesGRR": self.get_bienes(),
                        "ent_InformacionAdicionalTotales": {
                            "at_PesoNeto": self.documento.pesoBruto,
                            "at_PesoBruto": self.documento.pesoBruto,
                            # Revisar
                            "at_CantidadBobina": self.documento.bultos,
                            "at_CantidadBienes": self.documento.bultos,
                        },
                        "ent_PuntoLlegadaGRR": {
                            "at_Ubigeo": self.documento.ubigeoLlegada,
                            "at_DireccionCompleta": self.documento.direccionLlegada,
                            # "at_Urbanizacion": self.documento.destino.urbanizacion,
                            # "at_Provincia": self.documento.destino.provincia,
                            # "at_Departamento": self.documento.destino.region,
                            # "at_Distrito": self.documento.destino.distrito,
                            # "at_CodigoPais": self.documento.destino.codPais,
                            # "at_CodigoEstablecimiento": self.documento.codSucursalLlegada,
                            # "at_NumeroDocumentoIdentidad": self.documento.rucLlegada,
                        },
                        "ent_PuntoPartidaGRR": {
                            "at_Ubigeo": self.documento.ubigeoPartida,
                            "at_DireccionCompleta": self.documento.direccionPartida,
                            # "at_Urbanizacion": self.documento.origen.urbanizacion,
                            # "at_Provincia": self.documento.origen.provincia,
                            # "at_Departamento": self.documento.origen.region,
                            # "at_Distrito": self.documento.origen.distrito,
                            # "at_CodigoPais": self.documento.origen.codPais,
                            # "at_CodigoEstablecimiento": self.documento.codSucursalPartida,

                        }
                    },

                },
                "at_ControlOtorgamiento": True
            })

            if self.documento.codSucursalLlegada:
                vals['ent_DatosGeneralesGRR']["ent_InformacionTrasladoGRR"]["ent_PuntoLlegadaGRR"]["at_CodigoEstablecimiento"] = self.documento.codSucursalLlegada
                vals['ent_DatosGeneralesGRR']["ent_InformacionTrasladoGRR"]["ent_PuntoLlegadaGRR"]["at_NumeroDocumentoIdentidad"] = self.documento.emisor.numDocumento
            if self.documento.codSucursalPartida:
                vals['ent_DatosGeneralesGRR']["ent_InformacionTrasladoGRR"]["ent_PuntoPartidaGRR"]["at_CodigoEstablecimiento"] = self.documento.codSucursalLlegada
                vals['ent_DatosGeneralesGRR']["ent_InformacionTrasladoGRR"]["ent_PuntoPartidaGRR"]["at_NumeroDocumentoIdentidad"] = self.documento.emisor.numDocumento

        _logger.info(json.dumps(vals))
        return vals

    # Guia de Remisión Remitente
    def get_informacion_transporte(self):
        vals = {
            "en_InformacionTransporteGRR": {
                "at_Modalidad": self.documento.modoTraslado,
                "at_FechaInicio": self.documento.fechaTraslado #.strftime("%Y-%m-%d %H:%M:%S"),
            }
        }
        if self.documento.modoTraslado == '01':
            publico = {}
            for transportista in self.documento.transportistas:
                if transportista.tipoDocumento == '6':
                    publico['at_TipoDocumentoIdentidad'] = transportista.tipoDocumento
                    publico['at_NumeroDocumentoIdentidad'] = transportista.numDocumento
                    publico['at_RazonSocial'] = transportista.nombre
                    if transportista.numRegistro:
                        publico['at_NumeroMTC'] = transportista.numRegistro
                    # Revisar en test
                    vehículos = []
                    for vehículo in self.documento.vehículos:
                        vehículos.append({
                            "en_VehiculoGRR": {
                                "aa_NumeroPlaca": vehículo.placa.replace("-", ""),
                            }
                        })
                    publico['l_VehiculoGRR'] = vehículos
                    transportistas = []
                    for transp in self.documento.transportistas:
                        if transp.tipoDocumento != '6':
                            transportistas.append({
                                "en_ConductorGRR": {
                                    "at_TipoDocumentoIdentidad": transp.tipoDocumento,
                                    "at_NumeroDocumentoIdentidad": transp.numDocumento,
                                    "at_Licencia": transp.nombre,
                                    "at_Nombres": transp.nomPersona or '',
                                    "at_Apellidos": transp.apPaterno + ' ' + transp.apMaterno,
                                }
                            })
                    publico['l_ConductorGRR'] = transportistas

            vals['ent_TransportePublicoGRR'] = publico
        elif self.documento.modoTraslado == '02':
            privado = {}
            for transportista in self.documento.transportistas:
                if transportista.tipoDocumento != '6':
                    vehículos = []
                    for vehículo in self.documento.vehículos:
                        vehículos.append({
                            "en_VehiculoGRR": {
                                "aa_NumeroPlaca": vehículo.placa.replace("-", ""),
                            }
                        })
                    privado['l_VehiculoGRR'] = vehículos
                    transportistas = []
                    for transp in self.documento.transportistas:
                        if transp.tipoDocumento != '6':
                            transportistas.append({
                                "en_ConductorGRR": {
                                    "at_TipoDocumentoIdentidad": transp.tipoDocumento,
                                    "at_NumeroDocumentoIdentidad": transp.numDocumento,
                                    "at_Licencia": transp.nombre,
                                    "at_Nombres": transp.nomPersona or '',
                                    "at_Apellidos": transp.apPaterno + ' ' + transp.apMaterno,
                                }
                            })
                    privado['l_ConductorGRR'] = transportistas

            vals['ent_TransportePrivadoGRR'] = privado
        return vals

    def get_bienes(self):
        bienes = []
        for bien in self.documento.detalles:
            bienes.append({
                "en_BienesGRR": {
                    "at_Cantidad": bien.cantidad,
                    "at_UnidadMedida": bien.codUnidadMedida,
                    "at_Descripcion": bien.descripcion,
                    "at_Codigo": bien.codProducto,
                }
            })
        return bienes

    def get_comunicacion_baja(self):
        vals = {}
        # vals.update(self.get_empresa())
        vals['oENEmpresa'] = {
                'Ruc': self.documento.emisor.numDocumento
            }
        vals['oENNumeradosNoEmitidosCab'] = {}
        vals['oENNumeradosNoEmitidosCab']['FechaGeneracion'] = self.documento.fecEnvio
        vals['oENNumeradosNoEmitidosCab']['FechaEmision'] = self.documento.fecEmision

        i = 1
        numerados_no_emitido = []
        # ENNumeradosNoEmitidosCab.ENNumeradosNoEmitidos
        for anulado in self.documento.documentosAnulados:
            numerados_no_emitido.append({
                'ENNumeradosNoEmitidos': {
                    "Item": str(i),
                    "CodigoTipoDocumento": anulado.tipoDocumento,
                    "SerieDocumento": anulado.serie,
                    "NumeroDocumento": str(int(anulado.numero)),
                    "MotivoBaja": anulado.descripcion
                }
            })
        vals['oENNumeradosNoEmitidosCab']['NumeradosNoEmitidos'] = numerados_no_emitido
        return vals



