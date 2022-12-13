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
        
        lista_areas, count= listaAreas(buscarAreas())
        total_areas= count

        response = templates.TemplateResponse(
            "general_pages/homepage.html", {"request": request,  "total_areas": total_areas, "lista_areas":lista_areas})
        
        try:
            current_user: Usuario = get_current_user_from_token(param, db)
        except HTTPException:
            print("Error al cargar el usuario, sera enviado al LOGIN")
            return  responses.RedirectResponse("login", status_code=status.HTTP_401_UNAUTHORIZED)
        if (
            current_user.rol_usuario == "Carnetizador"
            or current_user.rol_usuario == "SuperAdmin"
        ):
            return response

    except Exception as e:
        print(e)
        print("Error Home")
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

def listaAreas(text : str):
    result = json.loads(str(text))          
    lista=""
    count =0
    for iter in result:
        iter['name']
        count= count +1
        lista= lista +iter['name']+ ","
    
    return lista, count

def buscarAreas_por_name(text: str, areaID):
    result = json.loads(str(text))
    area = ""
    for iter in result:
        if iter['name'] == areaID:       
            area = iter['distinguishedName']
            break

    return area
def buscar_personas_por_areas(area: str):
    
        reqUrl = "https://sigenu.cujae.edu.cu/sigenu-ldap-cujae/ldap/persons?area=OU=DG de ICI,OU=Area Central,DC=cujae,DC=edu,DC=cu"

        headersList = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)",
            "Authorization": "Basic ZGlzZXJ0aWMubGRhcDpkaXNlcnRpYyoyMDIyKmxkYXA=",
            "Content-Type": "application/json" 
            }

        payload = json.dumps({
        "area":area
        })

        response = requests.request("GET", reqUrl, data=payload,  headers=headersList)
        users =  json.loads(str(response.text))
        return users
        
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
    
    
@router.post("/")
async def home(request: Request):
    form = BuscarPersonaForm(request)
    lista_areas, count= listaAreas(buscarAreas())
    total_areas= count
    
    await form.load_data()
    value = form.is_valid()
    if value:
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(token)
            
            area = buscarAreas_por_name(buscarAreas(),form.areaBuscarPersona)
            print("area",area)
            print ("carnet")
            print(form.ciBuscarPersona)
            ci = form.ciBuscarPersona
            if  area != "":
                print("Area Encontrada")
                usuario  = buscarTrabajdor_and_Estudiante(ci,area)               
                if usuario is not None:
                    
                    checkTrue = form.Check1 or form.Check2 or form.Check3 or form.Check4
                    
                    if form.tipoBuscarPersona == "Student" and checkTrue:
                        if form.Check1:
                            print("estudiante 1 er año")
                            users= [usuario[0]]
                            responseEstudiante= templates.TemplateResponse("general_pages/homepage.html",
                            {'request':request, 'users':users, 'area': form.areaBuscarPersona, "lista_areas" :lista_areas,
                            "total_areas": total_areas
                            })
                            return responseEstudiante
                        if form.Check2:
                            print("estudiante 2 do año")
                            users= [usuario[0]]
                            responseEstudiante= templates.TemplateResponse("general_pages/homepage.html",
                            {'request':request, 'users':users, 'area':form.areaBuscarPersona, "lista_areas" :lista_areas,
                            "total_areas": total_areas
                            })
                            return responseEstudiante

                        if form.Check3:
                            print("estudiante 3 er año")
                            users= [usuario[0]]
                            responseEstudiante= templates.TemplateResponse("general_pages/homepage.html",
                            {'request':request, 'users':users, 'area':form.areaBuscarPersona, "lista_areas" :lista_areas,
                            "total_areas": total_areas
                            })
                            return responseEstudiante
                        if form.Check4:
                            print("estudiante 4 to año")
                            users= [usuario[0]]
                            responseEstudiante= templates.TemplateResponse("general_pages/homepage.html",
                            {'request':request, 'users':users, 'area':form.areaBuscarPersona, "lista_areas" :lista_areas,
                            "total_areas": total_areas
                            })
                            return responseEstudiante
                    else:
                        print("Es trabajador")
                        
                        
                        users= [usuario[0]]
                        print(users)
                        responseTrabajador= templates.TemplateResponse("general_pages/homepage.html",
                            {'request':request, 'users':users, 'area':form.areaBuscarPersona, "lista_areas" :lista_areas,
                            "total_areas": total_areas
                            })
                        return responseTrabajador
        except HTTPException as e:
            print("Error en Home")
            print (e)
            response = templates.TemplateResponse(
            "general_pages/homepage.html",
             {"request": request,
               "total_areas": total_areas,
                "lista_areas":lista_areas,
                })
            return response

    elif form.is_carntet_x_lotes() :
        print("Estoy en carnets por lotes")
        area = buscarAreas_por_name(buscarAreas(),form.areaBuscarPersona)
        tipo = form.tipoBuscarPersona

        userstemp = buscar_personas_por_areas(area)
        listResult = []
        print("Tipo ", tipo)
        for temp in userstemp:
            tipo_temp = temp['personType']
            if tipo_temp == tipo:
                listResult.append(temp)
            elif tipo_temp == tipo:
                listResult.append(temp)
        
        

        responses_carnet_x_lotes= templates.TemplateResponse("general_pages/homepage.html",
                            {'request':request, 'users':listResult, 'area':form.areaBuscarPersona, "lista_areas" :lista_areas,
                            "total_areas": total_areas
                            })
        return responses_carnet_x_lotes


    else:       
        errorArea= form.errorArea
        errorCI = form.errorCI
        response = templates.TemplateResponse(
                "general_pages/homepage.html",
                {"request": request,
                "total_areas": total_areas,
                "lista_areas":lista_areas,
                "errorArea": errorArea,
                "errorCI": errorCI })
        return response
      
