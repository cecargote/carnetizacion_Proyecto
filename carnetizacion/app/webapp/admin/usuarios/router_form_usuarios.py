from api.endpoints.router_login import get_current_user_from_token
from db.models.usuario import Usuario
from db.repository.usuario import create_new_user
from db.session import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from pytest import Session
from schemas.usuario import UsuarioCreate
from webapp.admin.usuarios.form_ususarios import CrearUsuarioForm

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/usuario_admin/form_usuario")
async def form_usuarios(request: Request, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        print(token)
        print(scheme)
        usuario = ""
        response = templates.TemplateResponse(
            "admin/usuarios/crear_usuario.html",
            {"request": request, "usuario": usuario},
        )
        user_response = get_current_user_from_token(
            response=response, request=request, token=param, db=db
        )
        usuario_actual: Usuario = user_response["user"]
        print("El usuario actual es", usuario_actual)
        if (
            usuario_actual.rol_usuario == "Carnetizador"
            or usuario_actual.rol_usuario == "SuperAdmin"
        ):
            return user_response["response"]

    except Exception as e:
        print(e)
        print("entro error")
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)


@router.post("/usuario_admin/form_usuario")
async def form_usuarios(request: Request, db: Session = Depends(get_db)):
    form = CrearUsuarioForm(request)
    await form.load_data()
    if form.is_valid():
        try:
            print("entro")
            print(form.rol_usuario)
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(token)
            response = responses.RedirectResponse(
                f"/usuario_admin", status_code=status.HTTP_302_FOUND
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
                usuario = UsuarioCreate(**form.__dict__)
                usuario = create_new_user(user=usuario, db=db)
                return user_response["response"]
        except HTTPException:
            print(HTTPException)
            return responses.RedirectResponse(
                "/login", status_code=status.HTTP_302_FOUND
            )
