"""
Rutas de autenticación.

- POST /api/usuarios       -> registra un usuario (contraseña con bcrypt hash)
- POST /api/usuarios/login -> inicia sesión y devuelve los datos del usuario

Toda excepción (conexión, SQL, etc.) se captura con traceback y se devuelve
como JSON limpio, NUNCA como HTML. Los recursos (cursor, conexión) se cierran
en un bloque finally.
"""
import re
import traceback

import bcrypt
from flask import Blueprint, jsonify, request

from ..bd import obtener_conexion
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


@auth_bp.route("/usuarios", methods=["POST"])
@soportar_cors
def registrar_usuario():
    """Registra un nuevo usuario en la tabla `usuarios`."""
    conexion = None
    cursor = None
    try:
        datos = request.get_json(force=True, silent=True)
        if not datos:
            return jsonify({"ok": False, "error": "No se recibieron datos JSON válidos"}), 400

        nombre = datos.get("nombre")
        email = datos.get("email")
        contrasena = datos.get("contrasena") or datos.get("password")

        if not nombre or not email or not contrasena:
            return jsonify(
                {"ok": False, "error": "Todos los campos (nombre, email, contraseña) son obligatorios"}
            ), 400

        if not re.match(r"[^@]+@[^@]+\.[^@]+", str(email)):
            return jsonify({"ok": False, "error": "El formato del email no es válido"}), 400

        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Verificar duplicados
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"ok": False, "error": "El correo ya está registrado"}), 400

        # Encriptar clave
        hashed_pw = _hash_password(contrasena)

        # Insertar
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, contrasena_hash) VALUES (%s, %s, %s)",
            (nombre, email, hashed_pw),
        )
        conexion.commit()
        nuevo_id = cursor.lastrowid

        return jsonify(
            {
                "ok": True,
                "datos": {
                    "id": nuevo_id,
                    "nombre": nombre,
                    "email": email,
                    "mensaje": "Usuario creado correctamente",
                },
            }
        ), 201

    except Exception as exc:  # noqa: BLE001
        print("ERROR EN REGISTRO:", traceback.format_exc())
        return jsonify({"ok": False, "error": f"Error interno: {str(exc)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


@auth_bp.route("/usuarios/login", methods=["POST"])
@soportar_cors
def iniciar_sesion():
    """Inicia sesión devolviendo la info del usuario si email/clave son válidos."""
    conexion = None
    cursor = None
    try:
        datos = request.get_json(force=True, silent=True)
        if not datos:
            return jsonify({"ok": False, "error": "No se recibieron datos JSON válidos"}), 400

        email = (datos.get("email") or "").strip().lower()
        contrasena = datos.get("contrasena") or datos.get("password") or ""

        if not email or not contrasena:
            return jsonify(
                {"ok": False, "error": "email y contraseña son obligatorios"}
            ), 400

        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, nombre, email, contrasena_hash FROM usuarios WHERE email = %s",
            (email,),
        )
        usuario = cursor.fetchone()

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
        print("ERROR EN LOGIN:", traceback.format_exc())
        return jsonify({"ok": False, "error": f"Error interno: {str(exc)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()
