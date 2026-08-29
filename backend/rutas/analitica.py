"""
Rutas de analítica.

- GET /api/analitica/prediccion -> predicción de gasto del próximo mes
- GET /api/analitica/anomalias  -> gastos anómalos (|Z| > 2)
"""
import traceback

from flask import Blueprint, jsonify, request

from ..core.exceptions import ErrorControlador
from ..services.analitica_service import analitica_servicio
from . import soportar_cors

analitica_bp = Blueprint("analitica", __name__)


@analitica_bp.route("/prediccion", methods=["GET", "OPTIONS"])
@soportar_cors
def prediccion():
    try:
        usuario_id = request.args.get("usuario_id")
        if not usuario_id:
            raise ErrorControlador("usuario_id es obligatorio.")
        resultado = analitica_servicio.prediccion(usuario_id)
        return jsonify({"ok": True, "datos": resultado}), 200
    except ErrorControlador as exc:
        return jsonify({"ok": False, "error": exc.mensaje}), exc.codigo
    except Exception as exc:  # noqa: BLE001
        print("ERROR EN ANALITICA:", traceback.format_exc())
        return jsonify({"ok": False, "error": f"Error interno: {str(exc)}"}), 500


@analitica_bp.route("/anomalias", methods=["GET", "OPTIONS"])
@soportar_cors
def anomalias():
    try:
        usuario_id = request.args.get("usuario_id")
        if not usuario_id:
            raise ErrorControlador("usuario_id es obligatorio.")
        resultado = analitica_servicio.anomalias(usuario_id)
        return jsonify({"ok": True, "datos": resultado}), 200
    except ErrorControlador as exc:
        return jsonify({"ok": False, "error": exc.mensaje}), exc.codigo
    except Exception as exc:  # noqa: BLE001
        print("ERROR EN ANALITICA:", traceback.format_exc())
        return jsonify({"ok": False, "error": f"Error interno: {str(exc)}"}), 500
