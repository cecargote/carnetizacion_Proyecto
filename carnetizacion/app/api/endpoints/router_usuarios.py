from db.repository.usuario import create_new_user
from db.repository.usuario import delete_usuario_by_id
from db.session import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from schemas.usuario import ShowUsuario
from schemas.usuario import UsuarioCreate
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/create_usuario/", response_model=ShowUsuario)
def create_user(user: UsuarioCreate, db: Session = Depends(get_db)):
    user = create_new_user(user=user, db=db)
    return user


@router.delete("/delete_usuario/{id}")
def delete_usuario(id: int, db: Session = Depends(get_db)):
    message = delete_usuario_by_id(id=id, db=db)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con id {id} no existe",
        )
    return {"detail": "Eliminado completamente."}
