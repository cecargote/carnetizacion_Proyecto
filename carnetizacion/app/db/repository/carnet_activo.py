from sqlalchemy.orm import Session
from sqlalchemy import desc

from schemas.carnet_activo import CarnetActivoCreate
from db.models.carnet_activo import CarnetActivo


def create_new_carnet_activo(carnet_activo: CarnetActivoCreate,db: Session,person_ci:int, tipo_motivo_id: int):
    carnet_activo_object = CarnetActivo(**carnet_activo.dict(),person_ci=person_ci, tipo_motivo_id= tipo_motivo_id)
    db.add(carnet_activo_object)
    db.commit()
    db.refresh(carnet_activo_object)
    return carnet_activo_object

def lista_solicitados(db: Session):
    carnets = db.query(CarnetActivo).filter(CarnetActivo.estado == "Solicitado").order_by(desc(CarnetActivo.id))
    return carnets

def get_carnet_by_person(person_ci: str,db: Session):
    carnet = db.query(CarnetActivo).filter(CarnetActivo.person_ci == person_ci).first()
    return carnet