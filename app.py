"""Punto de entrada de la aplicación (raíz del proyecto).

Tanto para ejecución local como para el despliegue en Render:

    python app.py        # desarrollo (http://localhost:8000)
    gunicorn app:app     # producción (Render) — Render usará este archivo

Este archivo reutiliza la fábrica y el arranque definidos en
``backend/app.py``, por lo que toda la lógica de la API vive en ese paquete
(rutas, modelos y análisis). Si se ejecuta ``python app.py``, el import de
``backend.app`` ya deja la base de datos inicializada (esquema + datos demo).
"""

import logging
import sys
from pathlib import Path

# Permite importar el paquete ``backend`` y ``conexion`` desde la raíz
# esté donde esté el directorio de trabajo (útil en Render y en local).
_RAIZ = str(Path(__file__).resolve().parent)
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from werkzeug.serving import run_simple  # noqa: E402

# ``app`` es la instancia de Flask que espera gunicorn con ``app:app``.
# Al importar ``backend.app`` se ejecuta ``inicializar_datos()`` (esquema y
# datos de demostración vía ``SEED_DEMO``).
from backend.app import app as app  # noqa: E402, F401
from backend.config import config  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("finanzas")

if __name__ == "__main__":
    logger.info("Motor de base de datos: %s", config.db_type)
    run_simple(
        "0.0.0.0",
        config.port,
        app,
        use_reloader=config.debug,
        use_debugger=config.debug,
    )