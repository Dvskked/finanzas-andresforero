"""
Excepciones controladas y utilidades de respuesta JSON.

Toda respuesta de error viaja como JSON estructurado: {"ok": false, "error": ...}
Nunca se renderiza HTML desde el backend.
"""
from flask import jsonify


class ErrorControlador(Exception):
    """Excepción controlada con mensaje y código HTTP asociado."""

    def __init__(self, mensaje, codigo=400):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo


class ErrorBaseDeDatos(ErrorControlador):
    """Error de capa de datos (conexión/SQL)."""

    def __init__(self, mensaje="Error interno de base de datos."):
        super().__init__(mensaje, 500)


class RegistroDuplicado(ErrorControlador):
    """Intento de insertar un valor único ya existente (p. ej. correo)."""

    def __init__(self, mensaje="El registro ya existe."):
        super().__init__(mensaje, 409)


class NoAutorizado(ErrorControlador):
    """Credenciales inválidas o token ausente/vencido."""

    def __init__(self, mensaje="Credenciales inválidas."):
        super().__init__(mensaje, 401)


def respuesta_exito(datos=None, status=200):
    """Respuesta de éxito: {"ok": true, "datos": ...}."""
    return jsonify({"ok": True, "datos": datos}), status


def respuesta_error(mensaje, status=400):
    """Respuesta de error: {"ok": false, "error": ...}."""
    return jsonify({"ok": False, "error": mensaje}), status


def manejar_error_controlado(error):
    """Handler para ErrorControlador → JSON."""
    return respuesta_error(error.mensaje, error.codigo)
