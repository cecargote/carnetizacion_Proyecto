from email.mime import image
from lib2to3.pgen2.token import OP
from typing import List
from typing import Optional

from fastapi import Request


class crearCarnetForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.estado: Optional[str] = "Solicitado"
        self.errorFolio: Optional[str] = ""
        self.errorMotivo: Optional[str] = ""
        self.rol: Optional[str]
        self.annoEstudiantePersona: int
        self.nombre: Optional[str]
        self.ci: Optional[str]
        self.comprobante_motivo: Optional[str]
        self.tipoPersona: Optional[str]
        self.area: Optional[str]
        self.area_anterior: Optional[str]
        self.rol_anterior: Optional[str]
        self.tipoMotivo: Optional[str]
        # self.estado: Optional[str]
        self.folio: int
        self.folio_desactivo: int
        # self.fotoCarnet: image
        
    async def load_data(self):
        form = await self.request.form()
        self.folio_desactivo= form.get("folio_desactivo")
        self.rol_anterior = form.get("rol_anterior")
        self.area_anterior = form.get("area_anterior")
        self.annoEstudiantePersona= form.get("annoEstudiantePersona")
        self.nombre= form.get("nombre")
        self.ci = form.get("ci")
        self.comprobante_motivo = form.get("comprobante_motivo")
        self.tipoPersona = form.get("tipoPersona")
        self.area = form.get("area")
        self.tipoMotivo = form.get("tipoMotivo")
        # self.estado = form.get("estado")
        self.rol = form.get("rol")
        self.folio = form.get("folio")
        # self.fotoCarnet = form.get("fotoCarnet")
    
    async def is_valid(self):
        if not self.folio:
            self.errorFolio= "Un folio es requerido"
        if not self.tipoMotivo or self.tipoMotivo=="Seleccione":
            self.errorMotivo =  "Un motivo es requerido"
        if not self.errorFolio and not self.errorMotivo:
            return True
        return False
        