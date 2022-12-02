import jwt
from api.endpoints.router_login import get_current_user_from_token
from db.models.usuario import Usuario
from db.session import get_db
from fastapi import APIRouter
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.params import Depends
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from core.config import settings
import requests

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/admin")
async def admin(request: Request, 
db: Session = Depends(get_db),
):
     print("Cargando Admin")
     token = request.cookies.get("access_token")
     scheme, param = get_authorization_scheme_param(token)  # scheme will hold "Bearer" and param will hold actual token value
     responses = templates.TemplateResponse(
            "admin/admin_template.html", {"request": request}
        )
     current_user: Usuario = get_current_user_from_token(
            param, db
        ) 
     print (current_user.nombre_usuario)
     if (current_user.rol_usuario == "Administrador" or current_user.rol_usuario == "SuperAdmin"):
            print("Admin - > User: "+current_user.nombre_usuario)
            return responses
     print("El usuario actual no es admin -> Login")  
     return responses.RedirectResponse("login", status_code=status.HTTP_302_FOUND)

def cantidad_trabajadores():
    url = settings.API_AUDIENCE + "workers"
    
    area = "OU=Facultad de Ingenieria Mecanica,DC=cujae,DC=edu,DC=cu"
    data = { "area": area}
    responseURL = requests.post(url, auth=("fpicayo.sec", "Sigenu_sec_*2014*"),json=data)
    print ("url response "+responseURL.url+ " status: "+responseURL.status_code)
    
    print(responseURL.text)

    return None