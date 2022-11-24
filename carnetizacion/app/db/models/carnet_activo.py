from ast import Str
from unicodedata import name

from db.base_class import Base
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship


class estado(str, Enum):
    Solicitado = "Solicitado"
    Hecho = "Hecho"
    Entregado = "Entregado"


class CarnetActivo(Base):
    id = Column(Integer, primary_key=True, index=True)
    person_ci = Column(String, ForeignKey("person.ci"))
    folio = Column(Integer, nullable=False)
    tipo_motivo_id = Column(Integer, ForeignKey("tipomotivo.id_motivo"))
    comprobante_motivo = Column(String)
    estado = Column(
        Enum("Solicitado", "Hecho", "Entregado", name="estado", create_type=True)
    )
    # foto = Column(String)
