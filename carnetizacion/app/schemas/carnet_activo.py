from typing import Optional
from db.models.carnet_activo import estado
from pydantic import BaseModel


class CarnetActivoBase(BaseModel):
    folio: int
    comprobante_motivo: Optional[str] = None
    estado: estado = None

class CarnetActivoCreate(CarnetActivoBase):
    folio: int
    comprobante_motivo: str
    estado: estado

class ShowCarnetActivo(CarnetActivoBase):
    folio: int
    comprobante_motivo: str
    estado: estado

    class Config:
        orm_mode = True
