"""
Rutas de categorías.

- GET  /api/categorias       -> listar (filtro opcional por tipo)
- POST /api/categorias       -> crear categoria (ingreso|gasto)
"""
import traceback

from flask import Blueprint, jsonify, request

from ..core.exceptions import ErrorControlador
from ..services.categoria_service import categoria_servicio
from . import soportar_cors

categorias_bp = Blueprint("categorias", __name__)


@categorias_bp.route("", methods=["GET", "OPTIONS"])
@categorias_bp.route("/", methods=["GET", "OPTIONS"])
@soportar_cors
def listar_categorias():
    try:
        tipo = (request.args.get("tipo") or "").strip().lower()
        resultado = categoria_servicio.listar(tipo)
        return jsonify({"ok": True, "datos": resultado}), 200
    except ErrorControlador as exc:
        return jsonify({"ok": False, "error": exc.mensaje}), exc.codigo
    except Exception as exc:  # noqa: BLE001
        print("ERROR EN CATEGORIAS:", traceback.format_exc())
        return jsonify({"ok": False, "error": f"Error interno: {str(exc)}"}), 500


@categorias_bp.route("", methods=["POST", "OPTIONS"])
@categorias_bp.route("/", methods=["POST", "OPTIONS"])
@soportar_cors
def crear_categoria():
    try:
        datos = request.get_json(force=True, silent=True) or {}
        resultado = categoria_servicio.crear(datos)
        return jsonify({"ok": True, "datos": resultado}), 201
    except ErrorControlador as exc:
        return jsonify({"ok": False, "error": exc.mensaje}), exc.codigo
    except Exception as exc:  # noqa: BLE001
        print("ERROR EN CATEGORIAS:", traceback.format_exc())
        return jsonify({"ok": False, "error": f"Error interno: {str(exc)}"}), 500
