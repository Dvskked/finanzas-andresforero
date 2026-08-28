"""
Rutas de categorías.

- GET  /api/categorias       -> lista todas las categorías
- POST /api/categorias       -> crea una categoría nueva (tipo ingreso|gasto)
"""
from flask import Blueprint, request

from ..conexion import ejecutar_consulta, ultimo_id
from . import json_error, json_exito, soportar_cors

categorias_bp = Blueprint("categorias", __name__)


@categorias_bp.route("/", methods=["GET", "OPTIONS"])
@categorias_bp.route("", methods=["GET", "OPTIONS"])
@soportar_cors
def listar_categorias():
    """Devuelve todas las categorías ordenadas por nombre."""
    if request.method == "OPTIONS":
        return _respuesta_preflight()

    filtro = (request.args.get("tipo") or "").strip().lower()
    try:
        if filtro in ("ingreso", "gasto"):
            filas = ejecutar_consulta(
                "SELECT id, nombre, tipo, descripcion, color "
                "FROM categorias WHERE tipo = %s ORDER BY nombre ASC",
                (filtro,),
                fetch=True,
            )
        else:
            filas = ejecutar_consulta(
                "SELECT id, nombre, tipo, descripcion, color "
                "FROM categorias ORDER BY nombre ASC",
                fetch=True,
            )
        return json_exito(filas)
    except Exception as exc:  # noqa: BLE001
        return json_error(f"Error al listar categorías: {exc}", 500)


@categorias_bp.route("/", methods=["POST", "OPTIONS"])
@categorias_bp.route("", methods=["POST", "OPTIONS"])
@soportar_cors
def crear_categoria():
    """Crea una categoría nueva."""
    if request.method == "OPTIONS":
        return _respuesta_preflight()

    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    tipo = (datos.get("tipo") or "").strip().lower()
    descripcion = (datos.get("descripcion") or "").strip()
    color = (datos.get("color") or "").strip()

    if not nombre:
        return json_error("El nombre de la categoría es obligatorio", 400)
    if tipo not in ("ingreso", "gasto"):
        return json_error("El tipo debe ser 'ingreso' o 'gasto'", 400)

    try:
        nuevo_id = ultimo_id(
            "INSERT INTO categorias (nombre, tipo, descripcion, color) "
            "VALUES (%s, %s, %s, %s)",
            (nombre, tipo, descripcion or None, color or None),
        )
        return json_exito(
            {
                "id": nuevo_id,
                "nombre": nombre,
                "tipo": tipo,
                "descripcion": descripcion,
                "color": color,
            },
            201,
        )
    except Exception as exc:  # noqa: BLE001
        return json_error(f"Error al crear la categoría: {exc}", 500)


def _respuesta_preflight():
    """Devuelve una respuesta vacía de éxito para las peticiones OPTIONS."""
    from flask import jsonify

    resp = jsonify({"ok": True})
    resp.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return resp, 200
