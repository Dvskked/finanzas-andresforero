"""
Configuración de la aplicación.

Carga las variables de entorno para la base de datos de Clever Cloud MySQL.
Si una variable no está definida en el entorno, usa un fallback predeterminado
con las credenciales de producción de Clever Cloud.
"""
import os


class Config:
    """Configuración central de la aplicación."""

    # Credenciales de base de datos (Clever Cloud MySQL)
    DB_HOST = os.getenv("DB_HOST", "bal4ecgxmnkkhixeiuz-mysql.services.clever-cloud.com")
    DB_NAME = os.getenv("DB_NAME", "bal4ecgxmnkkhixeiuz")
    DB_USER = os.getenv("DB_USER", "uumrqajbsuaq5pj1")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "jnCrtAO54uKSqdlkHxN5")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))

    # Puerto del servidor web (Render inyecta la variable PORT)
    PORT = int(os.getenv("PORT", "8000"))

    # Origen permitido para CORS (puede ajustarse con CORS_ORIGINS)
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000,http://localhost:5000"
    ).split(",")

    # Tamaño del pool de conexiones
    POOL_SIZE = int(os.getenv("POOL_SIZE", "5"))

    # Umbral Z-Score para detección de anomalías
    Z_THRESHOLD = float(os.getenv("Z_THRESHOLD", "2"))

    @staticmethod
    def database_url():
        """Devuelve una URL de conexión legible para MySQL (no usada por el driver)."""
        return (
            f"mysql://{Config.DB_USER}:{Config.DB_PASSWORD}"
            f"@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
        )


def load_env_file(path=".env"):
    """
    Carga variables desde un archivo .env si existe (compatible con dotenv).

    Evita depender de python-dotenv en tiempo de despliegue, ya que no es
    estrictamente necesario; se incluye en requirements.txt por conveniencia.
    """
    if not os.path.isfile(path):
        return
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("\"'")
            os.environ.setdefault(key, value)
