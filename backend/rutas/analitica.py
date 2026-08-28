"""
Rutas de analítica.

- GET /api/analitica/prediccion -> predicción de gasto del próximo mes
- GET /api/analitica/anomalias  -> gastos anómalos por categoría (|Z| > umbral)

Ambas delegan en los módulos de `backend/analitica/`.
"""
from flask import Blueprint, request

from ..analitica.anomalias import detectar_anomalias
from ..analitica.predictor import predecir_proximo_mes
from . import json_error, json_exito, soportar_cors

analitica_bp = Blueprint("analitica", __name__)


@analitica_bp.route("/prediccion", methods=["GET", "OPTIONS"])
@soportar_cors
def prediccion():
    """Devuelve la predicción de gasto del próximo mes."""
    if request.method == "OPTIONS":
        return _respuesta_preflight()

    usuario_id = request.args.get("usuario_id")
    if not usuario_id:
        return json_error("usuario_id es obligatorio", 400)

    try:
        resultado = predecir_proximo_mes(usuario_id)
        return json_exito(resultado)
    except Exception as exc:  # noqa: BLE001
        return json_error(f"Error al calcular la predicción: {exc}", 500)


@analitica_bp.route("/anomalias", methods=["GET", "OPTIONS"])
@soportar_cors
def anomalias():
    """Devuelve los gastos anómalos por categoría (|Z| > umbral)."""
    if request.method == "OPTIONS":
        return _respuesta_preflight()

    usuario_id = request.args.get("usuario_id")
    if not usuario_id:
        return json_error("usuario_id es obligatorio", 400)

    try:
        resultado = detectar_anomalias(usuario_id)
        return json_exito(resultado)
    except Exception as exc:  # noqa: BLE001
        return json_error(f"Error al detectar anomalías: {exc}", 500)


def _respuesta_preflight():
    """Devuelve una respuesta vacía de éxito para las peticiones OPTIONS."""
    from flask import jsonify

    resp = jsonify({"ok": True})
    resp.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return resp, 200
