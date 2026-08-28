"""
Manejador del pool de conexiones MySQL con reconexión automática.

Usa mysql-connector-python. Si una conexión se pierde (por timeout de Clever
Cloud o cierre del servidor), genera una conexión nueva de forma transparente.
También provee una utilidad que ejecuta scripts SQL (schema/seed) de forma
idempotente apoyándose en cláusulas IF NOT EXISTS e inserciones protegidas.
"""
import mysql.connector
from mysql.connector import pooling

from .config import Config

_pool = None


def _get_pool():
    """Crea (una sola vez) el pool de conexiones a la base de datos."""
    global _pool
    if _pool is None:
        config = {
            "host": Config.DB_HOST,
            "database": Config.DB_NAME,
            "user": Config.DB_USER,
            "password": Config.DB_PASSWORD,
            "port": Config.DB_PORT,
            "pool_name": "finanzas_pool",
            "pool_size": Config.POOL_SIZE,
            "pool_reset_session": True,
            "autocommit": False,
            "use_pure": True,
            "connect_timeout": 10,
        }
        _pool = pooling.MySQLConnectionPool(**config)
    return _pool


def obtener_conexion():
    """
    Devuelve una conexión fresca desde el pool.

    Si la conexión obtenida está caída, intenta reconectarse antes de usarla.
    """
    pool = _get_pool()
    conn = pool.get_connection()
    if not conn.is_connected():
        conn.reconnect()
    return conn


def ejecutar_consulta(sql, params=None, fetch=True):
    """
    Ejecuta una consulta (SELECT) y retorna las filas como lista de tuplas.

    Parameters
    ----------
    sql : str
        Sentencia SQL a ejecutar.
    params : tuple | dict | None
        Parámetros de la consulta (con mysql-connector-python se usa %s).
    fetch : bool
        Si True, retorna todas las filas; si False, retorna None.

    Returns
    -------
    list[tuple] | None
    """
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params or ())
        if fetch:
            return cursor.fetchall()
        return None
    finally:
        cursor.close()
        conn.close()


def ejecutar_escritura(sql, params=None):
    """
    Ejecuta una sentencia de escritura (INSERT/UPDATE/DELETE) y confirma/revierte.

    Returns
    -------
    int
        El número de filas afectadas.
    """
    conn = obtener_conexion()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params or ())
        conn.commit()
        return cursor.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def ultimo_id(sql, params=None):
    """Ejecuta un INSERT y devuelve el último id generado (auto_increment)."""
    conn = obtener_conexion()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params or ())
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def ejecutar_script_sql(ruta_sql):
    """
    Ejecuta el contenido de un archivo .sql sentencia por sentencia.

    Divide el script por ';' de forma sencilla e idempotente; la protección
    IF NOT EXISTS del DDL y las verificaciones del seed evitan duplicados.
    """
    with open(ruta_sql, "r", encoding="utf-8") as fh:
        contenido = fh.read()

    sentencias = [s.strip() for s in contenido.split(";") if s.strip()]

    conn = obtener_conexion()
    cursor = conn.cursor()
    try:
        for sentencia in sentencias:
            if not sentencia or sentencia.upper().startswith("--"):
                continue
            cursor.execute(sentencia)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def inicializar_bd():
    """
    Inicializa la base de datos: crea tablas (schema) y carga datos iniciales
    (seed) si aún no existen. Se invoca al arrancar la aplicación.
    """
    import os

    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Subimos un nivel para llegar a database/ (raíz del proyecto)
    proyecto_dir = os.path.dirname(base_dir)

    ruta_schema = os.path.join(proyecto_dir, "database", "schema.sql")
    ruta_seed = os.path.join(proyecto_dir, "database", "seed.sql")

    def _existe(ruta):
        return os.path.isfile(ruta)

    if _existe(ruta_schema):
        ejecutar_script_sql(ruta_schema)
    if _existe(ruta_seed):
        ejecutar_script_sql(ruta_seed)
