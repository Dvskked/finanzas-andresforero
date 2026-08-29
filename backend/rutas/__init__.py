"""
Rutas de la API. Cada módulo declara su Blueprint.
CORS/preflight lo maneja flask-cors de forma global (backend/app.py); aquí no
se manipulan headers manualmente para evitar conflictos.
"""
from functools import wraps

from flask import request

import flask


def soportar_cors(fn):
    """
    Decorador: responde a preflight OPTIONS con un 200 de cuerpo vacío,
    dejando que flask-cors inyecte los headers CORS correctos.
    """
    @wraps(fn)
    def _envoltura(*args, **kwargs):
        if request.method == "OPTIONS":
            return flask.Response(status=200)
        return fn(*args, **kwargs)
    return _envoltura
