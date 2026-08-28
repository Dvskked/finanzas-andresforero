"""
Rutas de movimientos (ingresos y gastos) y resumen financiero.

- GET    /api/movimientos            -> lista movimientos (con filtro opcional)
- POST   /api/movimientos            -> crea un movimiento
- GET    /api/movimientos/<id>       -> detalle de un movimiento
- PUT    /api/movimientos/<id>       -> actualiza un movimiento
- DELETE /api/movimientos/<id>       -> elimina un movimiento
- GET    /api/resumen                -> totales de ingresos/gastos/balance
"""
from flask import Blueprint, request

from ..conexion import ejecutar_consulta, ejecutar_escritura, ultimo_id
from . import json_error, json_exito, soportar_cors

movimientos_bp = Blueprint("movimientos", __name__)


def _validar_movimiento(datos, es_update=False):
    """Valida y normaliza los campos de un movimiento."""
    usuario_id = datos.get("usuario_id")
    categoria_id = datos.get("categoria_id")
    tipo = (datos.get("tipo") or "").strip().lower()
    monto = datos.get("monto")
    fecha = datos.get("fecha")
    descripcion = (datos.get("descripcion") or "").strip()

    if not es_update:
        if not usuario_id:
            return None, "usuario_id es obligatorio"
        if not categoria_id:
            return None, "categoria_id es obligatorio"

    if monto is None:
        return None, "monto es obligatorio"
    try:
        monto = round(float(monto), 2)
    except (ValueError, TypeError):
        return None, "monto debe ser un número válido"
    if monto <= 0:
        return None, "monto debe ser mayor que cero"

    if tipo not in ("ingreso", "gasto"):
        return None, "tipo debe ser 'ingreso' o 'gasto'"

    return {
        "usuario_id": usuario_id,
        "categoria_id": categoria_id,
        "tipo": tipo,
        "monto": monto,
        "fecha": fecha or None,
        "descripcion": descripcion,
    }, None


def _serializar(fila):
    """Convierte una fila (dict de cursor) a un dict JSON limpio."""
    if not fila:
        return None
    return {
        "id": fila.get("id"),
        "usuario_id": fila.get("usuario_id"),
        "categoria_id": fila.get("categoria_id"),
        "categoria_nombre": fila.get("categoria_nombre"),
        "tipo": fila.get("tipo"),
        "monto": float(fila.get("monto") or 0),
        "fecha": fila.get("fecha"),
        "descripcion": fila.get("descripcion"),
        "creado_en": fila.get("creado_en"),
    }


@movimientos_bp.route("/movimientos", methods=["GET", "OPTIONS"])
@soportar_cors
def listar_movimientos():
    """Lista los movimientos; filtra por usuario_id y/o tipo si se envían."""
    if request.method == "OPTIONS":
        return _respuesta_preflight()

    usuario_id = request.args.get("usuario_id")
    tipo = (request.args.get("tipo") or "").strip().lower()

    condiciones = []
    parametros = []
    if usuario_id:
        condiciones.append("m.usuario_id = %s")
        parametros.append(usuario_id)
    if tipo in ("ingreso", "gasto"):
        condiciones.append("m.tipo = %s")
        parametros.append(tipo)

    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""

    sql = (
        "SELECT m.id, m.usuario_id, m.categoria_id, c.nombre AS categoria_nombre, "
        "m.tipo, m.monto, m.fecha, m.descripcion, m.creado_en "
        "FROM ingresos_gastos m "
        "LEFT JOIN categorias c ON c.id = m.categoria_id "
        f"{where} ORDER BY m.fecha DESC, m.id DESC"
    )
    try:
        filas = ejecutar_consulta(sql, parametros, fetch=True)
        return json_exito([_serializar(f) for f in filas])
    except Exception as exc:  # noqa: BLE001
        return json_error(f"Error al listar movimientos: {exc}", 500)


@movimientos_bp.route("/movimientos", methods=["POST", "OPTIONS"])
@soportar_cors
def crear_movimiento():
    """Crea un nuevo movimiento (ingreso o gasto)."""
    if request.method == "OPTIONS":
        return _respuesta_preflight()

    datos = request.get_json(silent=True) or {}
    limpio, error = _validar_movimiento(datos)
    if error:
        return json_error(error, 400)

    try:
        # Verificar que la categoría existe
        cat = ejecutar_consulta(
            "SELECT id FROM categorias WHERE id = %s",
            (limpio["categoria_id"],),
            fetch=True,
        )
        if not cat:
            return json_error("La categoría indicada no existe", 400)

        nuevo_id = ultimo_id(
            "INSERT INTO ingresos_gastos "
            "(usuario_id, categoria_id, tipo, monto, fecha, descripcion) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (
                limpio["usuario_id"],
                limpio["categoria_id"],
                limpio["tipo"],
                limpio["monto"],
                limpio["fecha"],
                limpio["descripcion"] or None,
            ),
        )
        return json_exito({"id": nuevo_id, **limpio}, 201)
    except Exception as exc:  # noqa: BLE001
        return json_error(f"Error al crear el movimiento: {exc}", 500)


