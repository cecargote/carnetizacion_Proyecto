from api.endpoints.router_login import get_current_user_from_token
from db.models.usuario import Usuario
from db.repository.usuario import retreive_usuario
from db.repository.usuario import update_usuario_by_id
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


@router.get("/usuario_admin/form_usuario/{id}")
async def edit_usuario(id: int, request: Request, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        usuario = retreive_usuario(id=id, db=db)
        response = templates.TemplateResponse(
            "admin/usuarios/crear_usuario.html",
            {"request": request, "usuario": usuario},
        )
        try:
            current_user: Usuario = get_current_user_from_token(param, db)
        except HTTPException:
            print("Error al cargar el usuario, sera enviado al LOGIN")
            return  responses.RedirectResponse("login", status_code=status.HTTP_401_UNAUTHORIZED)
        if (
            current_user.rol_usuario == "Administrador"
            or current_user.rol_usuario == "SuperAdmin"
        ):
            return response
    except Exception as e:
        print(e)
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)


@router.post("/usuario_admin/form_usuario/{id}")
async def edit_usuario(id: int, request: Request, db: Session = Depends(get_db)):
    form = CrearUsuarioForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(token)
            response = responses.RedirectResponse(
                f"/usuario_admin", status_code=status.HTTP_302_FOUND
            )
            try:
                current_user: Usuario = get_current_user_from_token(param, db)
            except HTTPException:
                print("Error al cargar el usuario, sera enviado al LOGIN")
                return  responses.RedirectResponse("login", status_code=status.HTTP_401_UNAUTHORIZED)
            if (
                current_user.rol_usuario == "Administrador"
                or current_user.rol_usuario == "SuperAdmin"
            ):
                usuario = UsuarioCreate(**form.__dict__)
                update_usuario_by_id(id=id, usuario=usuario, db=db)
                return response
        except HTTPException:
            print(HTTPException)
            return responses.RedirectResponse(
                "/login", status_code=status.HTTP_302_FOUND
            )
