from typing import List
from typing import Optional

from fastapi import Request


class BuscarPersonaForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errorCI: Optional[str] = ""
        self.users: List
        self.errorArea: Optional[str]= ""
        self.ciBuscarPersona: Optional[str]
        self.areaBuscarPersona: Optional[str]
        self.tipoBuscarPersona: Optional[str]
        self.errorTipo: Optional[str]
        self.Check1: bool
        self.Check2: bool
        self.Check3: bool
        self.Check4: bool

    async def load_data(self):
        form = await self.request.form()
        self.ciBuscarPersona = form.get("ciBuscarPersona")
        self.areaBuscarPersona = form.get("areaBuscarPersona")
        self.tipoBuscarPersona = form.get("tipoBuscarPersona")
        self.Check1 = form.get("Check1")
        self.Check2 = form.get("Check2")
        self.Check3 = form.get("Check3")
        self.Check4 = form.get("Check4")

    def is_valid(self):
        result = True
        if self.areaBuscarPersona == "Seleccione":
            self.errorArea = "*Este campo es obligatorio"
            result = False
       
        if  not len(self.ciBuscarPersona) == 11:
            self.errorCI = "*Un Carnet de Identidad no valido"
            result = False
        #if self.tipoBuscarPersona == "Seleccione":
        #    result = False

        return result
    
    def is_carntet_x_lotes(self):
        result = True
        if self.areaBuscarPersona == "Seleccione":
            self.errorArea = "*Este campo es obligatorio"
            result = False
        if self.tipoBuscarPersona == "Seleccione":
            self.errorTipo = "*Este campo es obligatorio"
            result = False

        return result


     