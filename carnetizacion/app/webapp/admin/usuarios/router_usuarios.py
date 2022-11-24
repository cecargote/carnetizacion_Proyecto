from api.endpoints.router_login import get_current_user_from_token
from db.models.usuario import Usuario
from db.repository.usuario import lista_usuarios
from db.session import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from pytest import Session


templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/usuario_admin")
async def usuarios(request: Request, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        print(token)
        print(scheme)
        lista_usuario = lista_usuarios(db=db)
        response = templates.TemplateResponse(
            "admin/usuarios/admin_usuarios.html",
            {"request": request, "lista_usuario": lista_usuario},
        )
        user_response = get_current_user_from_token(
            response=response, request=request, token=param, db=db
        )
        usuario_actual: Usuario = user_response["user"]
        print("El usuario actual es", usuario_actual)
        if (
            usuario_actual.rol_usuario == "Administrador"
            or usuario_actual.rol_usuario == "SuperAdmin"
        ):
            return user_response["response"]
    except Exception as e:
        print(e)
        return responses.RedirectResponse("login", status_code=status.HTTP_302_FOUND)
