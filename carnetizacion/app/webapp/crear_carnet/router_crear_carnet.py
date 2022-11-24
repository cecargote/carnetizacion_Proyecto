import imp
import json
import os
from io import BytesIO
from typing import List
from typing import Optional
from db.repository.carnet_eliminado import create_new_carnet_eliminado
from db.repository.carnet_activo import create_new_carnet_activo
from schemas.carnet_activo import CarnetActivoCreate
from db.repository.person import create_new_person, retreive_person
from schemas.person import PersonCreate

import barcode
import qrcode
import requests
import webapp.home.router_home
from api.endpoints.router_login import get_current_user_from_token
from barcode.ean import EuropeanArticleNumber13
from barcode.writer import ImageWriter
from click import echo
from core.config import settings
from db.models.carnet_activo import estado
from db.models.usuario import Usuario
from db.repository.tipo_motivos import list_motivos
from db.session import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import FastAPI
from fastapi import Form
from fastapi import HTTPException
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.responses import HTMLResponse
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from pytest import Session
from api.endpoints.router_login import refreshToken
from db.repository.carnet_activo import lista_solicitados, get_carnet_by_person
from db.repository.person import list_persons, update_person_by_ci
from schemas.carnet_eliminado import CarnetEliminadoCreate
from webapp.crear_carnet.form import crearCarnetForm

# import treepoem

# from requests import *

templates = Jinja2Templates(directory="templates")

# from api.endpoints.web.user import router as userRouter

router = APIRouter()

##EndPoints APP
# router.include_router(userRouter, prefix="/user", tags=["Users"])


