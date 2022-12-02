from api.endpoints.router_login import get_current_user_from_token
from api.endpoints.router_login import login_for_access_token
from db.repository.login import get_user
from db.session import get_db
from fastapi import APIRouter

from fastapi import HTTPException
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.params import Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from webapp.auth.forms import LoginForm
templates = Jinja2Templates(directory="templates")


router = APIRouter()
userGeneral = None


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)

@router.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login/login.html", {"request": request})


@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():        
        try:
            form.__dict__.update(msg="Inicio de Sesion Exitoso :)")
            response = templates.TemplateResponse("login/login.html", form.__dict__)
            user = get_user(nombre_usuario=form.username, db=db)

            if user is None:
                print ("Usuario no encontrado")
                form.__dict__.get("errors").append("Incorrecto Usuario o Contraseña")
                form.__dict__.update(msg="")
                return templates.TemplateResponse("login/login.html", form.__dict__)
            
            form.__dict__.update(msg="Inicio de Sesion Exitoso :)")
        
            if user.rol_usuario == "Carnetizador":
                print("entro carnetizador")
                userGeneral = user           
                response = responses.RedirectResponse(
                    "", status_code=status.HTTP_303_SEE_OTHER)               
            elif (
                user.rol_usuario == "Administrador" or user.rol_usuario == "SuperAdmin"  ):

                response = RedirectResponse(
                    f"/admin", status_code=status.HTTP_302_FOUND
                )
            try:
                login_a=login_for_access_token(response=response, form_data=form, db=db)
            except Exception:
                print ("Usuario o Contraseña from LDAP")
                form.__dict__.get("errors").append("Incorrecto Usuario o Contraseña")
                form.__dict__.update(msg="")
                return templates.TemplateResponse("login/login.html", form.__dict__)

            authorization: str = login_a["access_token"]  # changed to accept access token from httpOnly Cookie
           

            return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrecto Usuario o Contraseña")
            
    else :
        print ("error de autentificacion")
        form.__dict__.update(msg="")
        form.__dict__.get("errors").append("Incorrecto Usuario o Contraseña")
        return templates.TemplateResponse("login/login.html", form.__dict__)