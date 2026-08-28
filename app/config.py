"""
Configuración central de la aplicación.

Todas las variables de entorno se cargan de forma centralizada aquí para que
el resto del código no dependa directamente de ``os.environ``. Esto facilita
las pruebas, la documentación y el despliegue (Render / Clever Cloud).
"""

import os
from functools import lru_cache

from dotenv import load_dotenv


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@lru_cache
def load_settings() -> dict:
    # Carga las variables del archivo .env (no hace falta que exista en producción).
    load_dotenv()

    return {
        # --- Servidor ---
        "HOST": os.getenv("HOST", "0.0.0.0"),
        # Render inyecta la variable PORT automáticamente; de forma local usamos 8000.
        "PORT": int(os.getenv("PORT", "8000")),
        "DEBUG": _as_bool(os.getenv("DEBUG"), default=False),

        # --- Base de datos (Clever Cloud MySQL) ---
        "DB_HOST": os.getenv("DB_HOST", "localhost"),
        "DB_PORT": int(os.getenv("DB_PORT", "3306")),
        "DB_USER": os.getenv("DB_USER", "root"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD", ""),
        "DB_NAME": os.getenv("DB_NAME", "finanzas_personales"),

        # --- Orígenes permitidos (CORS) ---
        "CORS_ORIGINS": os.getenv(
            "CORS_ORIGINS", "*"
        ).split(","),
    }
