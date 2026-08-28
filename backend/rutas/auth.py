"""
Rutas de autenticación.

- POST /api/usuarios       -> registra un usuario (contraseña con bcrypt hash)
- POST /api/usuarios/login -> inicia sesión y devuelve los datos del usuario

Las contraseñas nunca se almacenan en claro; se usa bcrypt. El decorador
`soportar_cors` responde automáticamente a las peticiones preflight OPTIONS.
"""
import re

import bcrypt
from flask import Blueprint, jsonify, request

from ..conexion import ejecutar_consulta, ultimo_id
from . import json_error, soportar_cors

auth_bp = Blueprint("auth", __name__)


def _hash_password(contrasena):
    """Genera un hash bcrypt seguro de la contraseña."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(contrasena.encode("utf-8"), salt).decode("utf-8")


def _verificar_password(contrasena, hash_guardado):
    """Compara la contraseña en claro con su hash bcrypt."""
    try:
        return bcrypt.checkpw(
            contrasena.encode("utf-8"), hash_guardado.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False


@auth_bp.route("/usuarios", methods=["POST", "OPTIONS"])
@soportar_cors
def registrar_usuario():
    """Registra un nuevo usuario en la tabla `usuarios`."""
    if request.method == "OPTIONS":
        return _respuesta_preflight()

    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    email = (datos.get("email") or "").strip().lower()
    contrasena = datos.get("contrasena") or ""

    if not nombre or not email or not contrasena:
        return json_error("nombre, email y contrasena son obligatorios", 400)

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return json_error("El formato del email no es válido", 400)

    if len(contrasena) < 4:
        return json_error("La contrasena debe tener al menos 4 caracteres", 400)

    try:
        existe = ejecutar_consulta(
            "SELECT id FROM usuarios WHERE email = %s", (email,), fetch=True
        )
        if existe:
            return json_error("Ya existe un usuario con ese email", 400)

        hash_pw = _hash_password(contrasena)
        nuevo_id = ultimo_id(
            "INSERT INTO usuarios (nombre, email, contrasena_hash) "
            "VALUES (%s, %s, %s)",
            (nombre, email, hash_pw),
        )

        return _respuesta_registro_usuario(nuevo_id, nombre, email)
    except Exception as exc:  # noqa: BLE001
        return json_error(f"Error de Base de Datos: {str(exc)}", 500)


def _respuesta_registro_usuario(nuevo_id, nombre, email):
    """Construye la respuesta de registro forzando el header Content-Type."""
    res = jsonify(
        {
            "ok": True,
            "datos": {
                "id": nuevo_id,
                "nombre": nombre,
                "email": email,
                "mensaje": "Usuario registrado exitosamente",
            },
        }
    )
    res.status_code = 200
    # Forzar explícitamente el Content-Type para que el navegador lo acepte.
    res.headers.add("Content-Type", "application/json")
    return res


@auth_bp.route("/usuarios/login", methods=["POST", "OPTIONS"])
@soportar_cors
def iniciar_sesion():
    """Inicia sesión devolviendo la info del usuario si email/clave son válidos."""
    if request.method == "OPTIONS":
        return _respuesta_preflight()

    datos = request.get_json(silent=True) or {}
    email = (datos.get("email") or "").strip().lower()
    contrasena = datos.get("contrasena") or ""

    if not email or not contrasena:
        return json_error("email y contrasena son obligatorios", 400)

    try:
        filas = ejecutar_consulta(
            "SELECT id, nombre, email, contrasena_hash FROM usuarios "
            "WHERE email = %s",
            (email,),
            fetch=True,
        )
        if not filas:
            return json_error("Credenciales inválidas", 401)

        usuario = filas[0]
        if not _verificar_password(contrasena, usuario["contrasena_hash"]):
            return json_error("Credenciales inválidas", 401)

        return json_exito({
            "id": usuario["id"],
            "nombre": usuario["nombre"],
            "email": usuario["email"],
        })
    except Exception as exc:  # noqa: BLE001
        return json_error(f"Error al iniciar sesión: {exc}", 500)


def _respuesta_preflight():
    """Devuelve una respuesta vacía de éxito para las peticiones OPTIONS."""
    from flask import jsonify

    resp = jsonify({"ok": True})
    resp.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return resp, 200
