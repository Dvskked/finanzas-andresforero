"""
Rutas de movimientos (ingresos/gastos).

- GET    /api/movimientos           -> listar (usuario_id, tipo)
- POST   /api/movimientos           -> crear
- GET    /api/movimientos/<id>      -> detalle
- PUT    /api/movimientos/<id>      -> actualizar
- DELETE /api/movimientos/<id>      -> eliminar
- GET    /api/resumen               -> resumen (usuario_id)
"""
import traceback

from flask import Blueprint, jsonify, request

from ..core.exceptions import ErrorControlador
from ..services.movimiento_service import movimiento_servicio
from . import soportar_cors

movimientos_bp = Blueprint("movimientos", __name__)


@movimientos_bp.route("/movimientos", methods=["GET", "OPTIONS"])
@soportar_cors
def listar_movimientos():
    try:
        usuario_id = request.args.get("usuario_id")
        tipo = (request.args.get("tipo") or "").strip().lower()
        if not usuario_id:
            raise ErrorControlador("usuario_id es obligatorio.")
        resultado = movimiento_servicio.listar(usuario_id, tipo)
        return jsonify({"ok": True, "datos": resultado}), 200
    except ErrorControlador as exc:
        return jsonify({"ok": False, "error": exc.mensaje}), exc.codigo
    except Exception as exc:  # noqa: BLE001
        print("ERROR EN MOVIMIENTOS:", traceback.format_exc())
        return jsonify({"ok": False, "error": f"Error interno: {str(exc)}"}), 500


@movimientos_bp.route("/movimientos", methods=["POST", "OPTIONS"])
@soportar_cors
def crear_movimiento():
    try:
        datos = request.get_json(force=True, silent=True) or {}
        resultado = movimiento_servicio.crear(datos)
        return jsonify({"ok": True, "datos": resultado}), 201
    except ErrorControlador as exc:
        return jsonify({"ok": False, "error": exc.mensaje}), exc.codigo
    except Exception as exc:  # noqa: BLE001
        print("ERROR EN MOVIMIENTOS:", traceback.format_exc())
        return jsonify({"ok": False, "error": f"Error interno: {str(exc)}"}), 500


@movimientos_bp.route("/movimientos/<int:mov_id>", methods=["GET", "OPTIONS"])
@soportar_cors
def detalle_movimiento(mov_id):
    try:
        resultado = movimiento_servicio.obtener(mov_id)
        if not resultado:
            raise ErrorControlador("Movimiento no encontrado.", 404)
        return jsonify({"ok": True, "datos": resultado}), 200
    except ErrorControlador as exc:
        return jsonify({"ok": False, "error": exc.mensaje}), exc.codigo
    except Exception as exc:  # noqa: BLE001
        print("ERROR EN MOVIMIENTOS:", traceback.format_exc())
        return jsonify({"ok": False, "error": f"Error interno: {str(exc)}"}), 500


@movimientos_bp.route("/movimientos/<int:mov_id>", methods=["PUT", "OPTIONS"])
@soportar_cors
def actualizar_movimiento(mov_id):
    try:
        datos = request.get_json(force=True, silent=True) or {}
        resultado = movimiento_servicio.actualizar(mov_id, datos)
        return jsonify({"ok": True, "datos": resultado}), 200
    except ErrorControlador as exc:
        return jsonify({"ok": False, "error": exc.mensaje}), exc.codigo
    except Exception as exc:  # noqa: BLE001
        print("ERROR EN MOVIMIENTOS:", traceback.format_exc())
        return jsonify({"ok": False, "error": f"Error interno: {str(exc)}"}), 500


@movimientos_bp.route("/movimientos/<int:mov_id>", methods=["DELETE", "OPTIONS"])
@soportar_cors
def eliminar_movimiento(mov_id):
    try:
        resultado = movimiento_servicio.eliminar(mov_id)
        return jsonify({"ok": True, "datos": resultado}), 200
    except ErrorControlador as exc:
        return jsonify({"ok": False, "error": exc.mensaje}), exc.codigo
    except Exception as exc:  # noqa: BLE001
        print("ERROR EN MOVIMIENTOS:", traceback.format_exc())
        return jsonify({"ok": False, "error": f"Error interno: {str(exc)}"}), 500


@movimientos_bp.route("/resumen", methods=["GET", "OPTIONS"])
@soportar_cors
def resumen():
    try:
        usuario_id = request.args.get("usuario_id")
        if not usuario_id:
            raise ErrorControlador("usuario_id es obligatorio.")
        resultado = movimiento_servicio.resumen(usuario_id)
        return jsonify({"ok": True, "datos": resultado}), 200
    except ErrorControlador as exc:
        return jsonify({"ok": False, "error": exc.mensaje}), exc.codigo
    except Exception as exc:  # noqa: BLE001
        print("ERROR EN RESUMEN:", traceback.format_exc())
        return jsonify({"ok": False, "error": f"Error interno: {str(exc)}"}), 500
