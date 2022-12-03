import imp

from api.endpoints.router_login import get_current_user_from_token
from db.models.usuario import Usuario
from db.repository.tipo_motivos import list_motivos
from db.session import get_db
from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from pytest import Session


templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/motivos_admin")
async def admin(request: Request, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        
        list_tipo_motivos = list_motivos(db=db)
        response = templates.TemplateResponse(
            "admin/motivos/admin_motivos.html",
            {"request": request, "list_tipo_motivos": list_tipo_motivos},
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
        return templates.TemplateResponse("login/login.html", {"request": request})
