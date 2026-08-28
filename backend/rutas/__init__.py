"""
Utilidades compartidas para las rutas.
"""
from functools import wraps

from flask import jsonify, request


def json_exito(datos=None, status=200):
    """Respuesta de éxito con la estructura {ok, datos}."""
    return jsonify({"ok": True, "datos": datos}), status


def json_error(mensaje, status=400):
    """Respuesta de error con la estructura {ok, error}."""
    return jsonify({"ok": False, "error": mensaje}), status


def soportar_cors(fn):
    """Decorador que responde explícitamente a preflight OPTIONS."""
    @wraps(fn)
    def _envoltura(*args, **kwargs):
        if request.method == "OPTIONS":
            response = jsonify({"ok": True})
            response.headers["Access-Control-Allow-Origin"] = request.headers.get(
                "Origin", "*"
            )
            response.headers["Access-Control-Allow-Methods"] = (
                "GET, POST, PUT, DELETE, OPTIONS"
            )
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization"
            )
            return response, 200
        return fn(*args, **kwargs)
    return _envoltura
