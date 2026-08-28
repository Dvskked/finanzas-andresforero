"""
Utilidades compartidas para las rutas.
"""
from functools import wraps

import flask
from flask import jsonify, request


def json_exito(datos=None, status=200):
    """Respuesta de éxito con la estructura {ok, datos}."""
    return jsonify({"ok": True, "datos": datos}), status


def json_error(mensaje, status=400):
    """Respuesta de error con la estructura {ok, error}."""
    return jsonify({"ok": False, "error": mensaje}), status


def soportar_cors(fn):
    """Decorador que responde a las peticiones preflight OPTIONS.

    Los headers CORS los inyecta flask-cors de forma global; aquí solo
    cortamos el OPTIONS con un cuerpo vacío (preflight correcto) para que
    la respuesta no llegue vacía por conflictos de headers duplicados.
    """
    @wraps(fn)
    def _envoltura(*args, **kwargs):
        if request.method == "OPTIONS":
            return flask.Response(status=200)
        return fn(*args, **kwargs)
    return _envoltura
