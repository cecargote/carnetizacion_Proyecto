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
import json
templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/admin")
async def admin(request: Request, 
db: Session = Depends(get_db),
):
     print("Cargando Admin")

     count= repr(cantidad_trabajadores())
     print ("count "+count)
     token = request.cookies.get("access_token")
     scheme, param = get_authorization_scheme_param(token)  # scheme will hold "Bearer" and param will hold actual token value
     
     responses = templates.TemplateResponse(
            "admin/admin_template.html", {"request": request, "count": count})
     
     current_user: Usuario = get_current_user_from_token(
            param, db
        ) 
     print (current_user.nombre_usuario)
     if (current_user.rol_usuario == "Administrador" or current_user.rol_usuario == "SuperAdmin"):
            print("Admin - > User: "+current_user.nombre_usuario)
            return responses
     print("El usuario actual no es admin -> Login")  
     return responses.RedirectResponse("login", status_code=status.HTTP_302_FOUND)

def cantidad_trabajadores_totales():
 
    reqUrl = "https://sigenu.cujae.edu.cu/sigenu-ldap-cujae/ldap/persons?area=OU=DG de ICI,OU=Area Central,DC=cujae,DC=edu,DC=cu"
    headersList = {
    "Accept": "*/*",
    "User-Agent": "Thunder Client (https://www.thunderclient.com)",
    "Authorization": "Basic ZGlzZXJ0aWMubGRhcDpkaXNlcnRpYyoyMDIyKmxkYXA=" 
        }

    payload = ""

    response = requests.request("GET", reqUrl, data=payload,  headers=headersList)
    
    responseArray = response.json()
    count =len(responseArray)
    print("cantidad total de trabajadores ",count)
    return count