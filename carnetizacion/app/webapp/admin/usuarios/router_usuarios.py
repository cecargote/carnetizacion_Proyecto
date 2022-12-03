from api.endpoints.router_login import get_current_user_from_token
from db.models.usuario import Usuario
from db.repository.usuario import lista_usuarios
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


@router.get("/usuario_admin")
async def usuarios(request: Request, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)  # scheme will hold "Bearer" and param will hold actual token value
        
        lista_usuario = lista_usuarios(db=db)
        response = templates.TemplateResponse(
            "admin/usuarios/admin_usuarios.html",
            {"request": request, "lista_usuario": lista_usuario},
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
        print("El Usuario no es Administrador")
        return responses.RedirectResponse("login", status_code=status.HTTP_302_FOUND)
