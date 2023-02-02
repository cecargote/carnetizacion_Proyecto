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
def buscar_Tipo_Estudiante_carnet(ci: str):
    reqUrl = "https://sigenu.cujae.edu.cu/sigenu-rest/student/fileStudent/getStudentAllData/"+ci

    headersList = {
    "Accept": "*/*",
    "User-Agent": "Thunder Client (https://www.thunderclient.com)",
    "Authorization": "Basic ZGlzZXJ0aWMud3Muc2lnZW51OmRpc2VydGljLndzKjIwMTUq",
    "Content-Type": "application/json" 
    }

    payload = json.dumps("")

    response = requests.request("GET", reqUrl, data=payload,  headers=headersList)



    result = json.loads(response.text)
    try:
        tipo =result[0]["docentData"]['studentType'] 

        print("tipo de estudiante",tipo)
    except Exception as e:
        print("no se encontro el estudiante")
        print(e)

    return tipo
def buscar_consejo_universitario(ci:str, name : str, last_name):
    archivo = 'C:/Users/Carlos Laptop/Downloads/datos2.xlsx'
    hoja = pandas.read_excel(archivo,engine="openpyxl")
    list = hoja
    last_name_temp=""
    name_temp= ""
    ci_temp = ""
    cargo_temp=""
    i=0
    size = len(list)
    while i< size:
        last_name_temp= list.iloc[i,3]
        name_temp= list.iloc[i,2]
        ci_temp = list.iloc[i,1]
        ci_temp = ""+str(ci_temp)

        if(name_temp==name and last_name_temp ==last_name or ci_temp==ci ):
            cargo_temp= list.iloc[i,6]
            print("se encontro un cargo para esta persona")
            print(i, " ",ci_temp," " ,name_temp," ",last_name_temp," cargo: ",cargo_temp)
        i+=1

    return cargo_temp
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
def buscarAreas_por_name(text: str, areaID):
    result = json.loads(str(text))
    area = ""
    for iter in result:
        if iter['name'] == areaID:       
            area = iter['distinguishedName']
            break

    return area
def buscarAreas():
    import requests

    reqUrl = "https://sigenu.cujae.edu.cu/sigenu-ldap-cujae/ldap/areas"

    headersList = {
    "Accept": "*/*",
    "User-Agent": "Thunder Client (https://www.thunderclient.com)",
    "Authorization": "Basic ZGlzZXJ0aWMubGRhcDpkaXNlcnRpYyoyMDIyKmxkYXA=" 
    }

    payload = ""

    response = requests.request("GET", reqUrl, data=payload,  headers=headersList)
    
    return response.text
@router.get("/crear_carnet/{area}/{ci}")
async def crear_carnet(area,ci, request: Request, db: Session = Depends(get_db)):
    print("es crear carnet")
    
    print(ci)
    
    print(area)
    areatemp = buscarAreas_por_name(buscarAreas(),area)

    try:
        list_tipo_motivos = list_motivos(db=db)
        carnet_user = get_carnet_by_person(ci, db)
        print("Carnet Anterior ",carnet_user)
        person_carnet = retreive_person(ci,db)
        print("Persona Anterior",person_carnet)
        print(person_carnet)
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
       

        usuario= buscarTrabajdor_and_Estudiante(ci,areatemp)
       
        if usuario != None :
            rol =""         
            user= usuario[0]
            
            if(user["personType"] == "Student"):
                rol= buscar_Tipo_Estudiante_carnet(ci)
                print("rol ",rol)
            elif user["personType"] == "Worker":
                if user["personTeacher"] == "TRUE":
                    rol= "Docente"         
                elif user["personTeacher"] == "FALSE":
                    rol= "No Docente"


            name_temp= user["name"]
            last_name = user["surname"] + " "+ user["lastname"]
            found = buscar_consejo_universitario(ci,name_temp,last_name)
            
            if found !="":
                rol = found


            print("rol ", rol)
            responseB= templates.TemplateResponse("general_pages/crear_carnet.html",{"request": request,
             "list_tipo_motivos": list_tipo_motivos,
              'user':user,
               'area':area,
               'carnet_user':carnet_user,
                'person_carnet':person_carnet,
                'rol': rol})    
             
                     
            current_user: Usuario = get_current_user_from_token(param, db)
           
            if ( current_user.rol_usuario == "Carnetizador" or current_user.rol_usuario == "SuperAdmin"):

                return responseB
    except Exception as e:
        print(e)
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

@router.post("/crear_carnet/{area}/{ci}")
async def crear_carnet_post(area,ci,request:Request, db: Session = Depends(get_db)):
    print("Comenzamos a crear un carnet")
    areatemp=  buscarAreas_por_name(buscarAreas(),area)
    form = crearCarnetForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            usuario= buscarTrabajdor_and_Estudiante(ci,areatemp)
            user= usuario[0]   
            print("se encontro el usuario")
            person=retreive_person(ci,db)
            carnet_anterior=get_carnet_by_person(ci,db)

            form.ci= user['identification']
            form.area= user['area']
            
           
            if(user["personType"] == "Student"):
                form.rol = buscar_Tipo_Estudiante_carnet(form.ci)
                form.annoEstudiantePersona= user['studentYear']
                form.tipoPersona = "Estudiante"
            else:
                form.tipoPersona = "Trabajador"
                if user["personTeacher"] == "TRUE":
                    form.rol = "Docente"         
                elif user["personTeacher"] == "FALSE":
                    form.rol = "No Docente"
            
            name_temp= user["name"]
            last_name = user["surname"] + " "+ user["lastname"]

            found = buscar_consejo_universitario(ci,name_temp,last_name)

            if found !="":
                print(found)
                form.rol = found 
            
            form.nombre= user['name']+" "+user['lastname']+" "+user['surname']
            
            #=====================================================

            form.folio = None # se desactivo el folio, es null
            print("")
            print ("folio desactivado del formulario")
            print("")

            #=====================================================
            
            print("===========Datos del usuario======================")
            print("ci: ",form.ci)
            #print("folio ",form.folio)
            if carnet_anterior != None:
                print("folio desactivo ",carnet_anterior.folio)
            else:
                print("folio desactivo: No existe folio anterior")
            print("area ",form.area)
            if person != None:
                print("area anterior ",person.area)
            else:
                print("area anterior: "+"No existe Area anteriror")
            print("comprobante motivo ",form.comprobante_motivo)
            print("estado ",form.estado)
            if(user["personType"] == "Student"):
                print("anno estudiante ",form.annoEstudiantePersona)
            print("nombre ",form.nombre)
            print("rol ",form.rol)
            print("tipo de persona ",form.tipoPersona)
            if person != None:
                print("rol anterior",person.rol)  
            else:
                print("rol anterior","No existe Rol anterior")    
            print("motivo",form.tipoMotivo)
            print("comprobante motivo: ",form.comprobante_motivo)

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
                form.folio_desactivo = carnet_anterior.folio
                form.area_anterior = person.area
                form.rol_anterior = person.rol
                person_a = PersonCreate(**form.__dict__)

                person_a = update_person_by_ci(ci, person_a,db)
                print("Se actualizo la persona")
                
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
