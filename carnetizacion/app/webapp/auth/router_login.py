import base64
import json
from multiprocessing.sharedctypes import Value
from os import access

import requests
from api.endpoints.router_login import get_current_user_from_token
from api.endpoints.router_login import login_for_access_token
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


# from api.endpoints.web.user import router as userRouter


router = APIRouter()


@router.get("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    response = templates.TemplateResponse("login/login.html", {"request": request})
    print(token)
    if token is None:
        return response
    else:
        try:
        
           scheme, param = get_authorization_scheme_param(token)
           print(token)
           print(scheme)
           user_response = get_current_user_from_token(response=response, request=request, token=param, db=db)
           usuario_actual: Usuario = user_response["user"]
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
    # print (usuario)
    # return templates.TemplateResponse("login/login.html")
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            form.__dict__.update(msg="Inicio de Sesion Exitoso :)")
            response = templates.TemplateResponse("login/login.html", form.__dict__)
            user = get_user(nombre_usuario=form.username, db=db)
            if user.rol_usuario == "Carnetizador":
                print("entro carnetizador")
                response = responses.RedirectResponse(
                    "", status_code=status.HTTP_303_SEE_OTHER
                )
            elif (
                user.rol_usuario == "Administrador" or user.rol_usuario == "SuperAdmin"
            ):
                print("entro admin")
                response = RedirectResponse(
                    f"/admin", status_code=status.HTTP_302_FOUND
                )
            login_a=login_for_access_token(response=response, form_data=form, db=db)
            authorization: str = login_a["access_token"]  # changed to accept access token from httpOnly Cookie
            print("access_token is", authorization)
            user = get_user(nombre_usuario=form.username, db=db)
            # if user.rol_usuario == "Carnetizador":
            #     print("entro carnetizador")
            #     return responses.RedirectResponse("", status_code=status.HTTP_303_SEE_OTHER)
            # elif (
            #     user.rol_usuario == "Administrador" or user.rol_usuario == "SuperAdmin"
            # ):
            #     print("entro admin")
            #     return RedirectResponse(
            #         f"/admin", status_code=302
            #     )

            print("El usuer es" + user.rol_usuario)
            # authorization = base64.b64encode(bytes(form.username +":"+ form.password), "uft-8")
            # print(authorization)
            # has_access(authorization)
            return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrecto Usuario o Contraseña")
            return templates.TemplateResponse("login/login.html", form.__dict__)
