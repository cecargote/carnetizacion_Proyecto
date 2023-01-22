from sqlalchemy.orm import Session
from sqlalchemy import desc

from schemas.carnet_eliminado import CarnetEliminadoCreate
from db.models.carnet_eliminado import CarnetEliminado

def create_new_carnet_eliminado(carnet_eliminado: CarnetEliminadoCreate,db: Session,person_ci:int):

    carnet_eliminado_object = CarnetEliminado(**carnet_eliminado.dict(),person_ci=person_ci)
    db.add(carnet_eliminado_object)
    db.commit()
    db.refresh(carnet_eliminado_object)
    return carnet_eliminado_object

def lista_eliminados(db: Session):
    carnets = db.query(CarnetEliminado).order_by(desc(CarnetEliminado.id))
    return carnets