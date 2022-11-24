
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
from db.repository.person import list_persons
from db.repository.tipo_motivos import list_motivos
from sqlalchemy.orm import Session

templates = Jinja2Templates(directory="templates")

# from api.endpoints.web.user import router as userRouter


router = APIRouter()

@router.get("/carnets/solicitados")
async def carnet_solicitado(request: Request, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        print(token)
        print(scheme)
        carnets = lista_solicitados(db=db)
        persons = list_persons(db=db)
        motivos = list_motivos(db=db)
        response = templates.TemplateResponse(
            "general_pages/carnets/carnets_pendientes.html", {"request": request, "carnets": carnets, "persons": persons, "motivos":motivos}
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