@router.get("/crear_carnet/{area}/{ci}")
async def crear_carnet(area,ci, request: Request, db: Session = Depends(get_db)):
    print("es crear carnet")
    print(area)
    print(ci)
    try:
        list_tipo_motivos = list_motivos(db=db)
        carnet_user = get_carnet_by_person(person_ci=ci, db=db)
        print(carnet_user)
        person_carnet = retreive_person(ci=ci,db=db)
        print(person_carnet)
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        print(token)
        print(scheme)
        headers = {"Authorization": "Bearer {}".format(param)}
        url = (
                    settings.API_AUDIENCE
                    + "tree/OU="
                    + area
                    + ",DC=cujae,DC=edu,DC=cu?filters=cUJAEPersonDNI:"
                    + ci
                )
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
            user= users[0]
                    # form.__dict__.update(users = users)
                    # context =
                    # print(responseA.context)
                    # responseB = responses.RedirectResponse(
                    #     f"/resultado/{users}", status_code=status.HTTP_302_FOUND
                    # )
            responseB= templates.TemplateResponse("general_pages/crear_carnet.html",{"request": request, "list_tipo_motivos": list_tipo_motivos, 'user':user, 'area':area, 'carnet_user':carnet_user, 'person_carnet':person_carnet})    
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
        else:
            result = json.loads(str(response.text))
                    # print(result["data"])
            users = result["data"]
            user = users[0]
        response = templates.TemplateResponse(
            "general_pages/crear_carnet.html",
            {"request": request, "list_tipo_motivos": list_tipo_motivos, 'user':user, 'area':area, 'carnet_user':carnet_user, 'person_carnet': person_carnet},
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


            

            # GENERAR QR CODE
            # formato de la info
            # N: Nombre y Apellidos, CI: ci, A: area, F:folio
            # qrtxt = (
            #     "aqui va el texto del qr"
            # )  # "N:" + test[posicion]["nombreCrearCarnet"] + " CI:" + test[posicion]["ciCrearrear"] + " A:" + test[posicion]["areaBuscarPersona"] + " F:" + test[posicion]["folioCrearCarnet"]
            # qr = qrcode.QRCode(
            #     version=1,
            #     error_correction=qrcode.constants.ERROR_CORRECT_L,
            #     box_size=10,
            #     border=4,
            # )
            # qr.add_data(qrtxt)
            # qr.make(fit=True)
            # img = qr.make_image(fill_color="black", back_color="white")
            # type(img)
            # img.save("QRCode.png")

            # # GENERAR BARCODE
            # # bc = test[posicion]["ciCrearCarnet"]
            # # image = treepoem.generate_barcode(
            #     # barcode_type="code128",  # One of the BWIPP supported codes.
            #     # barcode_type="qrcode",
            #     # One of the BWIPP supported codes.
            #     # barcode_type="interleaved2of5",  # One of the BWIPP supported codes.
            #     # barcode_type="code128",  # One of the BWIPP supported codes.
            #     #    # barcode_type="isbn",  # One of the BWIPP supported codes.
            #     #    # data="978-3-16-148410-0",
            #     #   barcode_type="code128",  # One of the BWIPP supported codes.
            #     #   barcode_type="micropdf417",  # One of the BWIPP supported codes.
            #     #   barcode_type="ean13",  # One of the BWIPP supported codes.
            #     # data=bc,
            # # )
            # # image.convert("1").save("BCCode.png")

            # # return templates.TemplateResponse(
            # # "general_pages/crear_carnet.html", {"request": request, "list_tipo_motivos": list_tipo_motivos, "test":test, "posicion":posicion, "tamano":tamano, "qrtxt":qrtxt, "img":img}
            # # )
            # # else:
            # # return responses.RedirectResponse("", status_code=status.HTTP_302_FOUND)
            # # endif
            return user_response["response"]
    except Exception as e:
        print(e)
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

@router.post("/crear_carnet/{area}/{ci}")
async def crear_carnet_post(area,ci,request:Request, db: Session = Depends(get_db)):
    print("entro al post")
    form = crearCarnetForm(request)
    await form.load_data()
    if await form.is_valid():
        try: 
            print(ci)
            print("entro al if del form")
        # print(form.ci.value())
            print(form.folio)
            print(form.folio_desactivo)
            ci=ci
            person=retreive_person(ci=ci,db=db)
            carnet_anterior=get_carnet_by_person(person_ci=ci,db=db)
            if carnet_anterior is not None:
                form.folio_desactivo=carnet_anterior.folio
                form.area_anterior = person.area
                form.rol_anterior= person.rol
                carnet_eliminado = CarnetEliminadoCreate(**form.__dict__)
                carnet_eliminado = create_new_carnet_eliminado(carnet_eliminado=carnet_eliminado, db=db, person_ci=ci)

            print("imprimiendo persona")
            print(person)
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(token)
            print(token)
            print(scheme)
            headers = {"Authorization": "Bearer {}".format(param)}
            url = (settings.API_AUDIENCE
                    + "tree/OU="
                    + area
                    + ",DC=cujae,DC=edu,DC=cu?filters=cUJAEPersonDNI:"
                    + ci
                  )
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
               user= users[0]
               carnets = lista_solicitados(db=db)
               persons = list_persons(db=db)
               motivos = list_motivos(db=db)
               responseB= templates.TemplateResponse("general_pages/carnets/carnets_pendientes.html",{"request": request, "carnets": carnets, "persons":persons, "motivos":motivos})    
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
            else:
                result = json.loads(str(response.text))
                    # print(result["data"])
                users = result["data"]
                user = users[0]
                form.ci = ci
                form.annoEstudiantePersona= user['cUJAEStudentYear']
                form.area= area
                form.nombre = user['name']
                person_a = PersonCreate(**form.__dict__)
            if(person == None):
                person_a = create_new_person(person=person_a, db=db)
                print(form.tipoMotivo)
            else:
                print("actualizar person")
                person_a = update_person_by_ci(ci=ci, person=person_a,db=db)
                print("se detuvo aqui en person")
            # nombre_motivo = form.tipoMotivo
            # tipo_motivo= retreive_motivo_by_name(nombre_motivo=nombre_motivo, db=db)
            # print(tipo_motivo)
            carnet_activo = CarnetActivoCreate(**form.__dict__)
            print("se deturvo en create")
            carnet_activo = create_new_carnet_activo(carnet_activo=carnet_activo, db=db, person_ci=ci,tipo_motivo_id=form.tipoMotivo)
            return responses.RedirectResponse("/carnets/solicitados", status_code=status.HTTP_302_FOUND)
        except Exception as e:
            print(e)
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
