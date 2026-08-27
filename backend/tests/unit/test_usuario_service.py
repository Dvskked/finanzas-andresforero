import pytest
from app.core.exceptions import AuthenticationException, DuplicateEntityException
from app.core.security import verify_password
from app.schemas.usuario import UsuarioCreate, UsuarioLogin
from app.services.usuario_service import UsuarioService


def test_service_crear_usuario_exitoso(usuario_service: UsuarioService, fake_usuario_repo):
    data = UsuarioCreate(
        nombre="Carlos Ruiz",
        correo="carlos@example.com",
        contrasena="Password123*"
    )
    res = usuario_service.registrar_usuario(data)

    assert res.id_usuario > 0
    assert res.nombre == "Carlos Ruiz"
    assert res.correo == "carlos@example.com"
    assert not hasattr(res, "contrasena")
    assert not hasattr(res, "contrasena_hash")

    # Verificar que en el repositorio el hash guardado sea válido con bcrypt
    guardado = fake_usuario_repo.get_by_id(res.id_usuario)
    assert guardado is not None
    assert guardado["contrasena_hash"] != "Password123*"
    assert verify_password("Password123*", guardado["contrasena_hash"]) is True


def test_service_crear_usuario_correo_duplicado(usuario_service: UsuarioService):
    data = UsuarioCreate(
        nombre="Usuario Repetido",
        correo="test@example.com",  # Ya existe en el fake repo
        contrasena="Password123*"
    )
    with pytest.raises(DuplicateEntityException) as exc_info:
        usuario_service.registrar_usuario(data)

    assert "ya se encuentra registrado" in str(exc_info.value.message)


def test_service_autenticar_exitoso(usuario_service: UsuarioService, fake_usuario_repo):
    """Autenticar un usuario con credenciales correctas devuelve su perfil."""
    data = UsuarioCreate(
        nombre="Lina Gómez",
        correo="lina@example.com",
        contrasena="ClaveSegura123*",
    )
    creado = usuario_service.registrar_usuario(data)

    login = UsuarioLogin(correo="lina@example.com", contrasena="ClaveSegura123*")
    res = usuario_service.autenticar(login)

    assert res.id_usuario == creado.id_usuario
    assert res.nombre == "Lina Gómez"
    assert res.correo == "lina@example.com"
    assert not hasattr(res, "contrasena")
    assert not hasattr(res, "contrasena_hash")


def test_service_autenticar_password_incorrecta(usuario_service: UsuarioService):
    """Autenticar con contraseña incorrecta lanza AuthenticationException (401)."""
    usuario_service.registrar_usuario(
        UsuarioCreate(nombre="Lina Gómez", correo="lina2@example.com", contrasena="ClaveSegura123*")
    )

    login = UsuarioLogin(correo="lina2@example.com", contrasena="ContrasenaErrada9*")
    with pytest.raises(AuthenticationException) as exc_info:
        usuario_service.autenticar(login)

    assert exc_info.value.status_code == 401


def test_service_autenticar_correo_inexistente(usuario_service: UsuarioService):
    """Autenticar con un correo no registrado lanza AuthenticationException (401)."""
    login = UsuarioLogin(correo="nadie@example.com", contrasena="CualquierClave1*")
    with pytest.raises(AuthenticationException):
        usuario_service.autenticar(login)
