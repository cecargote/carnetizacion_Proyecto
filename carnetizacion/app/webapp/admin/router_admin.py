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


templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/admin")
async def admin(request: Request, db: Session = Depends(get_db)):
     responses = templates.TemplateResponse(
            "admin/admin_template.html", {"request": request}
        )
     print("estoy en dmin")
     return responses
     try:
        response = templates.TemplateResponse(
            "admin/admin_template.html", {"request": request}
        )
        #user_response 
        #usuario_actual: Usuario = user_response["user"]
        #print("El usuario actual es", usuario_actual)
        #if (
            #usuario_actual.rol_usuario == "Administrador"
            #or usuario_actual.rol_usuario == "SuperAdmin"
        #):
          
     except Exception as e:
        print(e)
        return responses.RedirectResponse("login", status_code=status.HTTP_302_FOUND)
