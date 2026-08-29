"""
Repositorio de usuarios.
"""
from ..database import get_cursor
from ..core.exceptions import RegistroDuplicado


class UsuarioRepositorio:
    """Operaciones SQL sobre la tabla `usuarios`."""

    def buscar_por_correo(self, correo):
        with get_cursor() as cur:
            cur.execute(
                "SELECT id, nombre, email, contrasena_hash "
                "FROM usuarios WHERE email = %s",
                (correo,),
            )
            return cur.fetchone()

    def buscar_por_id(self, usuario_id):
        with get_cursor() as cur:
            cur.execute(
                "SELECT id, nombre, email FROM usuarios WHERE id = %s",
                (usuario_id,),
            )
            return cur.fetchone()

    def crear(self, nombre, email, contrasena_hash):
        with get_cursor() as cur:
            try:
                cur.execute(
                    "INSERT INTO usuarios (nombre, email, contrasena_hash) "
                    "VALUES (%s, %s, %s)",
                    (nombre, email, contrasena_hash),
                )
            except Exception as exc:  # noqa: BLE001
                if "duplicate" in str(exc).lower() or "1062" in str(exc):
                    raise RegistroDuplicado("El correo ya está registrado.") from exc
                raise
            return cur.lastrowid


usuario_repositorio = UsuarioRepositorio()
