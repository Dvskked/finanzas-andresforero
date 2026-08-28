"""
Fábrica de aplicación Flask.

Configura CORS (incluido preflight OPTIONS para /api/*), inicializa la base
de datos al arrancar y registra los blueprints de las rutas.
"""
import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from .config import Config, load_env_file
from .conexion import inicializar_bd


def crear_app():
    """Crea y configura la instancia de la aplicación Flask."""
    load_env_file()

    app = Flask(__name__, static_folder="../frontend", static_url_path="/")

    # Habilitar CORS para todos los orígenes configurados y manejar preflight.
    # send_wildcard=False permite reflejar el Origin y autorizar las peticiones.
    CORS(
        app,
        origins=Config.CORS_ORIGINS,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        supports_credentials=True,
    )

    # Registro de blueprints
    from .rutas.auth import auth_bp
    from .rutas.categorias import categorias_bp
    from .rutas.movimientos import movimientos_bp
    from .rutas.analitica import analitica_bp

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(categorias_bp, url_prefix="/api/categorias")
    app.register_blueprint(movimientos_bp, url_prefix="/api")
    app.register_blueprint(analitica_bp, url_prefix="/api/analitica")

    # Manejador global de errores de base de datos / servidor
    @app.errorhandler(Exception)
    def _manejar_excepcion(exc):
        """Captura cualquier excepción no controlada y devuelve JSON 500."""
        app.logger.error("Error no controlado: %s", exc, exc_info=True)
        return jsonify({"ok": False, "error": str(exc)}), 500

    @app.errorhandler(404)
    def _no_encontrado(error):
        # Si piden /api/... que no existe -> JSON; si no, servir index -> 404
        return jsonify({"ok": False, "error": "Recurso no encontrado"}), 404

    # Inicializar base de datos (DDL + seed) al arrancar
    try:
        inicializar_bd()
    except Exception as exc:  # noqa: BLE001
        # No detenemos el arranque; la app intentará reconectarse en cada request
        app.logger.error("No se pudo inicializar la base de datos: %s", exc)

    return app


app = crear_app()
