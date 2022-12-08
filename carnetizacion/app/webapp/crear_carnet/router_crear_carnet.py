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

def buscarTrabajdor_and_Estudiante(ci: str,area: str):

    reqUrl = "https://sigenu.cujae.edu.cu/sigenu-ldap-cujae/ldap/search-all"

    headersList = {
    "Accept": "*/*",
    "User-Agent": "Thunder Client (https://www.thunderclient.com)",
    "Authorization": "Basic ZGlzZXJ0aWMubGRhcDpkaXNlcnRpYyoyMDIyKmxkYXA=",
    "Content-Type": "application/json" 
    }
    payload = json.dumps({
    "identification": ci,
    "name": "",
    "lastname": "",
    "surname": "",
    "email": "",
    "area": area
    })

    response = requests.request("POST", reqUrl, data=payload,  headers=headersList)
    
    result = json.loads(str(response.text))
    if(bool(result)):
        return result
    else:
        print("no se encontro el Usuario en esa area")
        return None


@router.get("/crear_carnet/{area}/{ci}")
async def crear_carnet(area,ci, request: Request, db: Session = Depends(get_db)):
    print("es crear carnet")
    print(area)
    print(ci)
    try:
        list_tipo_motivos = list_motivos(db=db)
        carnet_user = get_carnet_by_person(ci, db)
        print(carnet_user)
        person_carnet = retreive_person(ci,db)
        print(person_carnet)
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
       

        usuario= buscarTrabajdor_and_Estudiante(ci,area)
       
        if usuario != None :         
            user= usuario[0]

            responseB= templates.TemplateResponse("general_pages/crear_carnet.html",{"request": request, "list_tipo_motivos": list_tipo_motivos, 'user':user, 'area':area, 'carnet_user':carnet_user, 'person_carnet':person_carnet})    
                     
            current_user: Usuario = get_current_user_from_token(param, db)
           
            if ( current_user.rol_usuario == "Carnetizador" or current_user.rol_usuario == "SuperAdmin"):


            

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
                return responseB
    except Exception as e:
        print(e)
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

@router.post("/crear_carnet/{area}/{ci}")
async def crear_carnet_post(area,ci,request:Request, db: Session = Depends(get_db)):
    print("Comenzamos a crear un carnet")
    form = crearCarnetForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            usuario= buscarTrabajdor_and_Estudiante(ci,area)
            user= usuario[0]   
            print("se encontro el usuario")
            person=retreive_person(ci,db)
            carnet_anterior=get_carnet_by_person(ci,db)

            form.ci= user['identification']
            form.area= user['area']
            
           
            if(user["personType"] == "Student"):
                form.annoEstudiantePersona= user['studentYear']
                form.tipoPersona = "Estudiante"
            else:
                form.tipoPersona = "Trabajador"
            
            form.nombre= user['name']+" "+user['lastname']+" "+user['surname']
            
            
            print("===========Datos del usuario======================")
            print("ci: ",form.ci)
            print("folio ",form.folio)
            print("folio desactivo ",form.folio_desactivo)
            print("area ",form.area)
            print("area anterior ",form.area_anterior)
            print("comprobante motivo ",form.comprobante_motivo)
            print("estado ",form.estado)
            print("anno estudiante ",form.annoEstudiantePersona)
            print("nombre ",form.nombre)
            print("rol ",form.rol)
            print("tipo de persona ",form.tipoPersona)
            print("rol anterior",form.rol_anterior)
            print("rol anterior",form.tipoMotivo)

            print("============== Estos son los datos que se recogieron==========")

            if person is None:
                print("no existe la persona en el registro")
                print("se registrara") 
                
                person_a = PersonCreate(**form.__dict__)
                person_a = create_new_person(person_a, db)
                print("Impriemiendo la persona Creada------")
                print("persona: ",person_a.nombre)
                print("persona: ", person_a.area)
                print("persona: ", person_a.ci)
                print("persona: ", person_a.is_activa)
                print("persona: ", person_a.rol)

            else:
                person_a = update_person_by_ci(ci, person,db)

            if carnet_anterior is not None: # si tiene carnet anterior
                print("existia un carnet anterior y se actualizara")
                form.folio_desactivo= carnet_anterior.folio 
                form.area_anterior= person.area
                form.rol_anterior= person.rol
                
                carnet_eliminado = CarnetEliminadoCreate(**form.__dict__)
                carnet_eliminado = create_new_carnet_eliminado(carnet_eliminado=carnet_eliminado, db=db, person_ci=ci)
                print("se actualizo el nuevo carnet y se guardo el viejo")
            else:
                print("El usuario no tenia carnet activo")
                carnet_activo = CarnetActivoCreate(**form.__dict__)
                carnet_activo = create_new_carnet_activo(carnet_activo=carnet_activo, db=db, person_ci=ci,tipo_motivo_id=form.tipoMotivo)
            
       
                  
                    
            
            print("Carne Realizado correctamente")   
            #responseB= templates.TemplateResponse("general_pages/carnets/carnets_pendientes.html",{"request": request, "carnets": carnets, "persons":persons, "motivos":motivos})    
                
                        

                
            
            return responses.RedirectResponse("/carnets/solicitados", status_code=status.HTTP_302_FOUND)
        
        except Exception as e:
            print(e)
            print("hubo un error a la hora de crear u carnet")
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
