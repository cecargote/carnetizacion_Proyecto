from api.endpoints.router_login import get_current_user_from_token
from db.models.usuario import Usuario
from db.repository.tipo_motivos import create_tipo_motivo
from db.repository.tipo_motivos import list_motivos
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
from schemas.tipo_motivo import TipoMotivoCreate
from webapp.admin.tipo_de_motivos.form_crear_motivos import CrearMotivoForm


templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/motivos_admin/crear-motivo")
async def motivos_crear(request: Request, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        print(token)
        print(scheme)
        tipo_motivo = ""
        response = templates.TemplateResponse(
            "admin/motivos/crear_motivos.html",
            {"request": request, "tipo_motivo": tipo_motivo},
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
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)


@router.post("/motivos_admin/crear-motivo")
async def motivos_crear(request: Request, db: Session = Depends(get_db)):
    form = CrearMotivoForm(request)
    await form.load_data()
    if form.is_valid():
        try:
            print("entro")
            print(form.nombre_motivo)
            print(form.is_valid())
            print(form.error_nombre_motivo)
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(token)
            response = responses.RedirectResponse(
                f"/motivos_admin", status_code=status.HTTP_302_FOUND
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
                tipo_motivo = TipoMotivoCreate(**form.__dict__)
                tipo_motivo = create_tipo_motivo(tipo_motivo=tipo_motivo, db=db)
                return user_response["response"]
        except HTTPException:
            return responses.RedirectResponse(
                "/login", status_code=status.HTTP_302_FOUND
            )
