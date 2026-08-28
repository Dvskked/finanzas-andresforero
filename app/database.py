"""
Capa de acceso a datos.

Se centraliza la conexión MySQL utilizando un pool para reutilizar conexiones
(nada de abrir/cerrar en cada request, que es caro y poco escalable). La base
de datos se autoconfigura en el arranque de la aplicación (CreateTables).
"""

import logging

import mysql.connector
from mysql.connector import pooling

from .config import load_settings

logger = logging.getLogger(__name__)

_pool: pooling.MySQLConnectionPool | None = None


def init_db_pool() -> pooling.MySQLConnectionPool:
    """Crea (o devuelve) el pool global de conexiones MySQL."""
    global _pool
    if _pool is not None:
        return _pool

    settings = load_settings()
    pool_config = {
        "host": settings["DB_HOST"],
        "port": settings["DB_PORT"],
        "user": settings["DB_USER"],
        "password": settings["DB_PASSWORD"],
        "database": settings["DB_NAME"],
        "pool_name": "finanzas_pool",
        "pool_size": 5,
        "pool_reset_session": True,
        "charset": "utf8mb4",
        "use_unicode": True,
        # Timeouts razonables para entornos serverless / cloud.
        "connect_timeout": 10,
        "autocommit": True,
    }

    try:
        _pool = pooling.MySQLConnectionPool(**pool_config)
    except mysql.connector.Error as exc:
        logger.error("No se pudo crear el pool de conexiones: %s", exc)
        raise

    return _pool


def get_connection():
    """Devuelve una conexión del pool (usar con 'with' / try-finally)."""
    return init_db_pool().get_connection()


def dict_cursor(conn):
    """Crea un cursor que devuelve filas como diccionarios."""
    return conn.cursor(dictionary=True)
