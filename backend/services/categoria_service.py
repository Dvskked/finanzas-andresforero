"""
Servicio de categorías.
"""
from ..core.exceptions import ErrorControlador
from ..repositories.categoria_repository import categoria_repositorio


class CategoriaServicio:
    """Reglas de negocio sobre categorías."""

    def listar(self, tipo=None):
        if tipo and tipo not in ("ingreso", "gasto"):
            raise ErrorControlador("El tipo debe ser 'ingreso' o 'gasto'.")
        return categoria_repositorio.listar(tipo if tipo in ("ingreso", "gasto") else None)

    def crear(self, datos):
        nombre = (datos.get("nombre") or "").strip()
        tipo = (datos.get("tipo") or "").strip().lower()
        descripcion = (datos.get("descripcion") or "").strip()
        color = (datos.get("color") or "").strip()

        if not nombre:
            raise ErrorControlador("El nombre de la categoría es obligatorio.")
        if tipo not in ("ingreso", "gasto"):
            raise ErrorControlador("El tipo debe ser 'ingreso' o 'gasto'.")

        nuevo_id = categoria_repositorio.crear(
            nombre, tipo, descripcion or None, color or None
        )
        return {
            "id": nuevo_id,
            "nombre": nombre,
            "tipo": tipo,
            "descripcion": descripcion,
            "color": color,
        }


categoria_servicio = CategoriaServicio()
