"""
Configuración central de la aplicación.

Carga variables de entorno con fallbacks a las credenciales de producción de
Clever Cloud MySQL. Utilizable desde el backend y desde la entrada gunicorn.
"""
import os


def load_env_file(path=".env"):
    """Carga variables desde un archivo .env si existe (sin sobreescribir)."""
    if not os.path.isfile(path):
        return
    with open(path, "r", encoding="utf-8") as fh:
        for linea in fh:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, _, valor = linea.partition("=")
            os.environ.setdefault(clave.strip(), valor.strip().strip("\"'"))


class Config:
    """Credenciales y parámetros centrales."""

    # --- Base de datos Clever Cloud (fallbacks de producción) ---
    DB_HOST = os.getenv("DB_HOST", "bal4ecgxmnkkhixeiuz-mysql.services.clever-cloud.com")
    DB_NAME = os.getenv("DB_NAME", "bal4ecgxmnkkhixeiuz")
    DB_USER = os.getenv("DB_USER", "uumrqajbsuaq5pj1")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "jnCrtAO54uKSqdlkHxN5")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))

    # --- Servidor ---
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "false").lower() in ("1", "true", "yes")

    @staticmethod
    def get_db_config():
        """Devuelve el dict de configuración de conexión MySQL."""
        return {
            "host": Config.DB_HOST,
            "port": Config.DB_PORT,
            "user": Config.DB_USER,
            "password": Config.DB_PASSWORD,
            "database": Config.DB_NAME,
            "charset": "utf8mb4",
        }
