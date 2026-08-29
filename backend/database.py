"""
Capa de acceso a datos (patrón del repo de referencia).

- `conexion()` crea una conexión MySQL con mysql.connector desde Config.
- `get_cursor()` es un context manager que garantiza cierre de cursor y
  conexión (try/except/finally) con commit automático si todo va bien y
  rollback si ocurre una excepción.
- Los errores de capa de datos se elevan como ErrorBaseDeDatos para que las
  rutas los conviertan en JSON; nunca se renderiza HTML.
"""
import logging
from contextlib import contextmanager
from typing import Generator, Optional

import mysql.connector
from mysql.connector import Error as MySQLConnectorError

from .core.config import Config
from .core.exceptions import ErrorBaseDeDatos

logger = logging.getLogger(__name__)


def conexion(custom_config: Optional[dict] = None) -> mysql.connector.MySQLConnection:
    """Crea y devuelve una nueva conexión MySQL."""
    config = custom_config or Config.get_db_config()
    try:
        return mysql.connector.connect(
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
            database=config["database"],
            charset=config.get("charset", "utf8mb4"),
            use_pure=True,
            connect_timeout=10,
            autocommit=False,
        )
    except MySQLConnectorError as err:
        logger.error("Error al conectar con MySQL: %s", err)
        raise ErrorBaseDeDatos("No fue posible conectar con la base de datos.") from err


@contextmanager
def get_cursor(conn=None) -> Generator[mysql.connector.cursor.MySQLCursorDict, None, None]:
    """
    Context manager seguro para transacciones y cursores (dict).

    - Si no se pasa conexión, crea una propia y la cierra al final.
    - Hace commit automático si no hay errores y rollback si los hay.
    - Siempre cierra el cursor y la conexión (finally).
    """
    es_propia = conn is None
    _conn = conn or conexion()
    cursor = _conn.cursor(dictionary=True, buffered=True)
    try:
        yield cursor
        _conn.commit()
    except ErrorBaseDeDatos:
        _conn.rollback()
        raise
    except MySQLConnectorError as err:
        _conn.rollback()
        logger.error("Error de base de datos durante transacción: %s", err)
        raise ErrorBaseDeDatos() from err
    except Exception:
        _conn.rollback()
        raise
    finally:
        cursor.close()
        if es_propia and _conn.is_connected():
            _conn.close()
