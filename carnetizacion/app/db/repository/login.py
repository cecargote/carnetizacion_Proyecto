from db.models.usuario import Usuario
from sqlalchemy.orm import Session


def get_user(nombre_usuario: str, db: Session):
    #print("entro")
    user = db.query(Usuario).filter(Usuario.nombre_usuario == nombre_usuario).first()
    #print("el user es")
    #print(user)
    return user


def update_state_usuario_by_id(id: int, db: Session):
    exist_usuario = db.query(Usuario).filter(Usuario.id == id)
    if not exist_usuario.first():
        return 0
    print(exist_usuario)
    print(exist_usuario.first())
    print(exist_usuario.__dict__)
    print(exist_usuario.first().is_activo)
    # user = Usuario(
    #     nombre_usuario=user.nombre_usuario,
    #     is_activo=False,
    #     rol_usuario=user.rol_usuario,
    # )
    # db.add(user)
    exist_usuario.update({"is_activo": True})
    db.commit()
    return 1