@movimientos_bp.route("/movimientos/<int:mov_id>", methods=["GET", "OPTIONS"])
@soportar_cors
def detalle_movimiento(mov_id):
    """Devuelve el detalle de un movimiento específico."""
    if request.method == "OPTIONS":
        return _respuesta_preflight()

    try:
        filas = ejecutar_consulta(
            "SELECT m.id, m.usuario_id, m.categoria_id, c.nombre AS categoria_nombre, "
            "m.tipo, m.monto, m.fecha, m.descripcion, m.creado_en "
            "FROM ingresos_gastos m "
            "LEFT JOIN categorias c ON c.id = m.categoria_id "
            "WHERE m.id = %s",
            (mov_id,),
            fetch=True,
        )
        if not filas:
            return json_error("Movimiento no encontrado", 404)
        return json_exito(_serializar(filas[0]))
    except Exception as exc:  # noqa: BLE001
        return json_error(f"Error al obtener el movimiento: {exc}", 500)


@movimientos_bp.route("/movimientos/<int:mov_id>", methods=["PUT", "OPTIONS"])
@soportar_cors
def actualizar_movimiento(mov_id):
    """Actualiza los campos de un movimiento existente."""
    if request.method == "OPTIONS":
        return _respuesta_preflight()

    datos = request.get_json(silent=True) or {}
    limpio, error = _validar_movimiento(datos, es_update=True)
    if error:
        return json_error(error, 400)

    # Permitir actualizar campos parciales: solo modificamos los presentes
    campos = []
    parametros = []
    mapeo = {
        "usuario_id": "usuario_id",
        "categoria_id": "categoria_id",
        "tipo": "tipo",
        "monto": "monto",
        "fecha": "fecha",
        "descripcion": "descripcion",
    }
    for clave, columna in mapeo.items():
        if clave in datos and datos[clave] is not None:
            campos.append(f"{columna} = %s")
            parametros.append(limpio[clave])

    if not campos:
        return json_error("No hay campos válidos para actualizar", 400)

    parametros.append(mov_id)
    sql = f"UPDATE ingresos_gastos SET {', '.join(campos)} WHERE id = %s"

    try:
        afectadas = ejecutar_escritura(sql, parametros)
        if afectadas == 0:
            filas = ejecutar_consulta(
                "SELECT id FROM ingresos_gastos WHERE id = %s", (mov_id,), fetch=True
            )
            if not filas:
                return json_error("Movimiento no encontrado", 404)
        return json_exito({"id": mov_id, **limpio})
    except Exception as exc:  # noqa: BLE001
        return json_error(f"Error al actualizar el movimiento: {exc}", 500)


@movimientos_bp.route("/movimientos/<int:mov_id>", methods=["DELETE", "OPTIONS"])
@soportar_cors
def eliminar_movimiento(mov_id):
    """Elimina un movimiento existente."""
    if request.method == "OPTIONS":
        return _respuesta_preflight()

    try:
        afectadas = ejecutar_escritura(
            "DELETE FROM ingresos_gastos WHERE id = %s", (mov_id,)
        )
        if afectadas == 0:
            return json_error("Movimiento no encontrado", 404)
        return json_exito({"id": mov_id, "eliminado": True})
    except Exception as exc:  # noqa: BLE001
        return json_error(f"Error al eliminar el movimiento: {exc}", 500)


@movimientos_bp.route("/resumen", methods=["GET", "OPTIONS"])
@soportar_cors
def resumen_financiero():
    """Devuelve totales de ingresos, gastos y balance global."""
    if request.method == "OPTIONS":
        return _respuesta_preflight()

    usuario_id = request.args.get("usuario_id")

    cond = ""
    params = []
    if usuario_id:
        cond = "WHERE usuario_id = %s"
        params.append(usuario_id)

    try:
        totales = ejecutar_consulta(
            "SELECT tipo, COALESCE(SUM(monto), 0) AS total "
            f"FROM ingresos_gastos {cond} GROUP BY tipo",
            params,
            fetch=True,
        )
        ingreso = 0.0
        gasto = 0.0
        for fila in totales:
            if fila["tipo"] == "ingreso":
                ingreso = float(fila["total"] or 0)
            elif fila["tipo"] == "gasto":
                gasto = float(fila["total"] or 0)

        balance = round(ingreso - gasto, 2)
        return json_exito({
            "ingresos": round(ingreso, 2),
            "gastos": round(gasto, 2),
            "balance": balance,
        })
    except Exception as exc:  # noqa: BLE001
        return json_error(f"Error al calcular el resumen: {exc}", 500)


def _respuesta_preflight():
    """Devuelve una respuesta vacía de éxito para las peticiones OPTIONS."""
    from flask import jsonify

    resp = jsonify({"ok": True})
    resp.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return resp, 200
