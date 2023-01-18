from db.models.usuario import Usuario
from schemas.usuario import UsuarioCreate
from sqlalchemy.orm import Session


def create_new_user(user: UsuarioCreate, db: Session):
    user = Usuario(
        nombre_usuario=user.nombre_usuario,
        is_activo=False,
        rol_usuario=user.rol_usuario,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def lista_usuarios(db: Session):
    usuarios = db.query(Usuario).all()
    return usuarios


def retreive_usuario(id: int, db: Session):
    item = db.query(Usuario).filter(Usuario.id == id).first()
    return item


def update_usuario_by_id(id: int, usuario: UsuarioCreate, db: Session):
    exist_usuario = db.query(Usuario).filter(Usuario.id == id)
    if not exist_usuario.first():
        return 0
    exist_usuario.update(usuario.__dict__)
    db.commit()
    return 1


def delete_usuario_by_id(id: int, db: Session):
    existing_usuario = db.query(Usuario).filter(Usuario.id == id)
    if not existing_usuario.first():
        return 0
    existing_usuario.delete(synchronize_session=False)
    db.commit()
    return 1


def update_state_usuario_by_id_logout(id: int, db: Session):
    exist_usuario = db.query(Usuario).filter(Usuario.id == id)
    if not exist_usuario.first():
        return 0
    exist_usuario.update({"is_activo": False})
    db.commit()
    return 1
