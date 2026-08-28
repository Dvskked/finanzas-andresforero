"""Rutas de autenticación y usuarios."""

import logging
import re

import bcrypt
from flask import Blueprint, jsonify, request

from ..modelos import repositorio as repo
from ..modelos.database import ErrorBaseDeDatos, RegistroDuplicado, json_ready
from .helpers import (
    ErrorControlador,
    id_entero,
    json_body,
    respuesta_error,
    respuesta_ok,
    texto_requerido,
)

logger = logging.getLogger("finanzas")

auth_bp = Blueprint("auth", __name__, url_prefix="/api")


def _validar_correo(correo):
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo):
        raise ErrorControlador("El campo 'correo' no tiene un formato válido.")
    return correo.strip().lower()


def _validar_contrasena(password):
    if len(password or "") < 6:
        raise ErrorControlador("La contraseña debe tener al menos 6 caracteres.")
    return password


def _datos_publicos(usuario):
    """Devuelve solo los campos públicos del usuario (formato JSON requerido)."""
    return {
        "id_usuario": usuario["id_usuario"],
        "nombre": usuario["nombre"],
        "correo": usuario["correo"],
    }


def _error_bd(exc):
    """Traduce excepciones inesperadas de base de datos a una respuesta JSON."""
    logger.error("Error de base de datos en /api/usuarios: %s", exc)
    return jsonify({
        "ok": False,
        "error": "Error interno al acceder a la base de datos. Intente nuevamente.",
    }), 500


@auth_bp.post("/usuarios")
def registrar_usuario():
    """Registro básico de usuario (RF01)."""
    data = json_body()
    nombre = texto_requerido(data, "nombre", max_len=100)
    correo = _validar_correo(texto_requerido(data, "correo", max_len=190))
    contrasena = _validar_contrasena(data.get("contrasena"))

    try:
        hash_contrasena = bcrypt.hashpw(
            contrasena.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        usuario = repo.crear_usuario(nombre, correo, hash_contrasena)
    except RegistroDuplicado as exc:
        return jsonify({"ok": False, "error": str(exc)}), 409
    except ErrorBaseDeDatos as exc:
        return _error_bd(exc)
    except Exception as exc:  # noqa: BLE001
        logger.error("Error inesperado en registro de usuario: %s", exc)
        return jsonify({
            "ok": False,
            "error": "Error interno del servidor. Intente nuevamente.",
        }), 500

    return jsonify({
        "ok": True,
        "datos": _datos_publicos(json_ready([usuario])[0]),
    }), 201


@auth_bp.post("/usuarios/login")
def iniciar_sesion():
    """Inicio de sesión: devuelve los datos públicos del usuario."""
    data = json_body()
    correo = _validar_correo(texto_requerido(data, "correo"))
    contrasena = data.get("contrasena") or ""

    try:
        usuario = repo.obtener_usuario_por_correo(correo)
        contrasena_valida = usuario is not None and bcrypt.checkpw(
            contrasena.encode("utf-8"),
            usuario["contrasena_hash"].encode("utf-8"),
        )
    except ErrorBaseDeDatos as exc:
        return _error_bd(exc)
    except Exception as exc:  # noqa: BLE001
        logger.error("Error inesperado en inicio de sesión: %s", exc)
        return jsonify({
            "ok": False,
            "error": "Error interno del servidor. Intente nuevamente.",
        }), 500

    if not contrasena_valida:
        return jsonify({"ok": False, "error": "Correo o contraseña incorrectos."}), 401

    return jsonify({
        "ok": True,
        "datos": _datos_publicos(json_ready([usuario])[0]),
    }), 200


@auth_bp.get("/usuarios")
def obtener_usuarios():
    """Lista usuarios registrados (útil para el selector de demo)."""
    try:
        usuarios = repo.listar_usuarios()
    except ErrorBaseDeDatos as exc:
        return _error_bd(exc)
    except Exception as exc:  # noqa: BLE001
        logger.error("Error inesperado al listar usuarios: %s", exc)
        return jsonify({"ok": False, "error": "Error interno del servidor."}), 500
    return respuesta_ok(json_ready(usuarios))


@auth_bp.get("/usuarios/<int:id_usuario>")
def obtener_usuario(id_usuario):
    try:
        usuario = repo.obtener_usuario_por_id(id_usuario)
    except ErrorBaseDeDatos as exc:
        return _error_bd(exc)
    except Exception as exc:  # noqa: BLE001
        logger.error("Error inesperado al obtener usuario: %s", exc)
        return jsonify({"ok": False, "error": "Error interno del servidor."}), 500
    if not usuario:
        return respuesta_error("Usuario no encontrado.", 404)
    return respuesta_ok(json_ready([usuario])[0])