from typing import List

from db.repository.tipo_motivos import create_tipo_motivo
from db.repository.tipo_motivos import delete_tipo_motivo_by_id
from db.repository.tipo_motivos import list_motivos
from db.repository.tipo_motivos import retreive_motivo
from db.repository.tipo_motivos import update_motivo_by_id
from db.session import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from schemas.tipo_motivo import ShowTipoMotivo
from schemas.tipo_motivo import TipoMotivoCreate
from sqlalchemy.orm import Session
from starlette.types import Message

router = APIRouter()


# @router.get("/motivos/", response_model=List[stm])
# async def show_motives(db: Session = Depends(get_db)):
#     motivos = db.query(tipo_motivo.TipoMotivo).all()
#     return motivos


@router.post("/create-motivo/", response_model=ShowTipoMotivo)
async def create_motivo(tipo_motivo: TipoMotivoCreate, db: Session = Depends(get_db)):
    tipo_motivo = create_tipo_motivo(tipo_motivo=tipo_motivo, db=db)
    return tipo_motivo


@router.get(
    "/get/{id}", response_model=ShowTipoMotivo
)  # if we keep just "{id}" . it would stat catching all routes
def read_motivo(id: int, db: Session = Depends(get_db)):
    motivo = retreive_motivo(id=id, db=db)
    if not motivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El motivo con este {id} no existe",
        )
    return motivo


@router.get("/all", response_model=List[ShowTipoMotivo])
def read_motivos(db: Session = Depends(get_db)):
    motivos = list_motivos(db=db)
    return motivos


@router.put("/update/{id}")
def update_motivo(
    id: int, tipo_motivo: TipoMotivoCreate, db: Session = Depends(get_db)
):
    message = update_motivo_by_id(id=id, tipo_motivo=tipo_motivo, db=db)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tipo de Motivo con id {id} no es correcto",
        )
    return {"msg": "Successfully updated data."}


@router.delete("/delete/{id}")
def delete_tipo_motivo(id: int, db: Session = Depends(get_db)):
    message = delete_tipo_motivo_by_id(id=id, db=db)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El motivo con este {id} no existe",
        )
    return {"detail": "Successfully deleted."}
