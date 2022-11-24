import json
import requests
from api.endpoints.router_login import get_current_user_from_token
from api.endpoints.router_login import refreshToken
from core.config import settings
from db.models.usuario import Usuario
from db.session import get_db
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.params import Depends
from fastapi.responses import HTMLResponse
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from webapp.home.form import BuscarPersonaForm

# from requests import *


templates = Jinja2Templates(directory="templates")

# from api.endpoints.web.user import router as userRouter


router = APIRouter()

##EndPoints APP
# router.include_router(userRouter, prefix="/user", tags=["Users"])


@router.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        print(token)
        print(scheme)
        response = templates.TemplateResponse(
            "general_pages/homepage.html", {"request": request}
        )
        user_response = get_current_user_from_token(
            response=response, request=request, token=param, db=db
        )
        usuario_actual: Usuario = user_response["user"]
        print("El usuario actual es", usuario_actual)
        if (
            usuario_actual.rol_usuario == "Carnetizador"
            or usuario_actual.rol_usuario == "SuperAdmin"
        ):
            return user_response["response"]

    except Exception as e:
        print(e)
        print("entro error")
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)


@router.post("/")
async def home(request: Request):
    form = BuscarPersonaForm(request)
    await form.load_data()
    # print(request.json())
    if form.is_valid():
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(token)
            headers = {"Authorization": "Bearer {}".format(param)}
            print("Entoooo")
            area=form.areaBuscarPersona
            if form.ciBuscarPersona:
                print("ciii")
                url = (
                    settings.API_AUDIENCE
                    + "tree/OU="
                    + area
                    + ",DC=cujae,DC=edu,DC=cu?filters=cUJAEPersonDNI:"
                    + form.ciBuscarPersona
                )
            if not form.ciBuscarPersona and form.tipoBuscarPersona != "Seleccione":
                print("tipo")
                print(form.Check1)
                checkTrue = form.Check1 or form.Check2 or form.Check3 or form.Check4
                print(checkTrue)
                if form.tipoBuscarPersona == "Student" and checkTrue:
                    check401Check1 = False
                    check401Check2 = False
                    check401Check3 = False
                    check401Check4 = False
                    print("Student")
                    if form.Check1:
                        urlCheck1 = (
                            settings.API_AUDIENCE
                            + "tree/OU="
                            + area
                            + ",DC=cujae,DC=edu,DC=cu?filters=cUJAEPersonType:"
                            + form.tipoBuscarPersona
                            + ",cUJAEStudentYear:"
                            + form.Check1
                        )
                        responseCheck1 = requests.get(urlCheck1, headers=headers)
                        if responseCheck1.status_code == 401:
                            check401Check1 = True
                            tokenR = refreshToken(request=request)
                            print("lo q devuelve el refresh", tokenR)
                            tokenRAcceso = tokenR["access_token"]
                            tokenRRefresh = tokenR["refresh_token"]
                            print(tokenRAcceso)
                            # token = request.cookies.get("access_token")
                            # scheme, param = get_authorization_scheme_param(token)
                            headers = {
                                "Authorization": "Bearer {}".format(tokenRAcceso)
                            }
                            print(headers)
                            responseCheck1 = requests.get(urlCheck1, headers=headers)
                            print(responseCheck1)
                            resultCheck1 = json.loads(str(responseCheck1.text))
                            users = resultCheck1["data"]

                            # form.__dict__.update(users = users)
                            # context =
                            # print(responseA.context)
                            if not form.Check2 and not form.Check3 and not form.Check4:
                                # responseBCheck1 = responses.RedirectResponse(
                                #     f"/resultado/{users}",
                                #     status_code=status.HTTP_302_FOUND,
                                # )
                                responseBCheck1= templates.TemplateResponse("general_pages/homepage.html", {'request':request, 'users':users, 'area':area})
                                responseBCheck1.set_cookie(
                                    key="access_token",
                                    value=f"Bearer {tokenRAcceso}",
                                    httponly=True,
                                )
                                responseBCheck1.set_cookie(
                                    key="refresh_token",
                                    value=f"Bearer {tokenRRefresh}",
                                    httponly=True,
                                )

                                return responseBCheck1

                        else:
                            resultCheck1 = json.loads(str(responseCheck1.text))
                            print(resultCheck1)
                            if not resultCheck1:
                                raise HTTPException(
                                    status_code=404, detail="User not found"
                                )
                            users = resultCheck1["data"]
                    if form.Check2:
                        urlCheck2 = (
                            settings.API_AUDIENCE
                            + "tree/OU="
                            + area
                            + ",DC=cujae,DC=edu,DC=cu?filters=cUJAEPersonType:"
                            + form.tipoBuscarPersona
                            + ",cUJAEStudentYear:"
                            + form.Check2
                        )
                        if check401Check1:
                            headers = {
                                "Authorization": "Bearer {}".format(tokenRAcceso)
                            }
                        responseCheck2 = requests.get(urlCheck2, headers=headers)
                        if responseCheck2.status_code == 401:
                            check401Check2 = True
                            tokenR = refreshToken(request=request)
                            print("lo q devuelve el refresh", tokenR)
                            tokenRAcceso = tokenR["access_token"]
                            tokenRRefresh = tokenR["refresh_token"]
                            print(tokenRAcceso)
                            # token = request.cookies.get("access_token")
                            # scheme, param = get_authorization_scheme_param(token)
                            headers = {
                                "Authorization": "Bearer {}".format(tokenRAcceso)
                            }
                            print(headers)
                            responseCheck2 = requests.get(urlCheck2, headers=headers)
                            resultCheck2 = json.loads(str(responseCheck2.text))
                            if form.Check1:
                                users.extend(resultCheck2["data"])
                            else:
                                users = resultCheck2["data"]
                            # form.__dict__.update(users = users)
                            # context =
                            # print(responseA.context)
                            if not form.Check3 and not form.Check4:
                                # responseBCheck2 = responses.RedirectResponse(
                                #     f"/resultado/{users}",
                                #     status_code=status.HTTP_302_FOUND,
                                # )
                                responseBCheck2= templates.TemplateResponse("general_pages/homepage.html", {'request':request, 'users':users, 'area':area})
                                responseBCheck2.set_cookie(
                                    key="access_token",
                                    value=f"Bearer {tokenRAcceso}",
                                    httponly=True,
                                )
                                responseBCheck2.set_cookie(
                                    key="refresh_token",
                                    value=f"Bearer {tokenRRefresh}",
                                    httponly=True,
                                )

                                return responseBCheck1

                        if responseCheck2.status_code != 502:
                            resultCheck2 = json.loads(str(responseCheck2.text))
                            print(resultCheck2)
                            if not resultCheck2:
                                raise HTTPException(
                                    status_code=404, detail="User not found"
                                )
                            if form.Check1:
                                # print(users)
                                # print(resultCheck1)
                                users.extend(resultCheck2["data"])
                            else:
                                users = resultCheck2["data"]
                        print(responseCheck2)
                    if form.Check3:
                        urlCheck3 = (
                            settings.API_AUDIENCE
                            + "tree/OU="
                            + area
                            + ",DC=cujae,DC=edu,DC=cu?filters=cUJAEPersonType:"
                            + form.tipoBuscarPersona
                            + ",cUJAEStudentYear:"
                            + form.Check3
                        )
                        if check401Check1 or check401Check2:
                            headers = {
                                "Authorization": "Bearer {}".format(tokenRAcceso)
                            }
                        responseCheck3 = requests.get(urlCheck3, headers=headers)
                        if responseCheck3.status_code == 401:
                            check401Check3 = True
                            tokenR = refreshToken(request=request)
                            print("lo q devuelve el refresh", tokenR)
                            tokenRAcceso = tokenR["access_token"]
                            tokenRRefresh = tokenR["refresh_token"]
                            print(tokenRAcceso)
                            # token = request.cookies.get("access_token")
                            # scheme, param = get_authorization_scheme_param(token)
                            headers = {
                                "Authorization": "Bearer {}".format(tokenRAcceso)
                            }
                            print(headers)
                            responseCheck3 = requests.get(urlCheck3, headers=headers)
                            resultCheck3 = json.loads(str(responseCheck3.text))
                            if form.Check1 or form.Check2:
                                users.extend(resultCheck3["data"])
                            else:
                                users = resultCheck3["data"]
                            # form.__dict__.update(users = users)
                            # context =
                            # print(responseA.context)
                            if not form.Check4:
                                # responseBCheck3 = responses.RedirectResponse(
                                #     f"/resultado/{users}",
                                #     status_code=status.HTTP_302_FOUND,
                                # )
                                responseBCheck3= templates.TemplateResponse("general_pages/homepage.html", {'request':request, 'users':users, 'area':area})
                                responseBCheck3.set_cookie(
                                    key="access_token",
                                    value=f"Bearer {tokenRAcceso}",
                                    httponly=True,
                                )
                                responseBCheck3.set_cookie(
                                    key="refresh_token",
                                    value=f"Bearer {tokenRRefresh}",
                                    httponly=True,
                                )

                                return responseBCheck3
                        if responseCheck3.status_code != 502:
                            resultCheck3 = json.loads(str(responseCheck3.text))
                            print(resultCheck3)
                            if not resultCheck3:
                                raise HTTPException(
                                    status_code=404, detail="User not found"
                                )
                            if form.Check1 or form.Check2:
                                users.extend(resultCheck3["data"])
                            else:
                                users = resultCheck3["data"]
                        print(responseCheck3)
                    if form.Check4:
                        urlCheck4 = (
                            settings.API_AUDIENCE
                            + "tree/OU="
                            + area
                            + ",DC=cujae,DC=edu,DC=cu?filters=cUJAEPersonType:"
                            + form.tipoBuscarPersona
                            + ",cUJAEStudentYear:"
                            + form.Check4
                        )
                        if check401Check1 or check401Check2 or check401Check3:
                            headers = {
                                "Authorization": "Bearer {}".format(tokenRAcceso)
                            }
                        responseCheck4 = requests.get(urlCheck4, headers=headers)
                        if responseCheck4.status_code == 401:
                            check401Check4 = True
                            tokenR = refreshToken(request=request)
                            print("lo q devuelve el refresh", tokenR)
                            tokenRAcceso = tokenR["access_token"]
                            tokenRRefresh = tokenR["refresh_token"]
                            print(tokenRAcceso)
                            # token = request.cookies.get("access_token")
                            # scheme, param = get_authorization_scheme_param(token)
                            headers = {
                                "Authorization": "Bearer {}".format(tokenRAcceso)
                            }
                            print(headers)
                            responseCheck4 = requests.get(urlCheck4, headers=headers)
                            resultCheck4 = json.loads(str(responseCheck4.text))
                            if form.Check1 or form.Check2 or form.Check3:
                                users.extend(resultCheck4["data"])
                            else:
                                users = resultCheck4["data"]
                            # form.__dict__.update(users = users)
                            # context =
                            # print(responseA.context)
                            # responseBCheck4 = responses.RedirectResponse(
                            #     f"/resultado/{users}", status_code=status.HTTP_302_FOUND
                            # )
                            responseBCheck4= templates.TemplateResponse("general_pages/homepage.html", {'request':request, 'users':users, 'area':area})
                            responseBCheck4.set_cookie(
                                key="access_token",
                                value=f"Bearer {tokenRAcceso}",
                                httponly=True,
                            )
                            responseBCheck4.set_cookie(
                                key="refresh_token",
                                value=f"Bearer {tokenRRefresh}",
                                httponly=True,
                            )
                            return responseBCheck4
                        if responseCheck4.status_code != 502:
                            resultCheck4 = json.loads(str(responseCheck4.text))
                            print(resultCheck4)
                            if not resultCheck4:
                                raise HTTPException(
                                    status_code=404, detail="User not found"
                                )
                            if form.Check1 or form.Check2 or form.Check3:
                                users.extend(resultCheck4["data"])
                            else:
                                users = resultCheck4["data"]
                        print(responseCheck4)
                else:
                    url = (
                        settings.API_AUDIENCE
                        + "tree/OU="
                        + area
                        + ",DC=cujae,DC=edu,DC=cu?filters=cUJAEPersonType:"
                        + form.tipoBuscarPersona
                    )
            if form.tipoBuscarPersona == "Seleccione" and not form.ciBuscarPersona:
                print("Area")
                url = settings.API_AUDIENCE + "tree/OU=" + area
            print(form.Check1)
            if (
                not form.Check1
                and not form.Check2
                and not form.Check3
                and not form.Check4
            ):
                print(url)
                response = requests.get(url, headers=headers)
                print(response)
                if response.status_code == 401:
                    print("entro al if 401")
                    tokenR = refreshToken(request=request)
                    print("lo q devuelve el refresh", tokenR)
                    tokenRAcceso = tokenR["access_token"]
                    tokenRRefresh = tokenR["refresh_token"]
                    print(tokenRAcceso)
                    # token = request.cookies.get("access_token")
                    # scheme, param = get_authorization_scheme_param(token)
                    headers = {"Authorization": "Bearer {}".format(tokenRAcceso)}
                    print(headers)
                    response = requests.get(url, headers=headers)
                    print(response)
                    result = json.loads(str(response.text))
                    users = result["data"]
                    # form.__dict__.update(users = users)
                    # context =
                    # print(responseA.context)
                    # responseB = responses.RedirectResponse(
                    #     f"/resultado/{users}", status_code=status.HTTP_302_FOUND
                    # )
                    responseB= templates.TemplateResponse("general_pages/homepage.html", {'request':request, 'users':users, 'area':area})
                    responseB.set_cookie(
                        key="access_token",
                        value=f"Bearer {tokenRAcceso}",
                        httponly=True,
                    )
                    responseB.set_cookie(
                        key="refresh_token",
                        value=f"Bearer {tokenRRefresh}",
                        httponly=True,
                    )

                    return responseB
                else:
                    # data = json.dumps(result)
                    result = json.loads(str(response.text))
                    # print(result["data"])
                    users = result["data"]
                    print(users[0]["cUJAEPersonType"])
                    # for user in users:
                    #  print(user)
                    #  print(user["name"])

                    # print(response.text)
                    # print(form.Check1)

            return templates.TemplateResponse("general_pages/homepage.html", {'request':request, 'users':users, 'area':area})
        except HTTPException:
            return templates.TemplateResponse(
                "general_pages/homepage.html", form.__dict__
            )
    # await form_lista.is_valid()
    # if form_lista.is_valid():
    # print("entro")
    # return templates.TemplateResponse(
    #     "general_pages/homepage.html", {"request": request}
    # )
