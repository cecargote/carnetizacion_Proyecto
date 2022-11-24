from fastapi import APIRouter
from webapp.admin import router_admin
from webapp.admin.tipo_de_motivos import router_motivos_admin
from webapp.admin.tipo_de_motivos import router_motivos_crear
from webapp.admin.tipo_de_motivos.editar_tipo_motivo import router_edit_tipo_motivo
from webapp.admin.usuarios import router_edit_usuario
from webapp.admin.usuarios import router_form_usuarios
from webapp.admin.usuarios import router_usuarios
from webapp.auth import router_login
from webapp.crear_carnet import router_crear_carnet
from webapp.home import router_home
from webapp.resultado_busqueda import router_resultado_busqueda
from webapp.crear_carnet.carnets import router_carnet_solicitados

api_router = APIRouter()

api_router.include_router(router_home.router, prefix="", tags=["Inicio"])
api_router.include_router(router_login.router, prefix="", tags=["Iniciar Sesión"])
api_router.include_router(router_admin.router, prefix="", tags=["Administración"])
api_router.include_router(
    router_motivos_admin.router, prefix="", tags=["Tipos de Motivos"]
)
api_router.include_router(
    router_motivos_crear.router, prefix="", tags=["Crear Tipos de Motivos"]
)
api_router.include_router(router_crear_carnet.router, prefix="", tags=["Crear Carnet"])
api_router.include_router(
    router_edit_tipo_motivo.router, prefix="", tags=["Editar Carnet"]
)
api_router.include_router(router_usuarios.router, prefix="", tags=["Usuarios"])
api_router.include_router(
    router_form_usuarios.router, prefix="", tags=["Formulario de Usuarios"]
)
api_router.include_router(
    router_resultado_busqueda.router, prefix="", tags=["Resultado de Busqueda"]
)
api_router.include_router(
    router_edit_usuario.router, prefix="", tags=["Editar usuario"]
)
api_router.include_router(
    router_carnet_solicitados.router, prefix="", tags=["Carnets solicitados"]
)