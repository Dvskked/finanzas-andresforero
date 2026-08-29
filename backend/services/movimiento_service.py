"""
Servicio de movimientos y resumen financiero.
"""
import datetime

from ..core.exceptions import ErrorControlador
from ..repositories.categoria_repository import categoria_repositorio
from ..repositories.movimiento_repository import movimiento_repositorio


def _serializar(fila):
    """Convierte una fila (dict) a un dict JSON limpio."""
    if not fila:
        return None
    return {
        "id": fila.get("id"),
        "usuario_id": fila.get("usuario_id"),
        "categoria_id": fila.get("categoria_id"),
        "categoria_nombre": fila.get("categoria_nombre"),
        "tipo": fila.get("tipo"),
        "monto": round(float(fila.get("monto") or 0), 2),
        "fecha": fila.get("fecha"),
        "descripcion": fila.get("descripcion"),
        "creado_en": fila.get("creado_en"),
    }


class MovimientoServicio:
    """Reglas de negocio sobre movimientos (ingresos/gastos)."""

    def listar(self, usuario_id, tipo=None):
        filas = movimiento_repositorio.listar(usuario_id, tipo)
        return [_serializar(f) for f in filas]

    def obtener(self, movimiento_id):
        return _serializar(movimiento_repositorio.obtener(movimiento_id))

    def crear(self, datos):
        usuario_id = datos.get("usuario_id")
        categoria_id = datos.get("categoria_id")
        tipo = (datos.get("tipo") or "").strip().lower()
        monto = datos.get("monto")
        fecha = datos.get("fecha")
        descripcion = (datos.get("descripcion") or "").strip()

        if not usuario_id or not categoria_id:
            raise ErrorControlador("usuario_id y categoria_id son obligatorios.")
        if tipo not in ("ingreso", "gasto"):
            raise ErrorControlador("tipo debe ser 'ingreso' o 'gasto'.")
        try:
            monto = round(float(monto), 2)
        except (TypeError, ValueError):
            raise ErrorControlador("monto debe ser un número válido.") from None
        if monto <= 0:
            raise ErrorControlador("monto debe ser mayor que cero.")

        if not categoria_repositorio.existe(categoria_id):
            raise ErrorControlador("La categoría indicada no existe.")

        if fecha:
            try:
                datetime.date.fromisoformat(str(fecha))
            except ValueError:
                raise ErrorControlador("fecha debe tener formato YYYY-MM-DD.") from None
        else:
            fecha = None

        nuevo_id = movimiento_repositorio.crear(
            usuario_id, categoria_id, tipo, monto, fecha, descripcion or None
        )
        return {
            "id": nuevo_id,
            "usuario_id": usuario_id,
            "categoria_id": categoria_id,
            "tipo": tipo,
            "monto": monto,
            "fecha": fecha,
            "descripcion": descripcion,
        }

    def actualizar(self, movimiento_id, datos):
        fila = movimiento_repositorio.obtener(movimiento_id)
        if not fila:
            raise ErrorControlador("Movimiento no encontrado.", 404)

        campos = {}
        for clave, columna in {
            "usuario_id": "usuario_id",
            "categoria_id": "categoria_id",
            "tipo": "tipo",
            "monto": "monto",
            "fecha": "fecha",
            "descripcion": "descripcion",
        }.items():
            if clave in datos and datos[clave] is not None:
                campos[columna] = datos[clave]

        if "monto" in campos:
            try:
                campos["monto"] = round(float(campos["monto"]), 2)
            except (TypeError, ValueError):
                raise ErrorControlador("monto debe ser un número válido.") from None

        if "tipo" in campos and campos["tipo"] not in ("ingreso", "gasto"):
            raise ErrorControlador("tipo debe ser 'ingreso' o 'gasto'.")

        movimiento_repositorio.actualizar(movimiento_id, campos)
        return _serializar(movimiento_repositorio.obtener(movimiento_id))

    def eliminar(self, movimiento_id):
        afectadas = movimiento_repositorio.eliminar(movimiento_id)
        if afectadas == 0:
            raise ErrorControlador("Movimiento no encontrado.", 404)
        return {"id": movimiento_id, "eliminado": True}

    def resumen(self, usuario_id):
        totales = movimiento_repositorio.totales(usuario_id)
        totales["balance"] = round(totales["ingresos"] - totales["gastos"], 2)
        return totales


movimiento_servicio = MovimientoServicio()
