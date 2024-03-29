
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
from db.repository.carnet_activo import lista_solicitados
from db.repository.carnet_activo import lista_hechos
from db.repository.person import list_persons
from db.repository.tipo_motivos import list_motivos
from sqlalchemy.orm import Session
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


templates = Jinja2Templates(directory="templates")

# from api.endpoints.web.user import router as userRouter


router = APIRouter()

@router.get("/carnets/hechos")
async def carnet_hechos(request: Request, db: Session = Depends(get_db)):
    print("estoy en carnet Hechos")
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        
        carnets = lista_hechos(db=db)
        
        persons = list_persons(db=db)
        
        motivos = list_motivos(db=db)
        
        paginate_by = 10
        paginator = Paginator(carnets, 10) # 6 employees per page

        try:
            page_obj = paginator.page(paginate_by)
        except PageNotAnInteger:
            # if page is not an integer, deliver the first page
            page_obj = paginator.page(1)
        except EmptyPage:
            # if the page is out of range, deliver the last page
            page_obj = paginator.page(paginator.num_pages)
        
        response = templates.TemplateResponse(
            "general_pages/carnets/carnets_hechos.html", {"request": request, "carnets": carnets, "persons": persons, "motivos":motivos, "page_obj":page_obj}
        )
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
        print("Error carnet hecho")
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
