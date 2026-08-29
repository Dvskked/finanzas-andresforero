"""
Repositorio de categorías.
"""
from ..database import get_cursor
from ..core.exceptions import RegistroDuplicado


class CategoriaRepositorio:
    """Operaciones SQL sobre la tabla `categorias`."""

    def listar(self, tipo=None):
        if tipo:
            with get_cursor() as cur:
                cur.execute(
                    "SELECT id, nombre, tipo, descripcion, color "
                    "FROM categorias WHERE tipo = %s ORDER BY nombre ASC",
                    (tipo,),
                )
                return cur.fetchall()
        with get_cursor() as cur:
            cur.execute(
                "SELECT id, nombre, tipo, descripcion, color "
                "FROM categorias ORDER BY nombre ASC"
            )
            return cur.fetchall()

    def crear(self, nombre, tipo, descripcion=None, color=None):
        with get_cursor() as cur:
            try:
                cur.execute(
                    "INSERT INTO categorias (nombre, tipo, descripcion, color) "
                    "VALUES (%s, %s, %s, %s)",
                    (nombre, tipo, descripcion, color),
                )
            except Exception as exc:  # noqa: BLE001
                if "duplicate" in str(exc).lower() or "1062" in str(exc):
                    raise RegistroDuplicado("La categoría ya existe.") from exc
                raise
            return cur.lastrowid

    def existe(self, categoria_id):
        with get_cursor() as cur:
            cur.execute("SELECT id FROM categorias WHERE id = %s", (categoria_id,))
            return cur.fetchone() is not None


categoria_repositorio = CategoriaRepositorio()
