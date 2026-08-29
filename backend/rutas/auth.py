"""
Rutas de autenticación y registro de usuarios.

- POST /api/usuarios       -> registro (bcrypt hash)
- POST /api/usuarios/login -> inicio de sesión

Patrón del repo de referencia: proceso del JSON entrante, validación y
respuesta SIEMPRE con jsonify() en JSON estructurado. Ninguna excepción debe
renderizar HTML.
"""
import traceback

from flask import Blueprint, jsonify, request

from ..core.exceptions import ErrorControlador
from ..services.usuario_service import usuario_servicio
from . import soportar_cors

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/usuarios", methods=["POST", "OPTIONS"])
@soportar_cors
def registrar_usuario():
    """Crea un nuevo usuario con contraseña cifrada con bcrypt."""
    try:
        datos = request.get_json(force=True, silent=True) or {}
        resultado = usuario_servicio.registrar(datos)
        return jsonify({"ok": True, "datos": resultado}), 201
    except ErrorControlador as exc:
        return jsonify({"ok": False, "error": exc.mensaje}), exc.codigo
    except Exception as exc:  # noqa: BLE001
        print("ERROR EN REGISTRO:", traceback.format_exc())
        return jsonify({"ok": False, "error": f"Error interno: {str(exc)}"}), 500


@auth_bp.route("/usuarios/login", methods=["POST", "OPTIONS"])
@soportar_cors
def iniciar_sesion():
    """Valida credenciales y devuelve los datos públicos del usuario."""
    try:
        datos = request.get_json(force=True, silent=True) or {}
        resultado = usuario_servicio.autenticar(datos)
        return jsonify({"ok": True, "datos": resultado}), 200
    except ErrorControlador as exc:
        return jsonify({"ok": False, "error": exc.mensaje}), exc.codigo
    except Exception as exc:  # noqa: BLE001
        print("ERROR EN LOGIN:", traceback.format_exc())
        return jsonify({"ok": False, "error": f"Error interno: {str(exc)}"}), 500
