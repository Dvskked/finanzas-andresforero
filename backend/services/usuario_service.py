"""
Servicio de usuarios: registro y autenticación.
"""
from ..core.security import hash_password, verificar_password
from ..core.exceptions import NoAutorizado, RegistroDuplicado
from ..repositories.usuario_repository import usuario_repositorio


class UsuarioServicio:
    """Reglas de negocio sobre usuarios."""

    def registrar(self, datos):
        nombre = (datos.get("nombre") or "").strip()
        email = (datos.get("email") or datos.get("correo") or "").strip().lower()
        contrasena = datos.get("contrasena") or datos.get("password") or ""

        if not nombre or not email or not contrasena:
            raise RegistroDuplicado(
                "Todos los campos (nombre, email, contraseña) son obligatorios."
            )

        if len(contrasena) < 4:
            raise RegistroDuplicado(
                "La contraseña debe tener al menos 4 caracteres."
            )

        if usuario_repositorio.buscar_por_correo(email):
            raise RegistroDuplicado("El correo ya está registrado.")

        hash_pw = hash_password(contrasena)
        nuevo_id = usuario_repositorio.crear(nombre, email, hash_pw)
        return {"id": nuevo_id, "nombre": nombre, "email": email}

    def autenticar(self, datos):
        email = (datos.get("email") or datos.get("correo") or "").strip().lower()
        contrasena = datos.get("contrasena") or datos.get("password") or ""

        usuario = usuario_repositorio.buscar_por_correo(email) if email else None
        if not usuario or not verificar_password(
            contrasena, usuario["contrasena_hash"]
        ):
            # Mensaje genérico idéntico para correo inexistente o clave mala.
            raise NoAutorizado("Credenciales inválidas.")

        return {
            "id": usuario["id"],
            "nombre": usuario["nombre"],
            "email": usuario["email"],
        }


usuario_servicio = UsuarioServicio()
