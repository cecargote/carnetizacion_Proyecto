import base64
import json
from multiprocessing.sharedctypes import Value
from os import access

import requests
from api.endpoints.router_login import get_current_user_from_token
from api.endpoints.router_login import login_for_access
from core.config import settings
from db.models.usuario import Usuario
from db.repository.login import get_user
from db.session import get_db
from fastapi import APIRouter
from fastapi import Form
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
from fastapi.security.utils import get_authorization_scheme_param

router = APIRouter()
userGeneral = None

@router.get("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("user")
    print (token)
    response = templates.TemplateResponse("login/login.html", {"request": request})
    
    if userGeneral is None:
        print("is none")
        return response
    else:
        try:
           
           user = userGeneral
           usuario_actual: Usuario = user
           print("El usuario actual es", usuario_actual)
           if (usuario_actual.rol_usuario == "Administrador"
            or usuario_actual.rol_usuario == "SuperAdmin"):
              return responses.RedirectResponse("admin", status_code=status.HTTP_302_FOUND)
           else:
              return responses.RedirectResponse("", status_code=status.HTTP_302_FOUND)
        except Exception as e:
            print(e)
    return response


@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    
    form = LoginForm(request)
    await form.load_data()
    
    if await form.is_valid():
        
        try:
            user = get_user(nombre_usuario=form.username, db=db)
            if user is None:
                print ("Usuario no encontrado")
                form.__dict__.get("errors").append("Incorrecto Usuario o Contraseña")
                form.__dict__.update(msg="")
                return templates.TemplateResponse("login/login.html", form.__dict__)
            
            response = templates.TemplateResponse("login/login.html", form.__dict__)

            login_for_access(response=response, form_data=form, db=db)
            
            form.__dict__.update(msg="Inicio de Sesion Exitoso :)")
        
            if user.rol_usuario == "Carnetizador":
                print("entro carnetizador")
                userGeneral = user
                response = responses.RedirectResponse(
                    "", status_code=status.HTTP_303_SEE_OTHER
                )
            elif (
                user.rol_usuario == "Administrador" or user.rol_usuario == "SuperAdmin"
            ):
                print("entro admin")
                userGeneral = user
                response = RedirectResponse(
                    f"/admin", status_code=status.HTTP_302_FOUND
                )
          
            return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrecto Usuario o Contraseña")
            
    else :
        print ("error de autentificacion")
        form.__dict__.update(msg="")
        form.__dict__.get("errors").append("Incorrecto Usuario o Contraseña")
        return templates.TemplateResponse("login/login.html", form.__dict__)