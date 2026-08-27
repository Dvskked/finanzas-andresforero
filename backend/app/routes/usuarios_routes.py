from fastapi import APIRouter, Depends, Path, status

from app.core.dependencies import get_usuario_service
from app.core.exceptions import EntityNotFoundException
from app.schemas.usuario import UsuarioCreate, UsuarioLogin, UsuarioResponse
from app.services.usuario_service import UsuarioService

router = APIRouter(
    prefix="/api/usuarios",
    tags=["Usuarios"]
)


@router.post(
    "",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
    description="Crea un nuevo usuario con contraseña cifrada mediante bcrypt. No expone hashes en la respuesta."
)
def registrar_usuario(
    payload: UsuarioCreate,
    service: UsuarioService = Depends(get_usuario_service)
) -> UsuarioResponse:
    """
    Endpoint para el registro básico de usuarios (RF01).
    """
    return service.registrar_usuario(payload)


@router.post(
    "/login",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión con correo y contraseña",
    description=(
        "Autentica un usuario verificando su contraseña (bcrypt) contra el hash "
        "almacenado. Devuelve el perfil público; nunca expone credenciales."
    )
)
def iniciar_sesion(
    payload: UsuarioLogin,
    service: UsuarioService = Depends(get_usuario_service)
) -> UsuarioResponse:
    """
    Endpoint de autenticación de usuarios (RF02).
    """
    return service.autenticar(payload)


@router.get(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener un usuario por su ID",
    description="Consulta el perfil público de un usuario por su identificador, sin exponer credenciales."
)
def obtener_usuario(
    usuario_id: int = Path(..., gt=0, description="Identificador del usuario"),
    service: UsuarioService = Depends(get_usuario_service)
) -> UsuarioResponse:
    """
    Endpoint para consultar un usuario por ID (utilizado para revalidar sesión).
    """
    usuario = service.obtener_por_id(usuario_id)
    if not usuario:
        raise EntityNotFoundException(f"El usuario con ID {usuario_id} no existe.")
    return usuario
