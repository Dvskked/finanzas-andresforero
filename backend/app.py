"""
Fábrica de la aplicación Flask.

- Configura CORS global para /api/* (cualquier origen).
- Suspende los archivos estáticos del frontend desde la raíz.
- Maneja TODOS los errores (404, 405, HTTPException, Exception) en JSON.
- Inicializa la base de datos (schema + seed) al arrancar sin bloquear la app.
"""
import logging
import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from .core.config import load_env_file
from .core.exceptions import ErrorControlador, manejar_error_controlado
from .rutas.auth import auth_bp
from .rutas.categorias import categorias_bp
from .rutas.movimientos import movimientos_bp
from .rutas.analitica import analitica_bp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("finanzas")

PROYECTO_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROYECTO_DIR / "frontend"


def _inicializar_bd():
    """Ejecuta schema.sql y seed.sql de forma idempotente (sin bloquear)."""
    from .database import get_cursor

    schema = PROYECTO_DIR / "database" / "schema.sql"
    seed = PROYECTO_DIR / "database" / "seed.sql"

    def ejecutar_script(ruta):
        if not ruta.is_file():
            return
        contenido = ruta.read_text(encoding="utf-8")
        sentencias = [s.strip() for s in contenido.split(";") if s.strip()]
        with get_cursor() as cur:
            for s in sentencias:
                if s and not s.upper().startswith("--"):
                    cur.execute(s)

    try:
        ejecutar_script(schema)
        if seed.is_file():
            ejecutar_script(seed)
        logger.info("Base de datos inicializada correctamente.")
    except Exception as exc:  # noqa: BLE001
        logger.error("No se pudo inicializar la base de datos: %s", exc)


def crear_app():
    load_env_file()

    app = Flask(
        __name__,
        static_folder=str(FRONTEND_DIR),
        static_url_path="/",
    )

    # CORS global: cualquier origen para /api/* + preflight automático.
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Content-Type"],
    )

    # Blueprints de la API.
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(categorias_bp, url_prefix="/api/categorias")
    app.register_blueprint(movimientos_bp, url_prefix="/api")
    app.register_blueprint(analitica_bp, url_prefix="/api/analitica")

    # ---- Frontend estático (prioridad: /api/* se resuelve antes que estáticos) ----
    @app.route("/")
    def index():
        return send_from_directory(str(FRONTEND_DIR), "index.html")

    @app.route("/<path:ruta>")
    def estaticos(ruta):
        if ruta.startswith("api/"):
            return jsonify({"ok": False, "error": "Ruta no encontrada."}), 404
        ruta_archivo = FRONTEND_DIR / ruta
        if ruta_archivo.is_file():
            return send_from_directory(str(FRONTEND_DIR), ruta)
        return send_from_directory(str(FRONTEND_DIR), "index.html")

    # ---- Manejo de errores: SIEMPRE JSON ----
    @app.errorhandler(ErrorControlador)
    def _error_controlado(exc):
        return manejar_error_controlado(exc)

    @app.errorhandler(404)
    def _no_encontrado(exc):
        if request.path.startswith("/api/"):
            return jsonify({"ok": False, "error": "Ruta no encontrada."}), 404
        return send_from_directory(str(FRONTEND_DIR), "index.html"), 404

    @app.errorhandler(405)
    def _metodo_no_permitido(exc):
        return jsonify({"ok": False, "error": "Método no permitido para esta ruta."}), 405

    @app.errorhandler(500)
    def _error_interno(exc):
        logger.exception("Error interno del servidor")
        return jsonify({"ok": False, "error": "Error interno del servidor."}), 500

    @app.errorhandler(Exception)
    def _excepcion_general(exc):
        logger.exception("Excepción no controlada")
        return jsonify({"ok": False, "error": f"Error interno: {str(exc)}"}), 500

    # Inicialización de base de datos al arrancar.
    _inicializar_bd()

    return app


app = crear_app()
