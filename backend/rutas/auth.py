"""
Rutas de autenticación.

- POST /api/usuarios       -> registra un usuario (contraseña con bcrypt hash)
- POST /api/usuarios/login -> inicia sesión y devuelve los datos del usuario

Las contraseñas nunca se almacenan en claro; se usa bcrypt. El decorador
`soportar_cors` responde automáticamente a las peticiones preflight OPTIONS.

Cualquier excepción (conexión, SQL, etc.) se captura y se devuelve como JSON
limpio (nunca HTML) para que el frontend no colapse.
"""
import re

import bcrypt
from flask import Blueprint, jsonify, request

from ..conexion import obtener_conexion
from . import soportar_cors

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

    try:
        datos = request.get_json(silent=True)
        if not datos:
            return jsonify(
                {"ok": False, "error": "El cuerpo de la petición debe ser JSON válido"}
            ), 400

        nombre = (datos.get("nombre") or "").strip()
        email = (datos.get("email") or "").strip().lower()
        contrasena = datos.get("contrasena") or datos.get("password") or ""

        if not nombre or not email or not contrasena:
            return jsonify({"ok": False, "error": "Todos los campos son obligatorios"}), 400

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"ok": False, "error": "El formato del email no es válido"}), 400

        if len(contrasena) < 4:
            return jsonify(
                {"ok": False, "error": "La contrasena debe tener al menos 4 caracteres"}
            ), 400

        # 1. Verificar si el correo ya existe en la base de datos
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id FROM usuarios WHERE email = %s", (email,)
            )
            if cursor.fetchone():
                return jsonify(
                    {"ok": False, "error": "El correo ya se encuentra registrado"}
                ), 400

            # 2. Encriptar la contraseña con bcrypt
            hash_pw = _hash_password(contrasena)

            # 3. Insertar el nuevo usuario
            cursor.execute(
                "INSERT INTO usuarios (nombre, email, contrasena_hash) "
                "VALUES (%s, %s, %s)",
                (nombre, email, hash_pw),
            )
            conexion.commit()
            nuevo_id = cursor.lastrowid
        finally:
            cursor.close()
            conexion.close()

        # 4. Respuesta JSON con la información del usuario registrado
        res = jsonify(
            {
                "ok": True,
                "datos": {
                    "id": nuevo_id,
                    "nombre": nombre,
                    "email": email,
                    "mensaje": "Usuario creado con éxito",
                },
            }
        )
        res.status_code = 201
        res.headers.add("Content-Type", "application/json")
        return res
    except Exception as exc:  # noqa: BLE001
        # Retorna la descripción exacta de la falla de Python/MySQL en JSON
        # para que el frontend no colapse.
        return jsonify({"ok": False, "error": f"Falla en el servidor: {str(exc)}"}), 500


@auth_bp.route("/usuarios/login", methods=["POST", "OPTIONS"])
@soportar_cors
def iniciar_sesion():
    """Inicia sesión devolviendo la info del usuario si email/clave son válidos."""
    if request.method == "OPTIONS":
        return _respuesta_preflight()

    try:
        datos = request.get_json(silent=True)
        if not datos:
            return jsonify({"ok": False, "error": "No se recibieron datos JSON"}), 400

        email = (datos.get("email") or "").strip().lower()
        contrasena = datos.get("contrasena") or datos.get("password") or ""

        if not email or not contrasena:
            return jsonify({"ok": False, "error": "email y contrasena son obligatorios"}), 400

        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id, nombre, email, contrasena_hash FROM usuarios WHERE email = %s",
                (email,),
            )
            usuario = cursor.fetchone()
        finally:
            cursor.close()
            conexion.close()

        if not usuario or not _verificar_password(contrasena, usuario["contrasena_hash"]):
            return jsonify({"ok": False, "error": "Credenciales inválidas"}), 401

        return jsonify(
            {
                "ok": True,
                "datos": {
                    "id": usuario["id"],
                    "nombre": usuario["nombre"],
                    "email": usuario["email"],
                },
            }
        ), 200
    except Exception as exc:  # noqa: BLE001
        return jsonify({"ok": False, "error": f"Error en backend: {str(exc)}"}), 500


def _respuesta_preflight():
    """Devuelve una respuesta vacía de éxito para las peticiones OPTIONS."""
    resp = jsonify({"ok": True})
    resp.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return resp, 200
