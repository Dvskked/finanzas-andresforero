"""Rutas de autenticación y usuarios."""

import re

import bcrypt
from flask import Blueprint, request

from ..modelos import repositorio as repo
from ..modelos.database import RegistroDuplicado, json_ready
from .helpers import (
    ErrorControlador,
    id_entero,
    json_body,
    respuesta_error,
    respuesta_ok,
    texto_requerido,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/api")


def _validar_correo(correo):
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo):
        raise ErrorControlador("El campo 'correo' no tiene un formato válido.")
    return correo.strip().lower()


def _validar_contrasena(password):
    if len(password or "") < 6:
        raise ErrorControlador("La contraseña debe tener al menos 6 caracteres.")
    return password


@auth_bp.post("/usuarios")
def registrar_usuario():
    """Registro básico de usuario (RF01)."""
    data = json_body()
    nombre = texto_requerido(data, "nombre", max_len=100)
    correo = _validar_correo(texto_requerido(data, "correo", max_len=190))
    contrasena = _validar_contrasena(data.get("contrasena"))

    hash_contrasena = bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt())
    try:
        usuario = repo.crear_usuario(nombre, correo, hash_contrasena.decode("utf-8"))
    except RegistroDuplicado as exc:
        return respuesta_error(str(exc), 409)

    return json_ready([usuario])[0], 201


@auth_bp.post("/usuarios/login")
def iniciar_sesion():
    """Inicio de sesión: devuelve los datos públicos del usuario."""
    data = json_body()
    correo = _validar_correo(texto_requerido(data, "correo"))
    contrasena = data.get("contrasena") or ""

    usuario = repo.obtener_usuario_por_correo(correo)
    if not usuario or not bcrypt.checkpw(
        contrasena.encode("utf-8"), usuario["contrasena_hash"].encode("utf-8")
    ):
        return respuesta_error("Correo o contraseña incorrectos.", 401)

    return json_ready([{
        "id_usuario": usuario["id_usuario"],
        "nombre": usuario["nombre"],
        "correo": usuario["correo"],
        "fecha_registro": usuario["fecha_registro"],
    }])[0]


@auth_bp.get("/usuarios")
def obtener_usuarios():
    """Lista usuarios registrados (útil para el selector de demo)."""
    return json_ready(repo.listar_usuarios())


@auth_bp.get("/usuarios/<int:id_usuario>")
def obtener_usuario(id_usuario):
    usuario = repo.obtener_usuario_por_id(id_usuario)
    if not usuario:
        return respuesta_error("Usuario no encontrado.", 404)
    return usuario