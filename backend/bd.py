"""
Módulo de conexión a la base de datos.

Proporciona una función simple `obtener_conexion()` que usa mysql.connector
con manejo estricto de excepciones y reconexión frente a cierres de conexión
(timeouts de Clever Cloud). Lee las credenciales de variables de entorno con
fallbacks a las credenciales de producción.
"""
import os

import mysql.connector
from mysql.connector import Error as MySQLError
from mysql.connector.pooling import MySQLConnectionPool

_HOST = os.getenv("DB_HOST", "bal4ecgxmnkkhixeiuz-mysql.services.clever-cloud.com")
_NAME = os.getenv("DB_NAME", "bal4ecgxmnkkhixeiuz")
_USER = os.getenv("DB_USER", "uumrqajbsuaq5pj1")
_PASS = os.getenv("DB_PASSWORD", "jnCrtAO54uKSqdlkHxN5")
_PORT = int(os.getenv("DB_PORT", "3306"))

_pool = None
_pool_creado = False


def _crear_config():
    """Construye la configuración de conexión a la base de datos."""
    return {
        "host": _HOST,
        "database": _NAME,
        "user": _USER,
        "password": _PASS,
        "port": _PORT,
        "autocommit": False,
        "use_pure": True,
        "connect_timeout": 10,
    }


def _get_pool():
    """Crea el pool de conexiones una sola vez."""
    global _pool, _pool_creado
    if not _pool_creado:
        config = _crear_config()
        config.update(
            {
                "pool_name": "finanzas_bd_pool",
                "pool_size": 5,
                "pool_reset_session": True,
            }
        )
        _pool = MySQLConnectionPool(**config)
        _pool_creado = True
    return _pool


def obtener_conexion():
    """
    Devuelve una conexión a MySQL.

    Usa un pool y, si la conexión obtenida está caída, intenta reconectarse de
    forma transparente ante timeouts o cierres por parte del servidor.

    Raises
    ------
    mysql.connector.Error
        Si no se puede establecer/reconectar la conexión.
    """
    try:
        pool = _get_pool()
        conexion = pool.get_connection()
    except MySQLError:
        # Si el pool no pudo crearse (ej. BD caída al primer intento),
        # reintentamos crearlo limpiamente y abrimos una conexión directa.
        reset_pool()
        pool = _get_pool()
        conexion = pool.get_connection()

    if not conexion.is_connected():
        conexion.reconnect(attempts=3, delay=2)
    return conexion


def reset_pool():
    """Borra el pool actual para forzar su recreación en el siguiente uso."""
    global _pool, _pool_creado
    _pool = None
    _pool_creado = False
