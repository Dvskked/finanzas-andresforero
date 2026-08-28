"""
Punto de entrada de la API REST de Finanzas Personales.

Levanta la aplicación FastAPI, configura CORS, crea automáticamente las tablas
de la base de datos (si no existen) y sirve el frontend estático junto con la
API. Esto permite desplegar sin problema en un único Web Service de Render.
"""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import load_settings
from .database import get_connection
from .routes import analitica, categorias, movimientos, resumen, usuarios

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("finanzas")

# Ruta del frontend (raíz del repositorio -> frontend/)
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

SCHEMA_SQL = Path(__file__).resolve().parents[1] / "database" / "schema.sql"


def _ejecutar_script_sql(conn, script: Path) -> None:
    """Ejecuta un archivo .sql (se ignoran comentarios y otras bases)."""
    with open(script, "r", encoding="utf-8") as fh:
        sql = fh.read()
    cursor = conn.cursor()
    for statement in sql.split(";"):
        stmt = statement.strip()
        if not stmt or stmt.startswith("--") or stmt.upper().startswith("CREATE DATABASE"):
            continue
        try:
            cursor.execute(stmt)
        except Exception as exc:
            # Se ignoran errores benignos (tabla ya existe, etc.)
            logger.info("SQL ignorado: %s", exc)
    cursor.close()
    conn.commit()


def _init_database() -> None:
    """Crea el esquema y, si está vacía, carga datos de prueba."""
    conn = get_connection()
    try:
        _ejecutar_script_sql(conn, SCHEMA_SQL)

        # Si no hay usuarios, cargamos el seed para que el dashboard no esté vacío.
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        hay_datos = cursor.fetchone()[0] > 0
        cursor.close()

        if not hay_datos:
            seed = Path(__file__).resolve().parents[1] / "database" / "seed.sql"
            if seed.exists():
                _ejecutar_script_sql(conn, seed)
                logger.info("Datos de prueba cargados.")
    finally:
        conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Inicializando base de datos...")
    _init_database()
    logger.info("Base de datos lista.")
    yield


app = FastAPI(
    title="API Finanzas Personales",
    description=(
        "API REST para registrar ingresos y gastos, calcular resúmenes y obtener "
        "análisis predictivo (regresión lineal) y detección de anomalías."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

settings = load_settings()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings["CORS_ORIGINS"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API ---
app.include_router(usuarios.router)
app.include_router(categorias.router)
app.include_router(movimientos.router)
app.include_router(resumen.router)
app.include_router(analitica.router)


# --- Frontend estático ---
@app.get("/", include_in_schema=False)
def servir_index():
    return FileResponse(FRONTEND_DIR / "index.html")


if FRONTEND_DIR.exists():
    app.mount(
        "/static",
        StaticFiles(directory=FRONTEND_DIR),
        name="static",
    )


@app.get("/api/health")
def health_check():
    """Verifica que la API y la base de datos estén operativas."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}


# Para ejecución en Render: uvicorn app.main:app --host 0.0.0.0 --port $PORT
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings["HOST"],
        port=settings["PORT"],
        reload=settings["DEBUG"],
    )
