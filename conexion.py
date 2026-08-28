"""Conexión a la base de datos (MySQL en producción / SQLite local).

Punto único de conexión usado por la capa de datos (backend/modelos).

En Render (producción) se configura con las variables de entorno
``MYSQL_HOST``, ``MYSQL_PORT``, ``MYSQL_USER``, ``MYSQL_PASSWORD`` y
``MYSQL_DATABASE`` (también se acepta ``DATABASE_URL=mysql://...`` a través
de ``backend.config``). Si no hay ninguna, la aplicación usa **SQLite**
(únicamente para desarrollo local).

Ejemplo de uso:

    import conexion
    cnx = conexion.conectar()        # conexión MySQL o SQLite
    cur  = cnx.cursor()
    ...
    cnx.close()
"""

import sqlite3

import mysql.connector

from backend.config import config


def _kwargs_mysql(incluir_base_datos=True):
    """Parámetros de conexión MySQL según la configuración activa."""
    kwargs = dict(
        host=config.mysql_host,
        port=config.mysql_port,
        user=config.mysql_user,
        password=config.mysql_password,
        charset="utf8mb4",
        use_unicode=True,
        connect_timeout=15,
    )
    if incluir_base_datos:
        kwargs["database"] = config.mysql_database
    # Algunos proveedores de MySQL en la nube requieren TLS/SSL.
    if config.mysql_ssl:
        kwargs["ssl_disabled"] = False
        kwargs.setdefault("ssl_ca", "")
    return kwargs


def conectar():
    """Devuelve una conexión activa (MySQL o SQLite) según la configuración."""
    if config.db_type == "mysql":
        return mysql.connector.connect(**_kwargs_mysql(incluir_base_datos=True))

    conn = sqlite3.connect(str(config.sqlite_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def conectar_sin_base_datos():
    """Conexión MySQL sin seleccionar un esquema (para crearlo si no existe)."""
    return mysql.connector.connect(**_kwargs_mysql(incluir_base_datos=False))