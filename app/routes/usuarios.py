"""
Rutas de usuarios: registro y listado.
"""

from fastapi import APIRouter, HTTPException

import bcrypt

from ..database import get_connection
from ..schemas import UsuarioCreate, UsuarioOut

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])


@router.post("", response_model=dict, status_code=201)
def crear_usuario(u: UsuarioCreate):
    """Registra un nuevo usuario almacenando la contraseña con hash bcrypt."""
    contrasena_hash = bcrypt.hashpw(
        u.contrasena.encode("utf-8"), bcrypt.gensalt(rounds=12)
    ).decode("utf-8")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nombre, correo, contrasena_hash) VALUES (%s, %s, %s)",
            (u.nombre, u.correo, contrasena_hash),
        )
        conn.commit()
        return {
            "id_usuario": cursor.lastrowid,
            "mensaje": "Usuario creado exitosamente",
        }
    except Exception as exc:
        conn.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"No se pudo crear el usuario: {getattr(exc, 'msg', str(exc))}",
        )
    finally:
        cursor.close()
        conn.close()


@router.get("", response_model=list[UsuarioOut])
def listar_usuarios():
    """Lista todos los usuarios (útil para depuración)."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_usuario, nombre, correo, "
            "DATE_FORMAT(fecha_registro, '%%Y-%%m-%%d %%H:%%i:%%s') AS fecha_registro "
            "FROM usuarios ORDER BY id_usuario"
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
