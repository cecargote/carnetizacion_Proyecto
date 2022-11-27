import base64
import imp
import json
from datetime import timedelta
from os import access

import jwt
import requests
from core.config import settings
from db.models.usuario import Usuario
from db.repository.login import get_user
from db.repository.login import update_state_usuario_by_id
from db.repository.usuario import update_state_usuario_by_id_logout
from db.session import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from fastapi import responses
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError
from middleware.utiles import OAuth2PasswordBearerWithCookie
from rsa import verify
from schemas.token import Token
from sqlalchemy.orm import Session

# from core.security import create_access_token

router = APIRouter()


def authenticate_user(nombre_usuario: str, db: Session):
    user = get_user(nombre_usuario=nombre_usuario, db=db)
    #print(user)
    if not user:
        return False
    return user


@router.post("/token", response_model=Token)
def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    #print("login for acess token")
    user = authenticate_user(form_data.username, db)
   # print(user.id)
   # print("el usuario de lfat es:" + user.nombre_usuario)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    # access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    url = settings.API_AUDIENCE + "user/login"
   # print(url)
    responseURL = requests.get(url, auth=(form_data.username, form_data.password))
    #print(responseURL)
    if responseURL.status_code != 502:
        # data = json.dumps(result)
        update_state_usuario_by_id(id=user.id, db=db)
        result = json.loads(str(responseURL.text))
        #print(result)
        result_data = result["data"]
        access_token = result_data["access_token"]
        refresh_token = result_data["refresh_token"]
        #print(access_token)
        response.set_cookie(
            key="access_token", value=f"Bearer {access_token}", httponly=True
        )
        response.set_cookie(
            key="refresh_token", value=f"Bearer {refresh_token}", httponly=True
        )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/login/token")


@router.post("/refresh_token", response_model=Token)
def refreshToken(request: Request):
    #print("entro al refresh")
    refresh_url = settings.API_AUDIENCE + "user/refresh-token"
    #print(refresh_url)
    token = request.cookies.get("access_token")
    #print(token)
    refresh = request.cookies.get("refresh_token")
    #print(refresh)
    scheme1, param1 = get_authorization_scheme_param(token)
    scheme, param = get_authorization_scheme_param(refresh)
   # print(param)
    #print(param1)
    token = param1
    headers = {"Authorization": "Bearer {}".format(token)}
    #print(headers)
    body = {"refresh_token": param}
   # print(body)
    response = requests.post(refresh_url, headers=headers, json=body)
    #print(response)
    if response.status_code != 401:
        result = json.loads(str(response.text))
        #print(result)
        access_token = result["access_token"]
        refresh_token = result["refresh_token"]
       # print(access_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def get_current_user_from_token(
    response: Response,
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    # credentials_exception = HTTPException(
    #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     detail="No se puede validar las credenciales",
    # )
    # try:
   # print("El token es", token)
    user_url = settings.API_AUDIENCE + "tree/OU=Facultad de Ingenieria Informatica"
    headers = {"Authorization": "Bearer {}".format(token)}
   # print(headers)
    response_api = requests.get(user_url, headers=headers)
   # print(response_api)
    if response_api.status_code == 401:
       # print("Esta entrando al 401")
        refresh = refreshToken(request=request)
        access_token = refresh["access_token"]
        refresh_token = refresh["refresh_token"]
        #print(access_token)
        response.set_cookie(
            key="access_token", value=f"Bearer {access_token}", httponly=True
        )
        response.set_cookie(
            key="refresh_token", value=f"Bearer {refresh_token}", httponly=True
        )
        userheader = jwt.decode(access_token, options={"verify_signature": False})
    else:
        userheader = jwt.decode(token, options={"verify_signature": False})
   # print(userheader)
    username = userheader["sub"]
    #print("el usuario a continucion")
   # print(username)
    # response = requests.get(user_url + username, headers=headers)
    # print(response)
    # result = json.loads(str(response.text))
    # result_data = result["data"]

    # except JWTError:
    # print("ESTOY EXCEPT")
    # raise credentials_exception
    #print("ya esta pidiendo el user")
    user = get_user(nombre_usuario=username, db=db)
    #print(user)
    if user is None:
       # print("user 2")
        return responses.RedirectResponse("login", status_code=status.HTTP_302_FOUND)
        # raise credentials_exception
    return {"user": user, "response": response}


@router.get("/cerrarsesion", response_model=Token)
def logout(request: Request, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        #print(token)
        #print(scheme)
        response = responses.RedirectResponse(
            "/login", status_code=status.HTTP_302_FOUND
        )
        user_response = get_current_user_from_token(
            response=response, request=request, token=param, db=db
        )
        usuario_actual: Usuario = user_response["user"]
       # print("El usuario actual es", usuario_actual)
        update_state_usuario_by_id_logout(id=usuario_actual.id, db=db)
        # request.cookies.delete_cookie("access_token")
        # request.cookies.delete_cookie("refresh_token")
        #print("request original")
        response.set_cookie(
            key="access_token", value="", httponly=True
        )
        response.set_cookie(
            key="refresh_token", value="", httponly=True
        )
        # print(request.cookies)
        # request.cookies.clear()
        # print("request limpia")
        # print(request.cookies)
        
        return response
    except Exception as e:
        print(e)
        # return response
